from fastapi import FastAPI
from app.API.User import user_routers
from app.API.auth import auth_router
from app.API.Table import table_routers
from app.API.Category import category_routers
from app.API.Menu import menu_routers
from app.API.Upstock import update_stock_routers
from app.API.Orders import orders_routers
from fastapi.middleware.cors import CORSMiddleware

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Restaurant API SERVICE",
    version="1.0.0",
    description="A FastAPI Service for Restaurant"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Restaurant API Service!"}

app.include_router(auth_router.router)
app.include_router(user_routers.router)
app.include_router(table_routers.router)
app.include_router(category_routers.router)
app.include_router(menu_routers.router)
app.include_router(update_stock_routers.router)
app.include_router(orders_routers.router)
