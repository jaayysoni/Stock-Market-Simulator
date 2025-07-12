# Handles registration, login, Gmail OAuth, guest sessions
from fastapi import APIRouter

router = APIRouter()

@router.get("/login")
def login():
    return {"message": "Login route working"}