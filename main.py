from fastapi import FastAPI
from routers import auth_router
from utils import create_tables
import uvicorn


app = FastAPI(
    title="Authentication API",
    version="1.0.0",
    description="Modulli authentication tizimi"
)

# Database jadvallarini yaratish
create_tables()

# Routerlarni qo'shish
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


if __name__ == "__main__":
    print("🚀 Modulli Authentication API ishga tushmoqda...")
    print("📖 Docs: http://localhost:8000/docs")
    print("🔧 Barcha funksiyalar alohida modullarga ajratilgan")
    print("\n" + "=" * 60)
    print("PROYEKT STRUKTURASI:")
    print("├── main.py              # Asosiy fayl")
    print("├── .env                 # Environment variables")
    print("├── models/user.py       # User modeli")
    print("├── schemas/auth.py      # Pydantic schemas")
    print("├── utils/               # Yordamchi funksiyalar")
    print("│   ├── database.py      # Database setup")
    print("│   ├── auth.py          # Auth utilities")
    print("│   └── email.py         # Email functions")
    print("└── routers/auth.py      # Auth routes")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)