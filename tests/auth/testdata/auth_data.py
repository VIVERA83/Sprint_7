from uuid import uuid4

from ..settings import settings

test_not_valid_user_data = {
    "email": "Невалидный email",
    "username": "Очень длинное имя, которое не проходит валидацию по длине, и бо краткость сестра таланта",
    "Левое поле": "Не зачем присылать всякую дичь которая не ожидается",
}

expected = [
    {
        "email": ["Not a valid email address."],
        "password": ["Missing data for required field."],
        "username": ["Length must be between 3 and 20."],
        "Левое поле": ["Unknown field."],
    }
]

test_user_name = uuid4().hex[:10]

test_user_data = {
    "email": f"test@{test_user_name}.com",
    "password": f"test_{test_user_name}",
}

admin_user_data = {"email": settings.auth_login, "password": settings.auth_password}
