from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, verify_password, get_password_hash, decode_access_token
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, User as UserSchema

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                    db: Session = Depends(get_db)) -> User:
    """Get current authenticated user"""
    print("get_current_user called with credentials:", credentials)
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def get_current_user1(credentials: HTTPAuthorizationCredentials = Depends(security),
                    db: Session = Depends(get_db)) -> User:
    # 🚨 BYPASS - Remove for production!
    mock_user = User()
    mock_user.id = 999
    mock_user.email = "dev@test.com"
    mock_user.name = "Dev User"
    mock_user.role = "job_seeker"  # or "recruiter"
    return mock_user

def get_current_job_seeker(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is a job seeker"""
    if current_user.role != "job_seeker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires job seeker role"
        )
    return current_user

def get_current_recruiter(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is a recruiter"""
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires recruiter role"
        )
    return current_user

@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password) if user_data.password else ""
    db_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password,
        firebase_uid=user_data.firebase_uid,
        role=user_data.role,
        company=user_data.company,
        location=user_data.location,
        phone=user_data.phone,
        email_verified=user_data.email_verified or False
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(db_user.id), "email": db_user.email, "role": str(db_user.role)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserSchema.from_orm(db_user)
    }

@router.post("/firebase-register", response_model=Token)
def firebase_register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user via Firebase authentication"""
    # Check if user already exists by email or firebase_uid
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | 
        (User.firebase_uid == user_data.firebase_uid)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered"
        )

    # Create new user (no password needed for Firebase users)
    db_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password="",  # Empty string for Firebase users
        firebase_uid=user_data.firebase_uid,
        role=user_data.role,
        company=user_data.company,
        location=user_data.location,
        phone=user_data.phone,
        email_verified=user_data.email_verified or False
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(db_user.id), "email": db_user.email, "role": str(db_user.role)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserSchema.from_orm(db_user)
    }

@router.get("/firebase-user/{firebase_uid}", response_model=UserSchema)
def get_firebase_user(firebase_uid: str, db: Session = Depends(get_db)):
    """Get user by Firebase UID"""
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserSchema.from_orm(user)

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    print(f"🔐 Login attempt for email: {user_credentials.email}")
    
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    print(f"🔐 User found: {user}")
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        print(f"🔐 Authentication failed for user: {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if email is verified
    if not user.email_verified:
        print(f"🔐 Email not verified for user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email before logging in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": str(user.role)},
        expires_delta=access_token_expires
    )
    
    print(f"🔐 Access token created: {access_token[:20]}...")
    print(f"🔐 User role: {user.role} (type: {type(user.role)})")
    
    response_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserSchema.from_orm(user)
    }
    
    print(f"🔐 Login response: {response_data}")
    return response_data



@router.get("/me", response_model=UserSchema)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    print("Current user:sfsdfsdf", current_user)

    return UserSchema.from_orm(current_user)

@router.post("/refresh")
def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh access token"""
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(current_user.id), "email": current_user.email, "role": str(current_user.role)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.patch("/verify-email")
def verify_email(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Verify user's email address"""
    try:
        # Update the user's email verification status
        current_user.email_verified = True
        db.commit()
        db.refresh(current_user)
        
        return {"success": True, "message": "Email verified successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email"
        )

@router.get("/test")
def test_auth():
    """Test endpoint to check if auth is working"""
    return {"message": "Auth endpoint is working", "status": "ok"}

@router.post("/verify-email-code")
def verify_email_with_code(verification_data: dict, db: Session = Depends(get_db)):
    """Verify user's email using verification code (for unauthenticated users)"""
    try:
        email = verification_data.get("email")
        code = verification_data.get("code")
        
        if not email or not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and verification code are required"
            )
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # For now, we'll accept any 6-digit code (in production, you'd validate against stored code)
        if len(code) == 6 and code.isdigit():
            user.email_verified = True
            db.commit()
            db.refresh(user)
            
            return {"success": True, "message": "Email verified successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email"
        )

@router.get("/verification-status")
def get_verification_status(current_user: User = Depends(get_current_user)):
    """Get user's email verification status"""
    return {
        "email_verified": current_user.email_verified,
        "email": current_user.email
    }

@router.post("/firebase-login", response_model=Token)
def firebase_login(firebase_data: dict, db: Session = Depends(get_db)):
    """Login or register user via Firebase authentication"""
    firebase_uid = firebase_data.get("firebase_uid")
    email = firebase_data.get("email")
    name = firebase_data.get("name")
    role = firebase_data.get("role")
    
    if not firebase_uid or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firebase UID and email are required"
        )
    
    # Check if user exists by firebase_uid or email
    user = db.query(User).filter(
        (User.firebase_uid == firebase_uid) | (User.email == email)
    ).first()
    
    if user:
        # User exists, update firebase_uid if needed
        if not user.firebase_uid:
            user.firebase_uid = firebase_uid
            db.commit()
            db.refresh(user)
        
        # Create access token for existing user
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": str(user.role)},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserSchema.from_orm(user)
        }
    else:
        # New user - check if role is provided
        if not role:
            # Return special response indicating role selection is needed
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "needs_role_selection": True,
                    "firebase_uid": firebase_uid,
                    "email": email,
                    "name": name or email.split('@')[0]
                }
            )
        
        # Create new user with provided role
        user = User(
            email=email,
            name=name or email.split('@')[0],
            hashed_password="",  # Empty string for Firebase users
            firebase_uid=firebase_uid,
            role=role,
            email_verified=True  # Firebase users are considered verified
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create access token for new user
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": str(user.role)},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserSchema.from_orm(user)
        }
