from fastapi import FastAPI
from app.API.staff import staff_routers
from app.API.auth import auth_router
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
app.include_router(staff_routers.router)
