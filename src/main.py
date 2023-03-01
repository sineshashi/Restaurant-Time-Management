from fastapi import FastAPI
from tortoise import generate_config
from tortoise.contrib.fastapi import register_tortoise

from .config import DBURL
from .controller import router

app = FastAPI(title="Restaurant-Time-Management")

db_config = generate_config(db_url=DBURL, app_modules={"models": ["src.models", "aerich.models"]})

register_tortoise(app=app, config=db_config,generate_schemas=True, add_exception_handlers=True)

app.include_router(
    router=router,
    prefix=""
)