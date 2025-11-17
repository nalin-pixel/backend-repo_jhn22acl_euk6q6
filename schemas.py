"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Core domain schemas for the Party Planner app

class Party(BaseModel):
    name: str = Field(..., description="Party name")
    date: Optional[str] = Field(None, description="ISO date (yyyy-mm-dd) or friendly text")
    theme: Optional[str] = Field(None, description="Party theme")
    location: Optional[str] = Field(None, description="Where it will be held")
    budget: Optional[float] = Field(None, ge=0, description="Budget in dollars")
    notes: Optional[str] = Field(None, description="Extra details")

class Guest(BaseModel):
    party_id: str = Field(..., description="Associated party id")
    name: str = Field(..., description="Guest name")
    email: Optional[str] = Field(None, description="Guest email")
    status: str = Field("invited", description="invited, going, maybe, declined")

class Ingredient(BaseModel):
    name: str
    quantity: float = Field(1, ge=0)
    unit: Optional[str] = None

class MenuItem(BaseModel):
    party_id: str = Field(..., description="Associated party id")
    title: str = Field(..., description="Dish/drink name")
    category: Optional[str] = Field(None, description="starter, main, dessert, drink")
    serves: Optional[int] = Field(None, ge=1)
    ingredients: List[Ingredient] = Field(default_factory=list)

# Example schemas (kept for reference)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
