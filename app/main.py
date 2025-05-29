from fastapi import FastAPI
from app.api import endpoints

app = FastAPI()

# Include the /ping route
app.include_router(endpoints.router)
