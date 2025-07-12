from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import User
from schemas import (
    EmailRequest,
    VerifyCodeRequest,
    SetPasswordRequest,
    LoginRequest,
    Token,
    UserResponse
)
from utils import (
    get_db,
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    generate_verification_code,
    send_verification_email
)
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


@router.post("/send-code")
async def send_code(email_request: EmailRequest, db: Session = Depends(get_db)):
    """1-qadam: Email ga tasdiqlash kodini yuborish"""
    email = email_request.email

    # 6 raqamli kod yaratish
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)  # 10 daqiqa

    # Database da foydalanuvchi mavjudligini tekshirish
    user = db.query(User).filter(User.email == email).first()

    if user:
        # Mavjud foydalanuvchi uchun yangi kod
        user.verification_code = code
        user.code_expires_at = expires_at
        print(f"Mavjud foydalanuvchi uchun yangi kod: {code}")
    else:
        # Yangi foydalanuvchi yaratish
        user = User(
            email=email,
            verification_code=code,
            code_expires_at=expires_at
        )
        db.add(user)
        print(f"Yangi foydalanuvchi yaratildi. Kod: {code}")

    db.commit()

    # Console ga chiqarish
    print(f"\n{'=' * 50}")
    print(f"EMAIL YUBORILDI:")
    print(f"Kimga: {email}")
    print(f"Kod: {code}")
    print(f"Amal qilish muddati: {expires_at}")
    print(f"{'=' * 50}\n")

    # Real email yuborish
    email_sent = send_verification_email(email, code)

    if email_sent:
        return {
            "message": "Tasdiqlash kodi emailga yuborildi",
            "email": email,
            "expires_in": "10 daqiqa"
        }
    else:
        return {
            "message": "Tasdiqlash kodi yaratildi (email yuborilmadi - sozlamalarni tekshiring)",
            "email": email,
            "code": code,  # Test uchun
            "expires_in": "10 daqiqa"
        }


@router.post("/verify-code")
async def verify_code(verify_request: VerifyCodeRequest, db: Session = Depends(get_db)):
    """2-qadam: Yuborilgan kodni tekshirish"""
    email = verify_request.email
    code = verify_request.code

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi. Avval email ga kod yuboring."
        )

    # Kod tekshirish
    if not user.verification_code or user.verification_code != code:
        print(f"Noto'g'ri kod: Kutilgan {user.verification_code}, Kelgan {code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kod noto'g'ri. Qaytadan urinib ko'ring."
        )

    # Vaqt tekshirish
    if user.code_expires_at and user.code_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kod muddati tugagan. Yangi kod so'rang."
        )

    print(f"Kod to'g'ri tasdiqlandi: {email}")

    return {
        "message": "Kod to'g'ri tasdiqlandi. Endi parol o'rnating.",
        "email": email,
        "status": "verified"
    }


@router.post("/set-password")
async def set_password(password_request: SetPasswordRequest, db: Session = Depends(get_db)):
    """3-qadam: Parol o'rnatish va ro'yxatdan o'tishni yakunlash"""
    email = password_request.email
    code = password_request.code
    password = password_request.password

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )

    # Kod tekshirish
    if not user.verification_code or user.verification_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kod noto'g'ri yoki muddati tugagan"
        )

    # Vaqt tekshirish
    if user.code_expires_at and user.code_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kod muddati tugagan"
        )

    # Parol uzunligi tekshirish
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parol kamida 6 ta belgidan iborat bo'lishi kerak"
        )

    # Parolni shifrlash va saqlash
    hashed_password = hash_password(password)
    user.password = hashed_password
    user.is_verified = True
    user.verification_code = None
    user.code_expires_at = None

    db.commit()

    print(f"Parol muvaffaqiyatli o'rnatildi: {email}")

    return {
        "message": "Parol muvaffaqiyatli o'rnatildi. Endi tizimga kirishingiz mumkin.",
        "email": email,
        "status": "registered"
    }


@router.post("/login", response_model=Token)
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """4-qadam: Tizimga kirish"""
    email = login_request.email
    password = login_request.password

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email yoki parol noto'g'ri"
        )

    if not user.password or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email yoki parol noto'g'ri"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akkaunt tasdiqlanmagan. Emailni tasdiqlang."
        )

    # JWT token yaratish
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    print(f"Muvaffaqiyatli kirish: {email}")

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Joriy foydalanuvchi ma'lumotlarini olish"""
    return current_user


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """Himoyalangan sahifa - faqat login qilganlar kiradi"""
    return {
        "message": f"Salom {current_user.email}! Bu himoyalangan sahifa.",
        "user_id": current_user.id,
        "registered_at": current_user.created_at
    }