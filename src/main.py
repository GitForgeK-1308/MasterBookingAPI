from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from src.masters.router import router as masters_router
from src.master_services.router import router as service_router

app = FastAPI(title="MasterBooking")

app.include_router(masters_router)
app.include_router(service_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)