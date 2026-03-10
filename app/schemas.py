from pydantic import BaseModel, ConfigDict
from typing import Optional


class SignUpModel(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    password: str
    is_staff: Optional[bool] = False
    is_active: Optional[bool] = True

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john@email.com",
                "password": "password",
                "is_staff": False,
                "is_active": True
            }
        }
    )


class LoginModel(BaseModel):
    username: str
    password: str


class OrderModel(BaseModel):
    quantity: int
    pizza_size: Optional[str] = "SMALL"

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "quantity": 2,
                "pizza_size": "LARGE"
            }
        }
    )


class ApproveModel(BaseModel):
    order_status: Optional[str] = "PENDING"

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "order_status": "DELIVERED"
            }
        }
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"