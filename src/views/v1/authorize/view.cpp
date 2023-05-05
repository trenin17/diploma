#include "view.hpp"

#include <nlohmann/json.hpp>

#include <userver/clients/dns/component.hpp>
#include <userver/logging/log.hpp>
#include <userver/server/handlers/http_handler_base.hpp>
#include <userver/storages/postgres/cluster.hpp>
#include <userver/storages/postgres/component.hpp>
#include <userver/utils/uuid4.hpp>

using json = nlohmann::json;

namespace views::v1::authorize {

namespace {

class AuthorizeRequest {
 public:
  AuthorizeRequest(const std::string& body) {
    auto j = json::parse(body);
    login = j["login"];
    password = j["password"];
  }

  std::string login, password;
};

class AuthorizeResponse {
 public:
  std::string ToJSON() const {
    json j;
    j["token"] = token;
    return j.dump();
  }

  std::string token;
};

class UserInfo {
 public:
  std::string id, password;
};

class AuthorizeHandler final
    : public userver::server::handlers::HttpHandlerBase {
 public:
  static constexpr std::string_view kName = "handler-v1-authorize";

  AuthorizeHandler(
      const userver::components::ComponentConfig& config,
      const userver::components::ComponentContext& component_context)
      : HttpHandlerBase(config, component_context),
        pg_cluster_(
            component_context
                .FindComponent<userver::components::Postgres>("key-value")
                .GetCluster()) {}

  std::string HandleRequestThrow(
      const userver::server::http::HttpRequest& request,
      userver::server::request::RequestContext&) const override {
    AuthorizeRequest request_body(request.RequestBody());

    auto result = pg_cluster_->Execute(
        userver::storages::postgres::ClusterHostType::kSlave,
        "SELECT id, password FROM working_day.employees "
        "WHERE id = $1",
        request_body.login);

    if (result.IsEmpty()) {
      request.GetHttpResponse().SetStatus(
          userver::server::http::HttpStatus::kNotFound);
      return "No such user";
    }

    auto user_info =
        result.AsSingleRow<UserInfo>(userver::storages::postgres::kRowTag);
    if (user_info.password != request_body.password) {
      request.GetHttpResponse().SetStatus(
          userver::server::http::HttpStatus::kNotFound);
      return "Wrong password";
    }

    auto token = userver::utils::generators::GenerateUuid();
    auto auth_result = pg_cluster_->Execute(
        userver::storages::postgres::ClusterHostType::kMaster,
        "INSERT INTO working_day.auth_tokens (token, user_id, scopes) "
        "VALUES ($1, $2, ARRAY ['read'])",
        token, user_info.id);

    return token;
  }

 private:
  userver::storages::postgres::ClusterPtr pg_cluster_;
};

}  // namespace

void AppendAuthorize(userver::components::ComponentList& component_list) {
  component_list.Append<AuthorizeHandler>();
}

}  // namespace views::v1::authorize