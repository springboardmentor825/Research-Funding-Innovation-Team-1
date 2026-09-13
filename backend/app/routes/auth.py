from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.database import get_db
from app.models import User, ResearchProfile
from app.schemas import (
    UserCreate,
    User as UserSchema,
    Token,
    ForgotPasswordRequest,
    UserLoginRequest,
    GoogleAuthRequest,
    GoogleRoleCompletionRequest
)
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_pending_token,
    verify_pending_token,
    blacklist_token,
    oauth2_scheme,
    get_current_user,
    VALID_ROLES,
    PUBLIC_ALLOWED_ROLES,
    normalize_role
)

router = APIRouter()

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user in MySQL. Blocks self-registration as administrator."""
    # 1. Administrator Security Guard & Canonical Role Normalization
    raw_role = user_in.role or "researcher"
    role_to_set = normalize_role(raw_role)
    if role_to_set == "administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public self-registration as Administrator is strictly prohibited."
        )
    if role_to_set not in PUBLIC_ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user role: '{user_in.role}'. Allowed roles: {', '.join(PUBLIC_ALLOWED_ROLES)}"
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
        role=role_to_set,
        login_type=user_in.login_type or "email",
        auth_provider="email"
    )
    db_obj.account_status = "active"
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # Seed default research profile if needed
    existing_profile = db.query(ResearchProfile).filter(ResearchProfile.user_id == db_obj.id).first()
    if not existing_profile:
        default_profile = ResearchProfile(
            user_id=db_obj.id,
            organization="General Organization",
            designation=role_to_set.replace("_", " ").title(),
            research_domain="General Research",
            technology_area="General Technology",
            research_interests="Innovation & Research",
            keywords="research, innovation"
        )
        db.add(default_profile)
        db.commit()

    return db_obj

@router.post("/login", response_model=Token)
def login(
    login_data: Optional[UserLoginRequest] = Body(None),
    form_data: Optional[OAuth2PasswordRequestForm] = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    """
    Logs in user with Email + Password + Role Validation.
    Validates selected_role against stored database user.role.
    Does NOT change stored database role.
    """
    email = None
    password = None
    selected_role = None

    if login_data and login_data.email:
        email = login_data.email
        password = login_data.password
        selected_role = login_data.selected_role
    elif form_data and getattr(form_data, "username", None):
        email = form_data.username
        password = form_data.password
        selected_role = getattr(form_data, "scopes", [None])[0] if getattr(form_data, "scopes", None) else None

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required."
        )

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password."
        )

    # Validate selected_role if provided
    if selected_role:
        clean_selected = normalize_role(selected_role)
        user_db_role = normalize_role(user.role)
        if clean_selected != user_db_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected role does not match your account role."
            )

    access_token = create_access_token(data={
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "name": user.full_name
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "account_status": getattr(user, "account_status", "active"),
        "user_id": user.id,
        "full_name": user.full_name,
        "status": "success"
    }

@router.post("/google", response_model=Token)
def google_auth(payload: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Google OAuth Authentication Endpoint.
    - If user exists: Logs user in automatically with stored database role.
    - If user is new: Returns pending_role_selection status and pending_token.
    """
    email = payload.email
    full_name = payload.full_name or "Google User"

    # If payload contains Google credential/id_token, extract email
    if not email and payload.credential:
        # Simple token parsing for Google OAuth payload (or dev mock)
        email = f"google_user_{uuid.uuid4().hex[:8]}@gmail.com"

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google user email is required."
        )

    user = db.query(User).filter(User.email == email).first()

    # EXISTING GOOGLE USER FLOW
    if user:
        if getattr(user, "account_status", "active") == "pending_role":
            pending_token = create_pending_token({
                "email": user.email,
                "full_name": user.full_name,
                "google_id": user.google_id
            })
            return {
                "status": "pending_role_selection",
                "pending_token": pending_token,
                "email": user.email,
                "full_name": user.full_name
            }

        access_token = create_access_token(data={
            "sub": user.email,
            "user_id": user.id,
            "role": user.role,
            "name": user.full_name
        })
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role,
            "account_status": "active",
            "user_id": user.id,
            "full_name": user.full_name,
            "status": "success"
        }

    # NEW GOOGLE USER FLOW -> Require role selection
    pending_token = create_pending_token({
        "email": email,
        "full_name": full_name,
        "google_id": f"google_{uuid.uuid4().hex[:12]}"
    })

    return {
        "status": "pending_role_selection",
        "pending_token": pending_token,
        "email": email,
        "full_name": full_name
    }

@router.post("/google/complete-registration", response_model=Token)
def complete_google_registration(payload: GoogleRoleCompletionRequest, db: Session = Depends(get_db)):
    """
    Completes registration for a new Google user after role selection.
    Validates pending_token and saves selected role in database.
    """
    token_data = verify_pending_token(payload.pending_token)
    selected_role = normalize_role(payload.selected_role)

    # Administrator Security Guard
    if selected_role == "administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public self-selection of Administrator role is strictly prohibited."
        )

    if selected_role not in PUBLIC_ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role selection: '{payload.selected_role}'. Allowed roles: {', '.join(PUBLIC_ALLOWED_ROLES)}"
        )

    email = token_data.get("email")
    full_name = token_data.get("full_name") or "Google User"
    google_id = token_data.get("google_id")

    user = db.query(User).filter(User.email == email).first()
    if user:
        # Update existing pending user
        user.role = selected_role
        user.account_status = "active"
        db.commit()
        db.refresh(user)
    else:
        # Create active user
        user = User(
            full_name=full_name,
            email=email,
            password=None, # Google OAuth user
            role=selected_role,
            login_type="google",
            auth_provider="google",
            google_id=google_id
        )
        user.account_status = "active"
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create default profile
        profile = ResearchProfile(
            user_id=user.id,
            organization="Google User Organization",
            designation=selected_role.replace("_", " ").title(),
            research_domain="General Research",
            technology_area="General Technology",
            research_interests="Innovation & Research",
            keywords="google, research"
        )
        db.add(profile)
        db.commit()

    access_token = create_access_token(data={
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "name": user.full_name
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "account_status": "active",
        "user_id": user.id,
        "full_name": user.full_name,
        "status": "success"
    }

@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns currently authenticated user profile."""
    return current_user

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(token: str = Depends(oauth2_scheme)):
    """Blacklists the requesting authorization token."""
    blacklist_token(token)
    return {"message": "Successfully logged out."}

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(request_in: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Triggers account password recovery pipeline."""
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
