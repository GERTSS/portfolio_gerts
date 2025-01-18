from pydantic import BaseModel


class BaseRecipe(BaseModel):
    title: str
    time: float
    ingredients: str
    description: str
    views: int


class RecipeIn(BaseRecipe):
    pass


class RecipeOut(BaseRecipe):
    id: int

    # model_config = ConfigDict(from_attributes=True)
