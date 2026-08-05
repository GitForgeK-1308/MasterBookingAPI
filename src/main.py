from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.master_offering.router import router as service_router
from src.masters.router import router as masters_router
from src.master_schedule.router import router as schedules_router
from src.bookings.router import router as bookings_router

app = FastAPI(title="MasterBooking")

app.include_router(masters_router)
app.include_router(service_router)
app.include_router(schedules_router)
app.include_router(bookings_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)