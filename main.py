from fastapi import FastAPI
from routers import auth_router
from utils import create_tables


app = FastAPI(
    title="Authentication API",
    version="1.0.0",
    description="Modulli authentication tizimi"
)

create_tables()

app.include_router(auth_router)


@app.get("/")
async def root():
    """API haqida ma'lumot"""
    return {
        "message": "Authentication API ishlamoqda!",
        "version": "1.0.0",
        "endpoints": {
            "send_code": "POST /auth/send-code",
            "verify_code": "POST /auth/verify-code",
            "set_password": "POST /auth/set-password",
            "login": "POST /auth/login",
            "me": "GET /auth/me",
            "protected": "GET /auth/protected"
        },
        "docs": "/docs"
    }



