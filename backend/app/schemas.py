from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------- Auth / Users ----------
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_admin: bool
    created_at: datetime


class AdminUpdate(BaseModel):
    # Partial update: any subset of fields may be provided.
    is_admin: bool | None = None
    username: str | None = Field(default=None, min_length=3, max_length=64)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    is_admin: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class LoginRequest(BaseModel):
    username: str
    password: str


# ---------- Categories ----------
class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Products ----------
class ProductOwner(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    image_url: str | None
    created_at: datetime
    owner: ProductOwner
    categories: list[CategoryOut]
    review_count: int = 0
    average_rating: float | None = None


# ---------- Reviews ----------
class ReviewAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    text: str | None = None
    # Either reference an existing product...
    product_id: int | None = None
    # ...or create a new one inline.
    new_product_name: str | None = None
    new_product_description: str | None = None
    new_product_image_url: str | None = None
    new_product_category_ids: list[int] = []


class ReviewUpdate(BaseModel):
    rating: int = Field(ge=1, le=5)
    text: str | None = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rating: int
    text: str | None
    created_at: datetime
    author: ReviewAuthor
    product_id: int


class ReviewWithProduct(ReviewOut):
    product: ProductOut
