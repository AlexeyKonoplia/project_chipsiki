from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    Table,
    Column,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


# Many-to-many association between products and categories.
product_categories = Table(
    "product_categories",
    Base.metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)

# Many-to-many association between reviews and hashtags.
review_tags = Table(
    "review_tags",
    Base.metadata,
    Column("review_id", ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    products: Mapped[list["Product"]] = relationship(back_populates="owner")
    reviews: Mapped[list["Review"]] = relationship(back_populates="author")


class Category(Base):
    """Two-level taxonomy: top-level sections (parent_id is NULL) contain
    subcategories. Only admins may modify the tree."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=True
    )

    parent: Mapped["Category | None"] = relationship(
        remote_side="Category.id", back_populates="children"
    )
    children: Mapped[list["Category"]] = relationship(
        back_populates="parent", order_by="Category.name"
    )

    products: Mapped[list["Product"]] = relationship(
        secondary=product_categories, back_populates="categories"
    )


class Tag(Base):
    """A user-written hashtag (stored without the leading '#', lowercase)."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    reviews: Mapped[list["Review"]] = relationship(
        secondary=review_tags, back_populates="tags"
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owner: Mapped["User"] = relationship(back_populates="products")

    categories: Mapped[list["Category"]] = relationship(
        secondary=product_categories, back_populates="products"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("product_id", "author_id", name="uq_review_product_author"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..5
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    product: Mapped["Product"] = relationship(back_populates="reviews")

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped["User"] = relationship(back_populates="reviews")

    tags: Mapped[list["Tag"]] = relationship(
        secondary=review_tags, back_populates="reviews"
    )
