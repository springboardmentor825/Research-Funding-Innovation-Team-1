# backend/app/crud/crud_user.py

from typing import Optional
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate
from app.auth import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieves a user by email address."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, obj_in: UserCreate) -> User:
    """Creates a new user with bcrypt password hash."""
    hashed_pwd = get_password_hash(obj_in.password)
    db_obj = User(
        full_name=obj_in.full_name,
        email=obj_in.email,
        password=hashed_pwd,
        role=obj_in.role,
        login_type=obj_in.login_type
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticates user credentials."""
    user = get_user_by_email(db, email)
    if not user or not user.password:
        return None
    if not verify_password(password, user.password):
        return None
    return user
