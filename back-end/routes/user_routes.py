from fastapi import APIRouter, Depends, HTTPException
from datetime import timedelta
from jose import jwt, JWTError

from models import UserCreate, UserLogin, ForgotPasswordRequest, ResetPasswordConfirm
from security import *
from database import users_collection

from emailsender import send_reset_email

router = APIRouter()



@router.post("/register")
async def register(user: UserCreate):
    
    if await users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email is already registered.")


    await users_collection.insert_one({
        "username": user.username,
        "password": get_password_hash(user.password),
        "email": user.email,
        "company_name": user.company_name,
        "is_active": user.is_active
    })

    
    return {"message": "user created ",}


@router.post("/login")
async def login(user: UserLogin):
    db_user = await users_collection.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token(data={"sub": user.username}, expires_delta=timedelta( minutes=30))
    return {
        "access_token": token,
        "token_type": "bearer",
        
    }





@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    user = await users_collection.find_one({"email": request.email})
    if user:
        reset_token = create_access_token(data={"sub": user["username"]}, expires_delta=timedelta(minutes=5))

        try:
            send_reset_email(to_email=request.email, reset_token=reset_token)
        except Exception as e:
            print(f"Failed to send email: {e}")

    return {"message": "sent a link to your mail"}


@router.post("/reset-password-confirm")
async def reset_password(request: ResetPasswordConfirm):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        await users_collection.update_one({"username": username}, {"$set": {"password": get_password_hash(request.new_password)}})
        return {"message": "password updated "} 
    
    except JWTError:
        raise HTTPException(status_code=400, detail="invalid or expired token")