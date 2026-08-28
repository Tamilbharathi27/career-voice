from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import jwt

from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.db.session import get_db
from app.models.user import User, Profile, UserRole
from app.schemas.user import UserCreate, UserLogin, GoogleAuthRequest, TokenResponse, TokenRefreshRequest, UserResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new student or recruiter account."""
    # Check if user already exists
    existing = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Determine role
    assigned_role = user_in.role.lower() if user_in.role.lower() in [r.value for r in UserRole] else UserRole.STUDENT.value

    # Create User
    new_user = User(
        name=user_in.name,
        email=user_in.email.lower(),
        password_hash=get_password_hash(user_in.password),
        role=assigned_role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Sync with Supabase Database & Auth Dashboard
    try:
        from app.db.supabase import get_supabase_client
        supabase = get_supabase_client()
        if supabase:
            # 1. Sync to Supabase Table Editor -> users table
            supabase.table("users").upsert({
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
                "password_hash": new_user.password_hash,
                "role": new_user.role
            }).execute()

            # 2. Sync to Supabase Authentication -> Users tab
            try:
                supabase.auth.admin.create_user({
                    "email": new_user.email,
                    "password": user_in.password,
                    "email_confirm": True,
                    "user_metadata": {
                        "name": new_user.name,
                        "role": new_user.role
                    }
                })
            except Exception as auth_err:
                print(f"[Supabase Auth Note] {auth_err}")
    except Exception as sb_err:
        print(f"[Supabase Sync Note] {sb_err}")

    # Initialize default profile
    profile = Profile(
        user_id=new_user.id,
        target_role="Full Stack Engineer" if assigned_role == UserRole.STUDENT.value else "Technical Recruiter",
        experience_level="Intermediate",
        skills="React, Python, SQL, System Design" if assigned_role == UserRole.STUDENT.value else "Technical Sourcing, Candidate Assessment",
        bio="Welcome to Career Voice!"
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    # Generate JWT Tokens
    access_token = create_access_token(new_user.id, extra_claims={"role": new_user.role, "email": new_user.email})
    refresh_token = create_refresh_token(new_user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate with email and password."""
    user = db.query(User).filter(User.email == login_data.email.lower()).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    access_token = create_access_token(user.id, extra_claims={"role": user.role, "email": user.email})
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }

@router.post("/google", response_model=TokenResponse)
def google_auth(google_in: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate or register a user via Google OAuth."""
    email = google_in.email.lower()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        import uuid
        assigned_role = google_in.role.lower() if (google_in.role and google_in.role.lower() in [r.value for r in UserRole]) else UserRole.STUDENT.value
        user_name = google_in.name if google_in.name else email.split("@")[0].capitalize()

        # Create new OAuth user
        user = User(
            name=user_name,
            email=email,
            password_hash=get_password_hash(f"OAUTH_GOOGLE_{uuid.uuid4()}"),
            role=assigned_role
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create associated Profile
        profile = Profile(
            user_id=user.id,
            target_role="Full Stack Engineer" if assigned_role == UserRole.STUDENT.value else "Technical Recruiter",
            experience_level="Intermediate",
            skills="React, Python, SQL, System Design" if assigned_role == UserRole.STUDENT.value else "Technical Sourcing, Candidate Assessment",
            bio="Welcome to Career Voice!"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

        # Sync to Supabase Table Editor
        try:
            from app.db.supabase import get_supabase_client
            supabase = get_supabase_client()
            if supabase:
                supabase.table("users").upsert({
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "password_hash": user.password_hash,
                    "role": user.role
                }).execute()
        except Exception as sb_err:
            print(f"[Supabase Google Sync Note] {sb_err}")

    access_token = create_access_token(user.id, extra_claims={"role": user.role, "email": user.email})
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: TokenRefreshRequest, db: Session = Depends(get_db)):
    """Refresh expired access token using refresh token."""
    try:
        payload = decode_token(req.refresh_token, secret_key=settings.JWT_REFRESH_SECRET_KEY)
        user_id = int(payload.get("sub"))
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_access_token = create_access_token(user.id, extra_claims={"role": user.role, "email": user.email})
    new_refresh_token = create_refresh_token(user.id)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return current_user
