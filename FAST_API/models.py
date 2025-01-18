from sqlalchemy import Column, Float, Integer, String

from database_test import Base


class Recipe(Base):
    __tablename__ = "Recipe"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    time = Column(Float, index=True)
    ingredients = Column(String, index=True)
    description = Column(String, index=True)
    views = Column(Integer, default=0)
