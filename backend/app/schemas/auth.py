from pydantic import BaseModel, EmailStr


# What the client sends when registering
class UserRegister(BaseModel):
    email: EmailStr      # EmailStr validates it's a real email format
    username: str
    password: str        # plain password — hash it before storing


# What the client sends when logging in
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# What we send BACK after successful login
class Token(BaseModel):
    access_token: str
    token_type: str      # always "bearer" — it's a standard HTTP auth type


# What we send back when someone asks "who am I?"
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    is_admin: bool

    # This tells Pydantic to read data from SQLAlchemy model attributes,
    # not just plain dictionaries. Without this, converting a User object
    # to this schema would fail.
    class Config:
        from_attributes = True