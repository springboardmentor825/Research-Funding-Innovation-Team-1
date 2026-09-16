from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os
import secrets
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, User as UserSchema, Token, ForgotPasswordRequest, GoogleAuthRequest
from app.auth import get_password_hash, verify_password, create_access_token, blacklist_token, oauth2_scheme

router = APIRouter()

def _allow_password_auth():
    """Password login/registration is disabled UNLESS explicitly enabled via env."""
    return os.getenv("ALLOW_PASSWORD_AUTH", "false").lower() in ("true", "1", "yes")

@router.get("/google-config")
def google_config():
    """Public: returns the Google OAuth client id so the frontend can load it at runtime."""
    return {"client_id": os.getenv("GOOGLE_CLIENT_ID", ""), "google_only": not _allow_password_auth()}

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new User in MySQL with hashed password validation. Disabled when Google-only auth is active."""
    if not _allow_password_auth():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Google authentication is required. Email/password registration is disabled."
        )
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    hashed_password = get_password_hash(user_in.password)
    db_obj = User(
        full_name=user_in.full_name,
        email=user_in.email,
        password=hashed_password,
        role=user_in.role,
        login_type=user_in.login_type
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Logs user in with email/password. Disabled when Google-only auth is active."""
    if not _allow_password_auth():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Google authentication is required. Email/password login is disabled."
        )
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password."
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/google", response_model=Token)
def google_login(google_in: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Signs a user in (or up) using a Google Identity Services ID token."""
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured. Set GOOGLE_CLIENT_ID on the backend."
        )
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        info = id_token.verify_oauth2_token(
            google_in.credential, google_requests.Request(), client_id
        )
        if info.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}:
            raise ValueError("Wrong issuer.")
        if not info.get("email_verified", False):
            raise ValueError("Email not verified by Google.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google credential: {str(e)}"
        )

    email = info["email"]
    google_id = str(info.get("sub", ""))
    full_name = info.get("name") or email.split("@")[0]
    picture = info.get("picture")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Auto-create the account. Honour the role the user picked on the sign-in
        # screen (safe default researcher). Only an explicit new-user signup step
        # can set researcher/startup_founder; "administrator" is reserved for the
        # seeded fixed admin account and is NEVER assignable via a Google credential.
        requested_role = (google_in.role or "researcher").strip().lower()
        if requested_role not in {"researcher", "startup_founder"}:
            role = "researcher"
        else:
            role = requested_role

        user = User(
            full_name=full_name,
            email=email,
            password=get_password_hash(secrets.token_hex(24)),
            role=role,
            login_type="google",
            google_id=google_id,
            profile_picture=picture,
            auth_provider="google",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Link Google identity to the existing account
        user.google_id = user.google_id or google_id
        user.profile_picture = user.profile_picture or picture
        user.auth_provider = "google"
        user.login_type = "google"
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(token: str = Depends(oauth2_scheme)):
    """Blacklists the requesting authorization token, terminating session."""
    blacklist_token(token)
    return {"message": "Successfully logged out."}

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(request_in: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Disabled when Google-only auth is active."""
    if not _allow_password_auth():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Google authentication is required. Password recovery is disabled."
        )
    user = db.query(User).filter(User.email == request_in.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account with this email does not exist."
        )
    return {
        "message": "Password recovery email has been sent successfully.",
        "reset_token": f"mock-reset-token-for-{user.id}"
    }

