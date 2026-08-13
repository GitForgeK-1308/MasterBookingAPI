from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.master_offering.router import router as service_router
from src.masters.router import router as masters_router
from src.master_schedule.router import router as schedules_router
from src.bookings.router import router as bookings_router
from src.users.router import router as users_router
from src.users.profile_router import router as user_profile_router
from src.categories.router import router as categories_router
from src.offering_images.router import router as offering_images_router
from src.reviews.router import router as reviews_router


UPLOADS_DIR = Path("uploads")
OFFERINGS_DIR = UPLOADS_DIR / "offerings"

OFFERINGS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


app = FastAPI(title="MasterBooking")


app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)


app.include_router(masters_router)
app.include_router(service_router)
app.include_router(schedules_router)
app.include_router(bookings_router)
app.include_router(users_router)
app.include_router(user_profile_router)
app.include_router(categories_router)
app.include_router(offering_images_router)
app.include_router(reviews_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


