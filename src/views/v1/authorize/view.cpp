#define V1_AUTHORIZE

#include "view.hpp"

#include <nlohmann/json.hpp>

#include <userver/clients/dns/component.hpp>
#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/logging/log.hpp>
#include <userver/server/handlers/http_handler_base.hpp>
#include <userver/storages/postgres/cluster.hpp>
#include <userver/storages/postgres/component.hpp>
#include <userver/utils/uuid4.hpp>

#include "definitions/all.hpp"

using json = nlohmann::json;

namespace views::v1::authorize {

namespace {

class UserInfo {
 public:
  std::string id, password, role;
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
    // CORS
    request.GetHttpResponse().SetHeader(
        static_cast<std::string>("Access-Control-Allow-Origin"), "*");
    request.GetHttpResponse().SetHeader(
        static_cast<std::string>("Access-Control-Allow-Headers"), "*");

    AuthorizeRequest request_body;
    request_body.ParseRegisteredFields(request.RequestBody());

    auto result = pg_cluster_->Execute(
        userver::storages::postgres::ClusterHostType::kSlave,
        "SELECT id, password, role FROM working_day_" +
            request_body.company_id +
            ".employees "
            "WHERE id = $1",
        request_body.login);

    if (result.IsEmpty()) {
      request.GetHttpResponse().SetStatus(
          userver::server::http::HttpStatus::kNotFound);
      return ErrorMessage{"No such user"}.ToJsonString();
    }

    auto user_info =
        result.AsSingleRow<UserInfo>(userver::storages::postgres::kRowTag);
    if (user_info.password != request_body.password) {
      request.GetHttpResponse().SetStatus(
          userver::server::http::HttpStatus::kNotFound);
      return ErrorMessage{"Wrong password"}.ToJsonString();
    }

    std::vector<std::string> scopes = {"user"};
    if (user_info.role != "user") {
      scopes.push_back(user_info.role);
    }

    auto token = userver::utils::generators::GenerateUuid();
    auto auth_result = pg_cluster_->Execute(
        userver::storages::postgres::ClusterHostType::kMaster,
        "INSERT INTO wd_general.auth_tokens (token, user_id, company_id, "
        "scopes) "
        "VALUES ($1, $2, $3, $4)",
        token, user_info.id, request_body.company_id, scopes);

    AuthorizeResponse response(token, user_info.role);

    return response.ToJsonString();
  }

 private:
  userver::storages::postgres::ClusterPtr pg_cluster_;
};

}  // namespace

void AppendAuthorize(userver::components::ComponentList& component_list) {
  component_list.Append<AuthorizeHandler>();
}

}  // namespace views::v1::authorize