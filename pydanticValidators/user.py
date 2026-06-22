from pydantic import BaseModel, EmailStr, Field

# NOTE: add request body validators for APIs
class UserSignupFields(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    user_type: str | None = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@yopmail.com",
                    "password": "Password@123",
                    "user_type": "USER",
                }
            ]
        }
    }

class UserLoginFields(BaseModel):
    email: EmailStr
    password: str = Field(...)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@yopmail.com",
                    "password": "Password@123"
                }
            ]
        }
    }