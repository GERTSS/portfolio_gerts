from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.future import select

import models
import schemas
from database_test import engine_test, get_session

app = FastAPI()


@app.on_event("startup")
async def crete_objects():
    async with engine_test.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
        new_recipe = models.Recipe(
            title="jhon",
            time=2.2,
            ingredients="dfbsdhjjndkjf",
            description="dsjnfjkdsgngj",
        )
        async for session in get_session():
            session.add(new_recipe)
            await session.commit()


@app.on_event("shutdown")
async def delete_objects():
    async with engine_test.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
    await engine_test.dispose()


@app.post("/recipes", response_model=schemas.RecipeOut)
async def add_recipe(recipe: schemas.RecipeIn) -> JSONResponse:
    async for session in get_session():
        new_recipe = models.Recipe(**recipe.dict())
        session.add(new_recipe)
        await session.commit()
        return JSONResponse(
            content={
                "title": new_recipe.title,
                "time": new_recipe.time,
                "ingredients": new_recipe.ingredients,
                "description": new_recipe.description,
            },
            status_code=200,
        )
    return JSONResponse(content={"message": "Что то пошло не так("})


@app.get("/recipes", response_model=List[Dict[str, Any]])
async def recipes() -> JSONResponse:
    async for session in get_session():
        res = await session.execute(
            select(
                models.Recipe.title, models.Recipe.views, models.Recipe.time
            ).order_by(models.Recipe.views.desc(), models.Recipe.time.desc())
        )
        recipes_list = res.fetchall()
        return JSONResponse(
            content=[
                {
                    "title": recipe_elem.title,
                    "views": recipe_elem.views,
                    "time": recipe_elem.time,
                }
                for recipe_elem in recipes_list
            ],
            status_code=200,
        )
    return JSONResponse(content={"message": "Что то пошло не так("})


@app.get("/recipes/{id}", response_model=Dict[str, Any])
async def recipe(id: Optional[int] = None) -> JSONResponse:
    async for session in get_session():
        res = await session.execute(
            select(models.Recipe).where(models.Recipe.id == id)
        )
        result = res.scalars().first()
        if result:
            result.views += 1
            await session.commit()
            return JSONResponse(
                content={
                    "title": result.title,
                    "time": result.time,
                    "ingredients": result.ingredients,
                    "description": result.description,
                },
                status_code=200,
            )
    return JSONResponse(
        content={"message": "Что то пошло не так("}, status_code=400
    )
