from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from db.users import Users
from service.user_management import create_user, validate_jwt_token, generate_jwt_token
from core.security import pwd_context
from pydanticValidators.user import UserSignupFields, UserLoginFields
from util.common import format_response
from util.mail import send_verification_email

router = APIRouter()

@router.get("/health/")
async def health():
    return format_response(status_code=200, message="Yey! I'm healthy.")

@router.post("/signup/")
async def signup(user: UserSignupFields, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # create_user handles validation and existence checks
    user_obj = await create_user(db, user)
    
    background_tasks.add_task(send_verification_email, user_obj.email, user_obj.id)

    return format_response(status_code=201, message="User created successfully. Sent Mail to registered email.")

@router.post("/login/")
async def login(user: UserLoginFields, db: AsyncSession = Depends(get_db)):
    # Step 1: Check if the user exists
    res = await db.execute(select(Users).where(Users.email == user.email))
    db_user = res.scalar_one_or_none()
    
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Step 2: Generate JWT token
    access_token = generate_jwt_token(db_user)

    return format_response(
        status_code=200,
        message="Login successful",
        response={"access_token": access_token}
    )