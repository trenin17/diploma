#pragma once

#include <initializer_list>
#include <string>
#include <string_view>

#include <nlohmann/json.hpp>

#include <userver/components/component_list.hpp>
#include <userver/storages/postgres/cluster.hpp>
#include <userver/storages/postgres/component.hpp>

namespace views::v1::reverse_index {

class ReverseIndexResponse {
 public:
  ReverseIndexResponse(const std::string& employee_id)
      : employee_id(employee_id) {}

  std::string ToJSON() const {
    nlohmann::json j;
    j["employee_id"] = employee_id;
    return j.dump();
  }

  std::string employee_id;
};

class ReverseIndexRequest {
 public:
  std::function<ReverseIndexResponse(const ReverseIndexRequest&)> func;
  userver::storages::postgres::ClusterPtr cluster;
  std::string employee_id;
  std::optional<std::string> name, surname, patronymic, role, email, birthday,
      telegram_id, vk_id, team;
  std::optional<std::vector<std::string>> phones;
};

void ReverseIndexHandler(const ReverseIndexRequest& request);

void ClearTasks();

}  // namespace views::v1::reverse_index