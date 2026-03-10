from pydantic import BaseModel, Field, field_validator, EmailStr
from pydantic_core import PydanticCustomError

from .books import ReturnedBook


__all__ = [
    "IncomingSeller",
    "ReturnedSeller",
    "ReturnedAllSellers",
    "ReturnedSellerNoBooks",
    "UpdateSeller"
]


# Базовый класс "Продавцы", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    password: str = Field(min_length=8, max_length=32)

    @field_validator("password")  # Валидатор проверяет, что введенный пароль соответствует условиям
    @staticmethod
    def validate_password(val: str):
        if len(val) < 8:
            raise PydanticCustomError("Validation error", "Password must be at least 8 characters long")
        if not any(c.isalpha() for c in val):
            raise PydanticCustomError("Validation error", "Password must contain at least 1 letter")
        if not any(c.isdigit() for c in val):
            raise PydanticCustomError("Validation error", "Password must contain at least 1 digit")

        return val

# Класс для обновления информации о продавце
class UpdateSeller(BaseSeller):
    pass

# Класс, в котором нам не нужна информация о книгах
class ReturnedSellerNoBooks(UpdateSeller):
    id: int

# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):  # {"id": 1, "title": "Clean Code", ....}
    id: int
    books: list[ReturnedBook] = Field(default_factory=list)

# Класс для возврата массива объектов "Продавцы"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSellerNoBooks]
