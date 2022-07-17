from flasgger import swag_from
from flask import Flask
from sqlalchemy.exc import IntegrityError
from src.api.v1.schema.requests_schema import IdSchema
from src.api.v1.schema.users_schema import RoleSchema, UserRole, UserRoleSchema
from src.core.settings import settings
from src.db.models.db_models import Role
from src.helpers.helpers import (
    CustomResponse,
    get_error_dict,
    get_request_body,
    get_request_query,
    get_swagger_path,
    validate_request,
)
from src.services.service_base import service


@validate_request(schema=RoleSchema, data=get_request_body, only=["name"])
@swag_from(get_swagger_path("role/set_role.yaml"))
def set_role():
    """Создать роль"""
    try:
        service.set_data(RoleSchema(exclude=["id"]).load(get_request_body()))
    except IntegrityError as e:
        return CustomResponse(message=get_error_dict(e), status=400)
    return CustomResponse()


@swag_from(get_swagger_path("role/get_roles.yaml"))
def get_roles():
    """Получить список ролей"""
    data = RoleSchema().dump(service.get_data(Role), many=True)
    return CustomResponse(data)


@validate_request(schema=IdSchema, data=get_request_query)
@swag_from(get_swagger_path("role/del_role.yaml"))
def del_role():
    """Удалить роль"""
    if service.delete(get_request_query().get("id"), Role):
        return CustomResponse()
    return CustomResponse(message={"id": "Not Found"}, status=404)


@validate_request(schema=RoleSchema, data=get_request_body)
@swag_from(get_swagger_path("role/update_role.yaml"))
def update_role():
    """Обновить информацию о роле"""
    try:
        role = RoleSchema(only=["id", "name"]).dump(get_request_body())
        if service.update_data(role["id"], Role, role):
            return CustomResponse()
    except IntegrityError as e:
        return CustomResponse(message=get_error_dict(e), status=400)
    return CustomResponse(
        message="Not Found",
        status=404,
    )


@validate_request(
    schema=UserRoleSchema, data=get_request_body, only=["id_user", "id_role"]
)
@swag_from(get_swagger_path("role/assign_role.yaml"))
def assign_role():
    """Назначить пользователю роль"""
    try:
        service.set_data(UserRoleSchema().load(get_request_body()))
    except IntegrityError as e:
        return CustomResponse(message=get_error_dict(e), status=400)
    return CustomResponse()


@validate_request(
    schema=UserRoleSchema, data=get_request_body, only=["id_user", "id_role"]
)
@swag_from(get_swagger_path("role/del_user_role.yaml"))
def del_user_role():
    """Отобрать роль у пользователя"""
    user_role: UserRole = UserRoleSchema(exclude=["id"]).load(get_request_body())
    if data := service.get_data_user_roles(UserRole, user_role):
        service.delete(data.id, UserRole)
        return CustomResponse()
    return CustomResponse(status=400)


@validate_request(
    schema=UserRoleSchema, data=get_request_query, only=["id_user", "id_role"]
)
@swag_from(get_swagger_path("role/check_usr_role.yaml"))
def check_usr_role():
    """Проверки наличия прав у пользователя"""
    user_role: UserRole = UserRoleSchema(exclude=["id"]).load(get_request_body())
    if service.get_data_user_roles(UserRole, user_role):
        return CustomResponse()
    return CustomResponse(status=400, message="Not Found")


def init_role_routes(app: Flask):
    """Пути к api role"""
    app.add_url_rule(
        rule=settings.auth_base_path + "get_roles", view_func=get_roles, methods=["GET"]
    ),
    app.add_url_rule(
        rule=settings.auth_base_path + "set_role", view_func=set_role, methods=["POST"]
    ),
    app.add_url_rule(
        rule=settings.auth_base_path + "update_role",
        view_func=update_role,
        methods=["PUT"],
    )
    app.add_url_rule(
        rule=settings.auth_base_path + "del_role",
        view_func=del_role,
        methods=["DELETE"],
    )
    app.add_url_rule(
        rule=settings.auth_base_path + "assign_role",
        view_func=assign_role,
        methods=["POST"],
    )
    app.add_url_rule(
        rule=settings.auth_base_path + "del_user_role",
        view_func=del_user_role,
        methods=["DELETE"],
    )
    app.add_url_rule(
        rule=settings.auth_base_path + "check_usr_role",
        view_func=check_usr_role,
        methods=["POST"],
    )
