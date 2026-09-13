from datetime import datetime, timedelta, timezone
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import os
import bcrypt
from dotenv import load_dotenv

from app.database import get_db
from app.models import User
from app.schemas import TokenData

load_dotenv()

# JWT Config configurations
SECRET_KEY = os.getenv("SECRET_KEY", "highly-secure-production-jwt-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Valid official system roles
VALID_ROLES = ["researcher", "startup_founder", "administrator"]
PUBLIC_ALLOWED_ROLES = ["researcher", "startup_founder"]

ROLE_ALIASES = {
    "funder": "startup_founder",
    "investor": "startup_founder",
    "investor_funder": "startup_founder",
    "founder": "startup_founder",
    "startup": "startup_founder",
    "admin": "administrator"
}

def normalize_role(role_str: Optional[str]) -> str:
    """Normalizes role strings to canonical identifiers via alias resolution."""
    if not role_str:
        return "researcher"
    clean = role_str.lower().strip()
    return ROLE_ALIASES.get(clean, clean)

# In-memory blacklist for stateless tokens invalidation
BLACKLISTED_TOKENS = set()

# OAuth2 context scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Matches a plain password to the encrypted bcrypt database hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Encrypts a password with standard bcrypt configuration."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates an OAuth2 compatible JWT token containing email, user_id, and role."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_pending_token(data: dict) -> str:
    """Generates a temporary signed token for new Google signups awaiting role selection."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire, "type": "pending_role"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_pending_token(token: str) -> dict:
    """Decodes and validates a pending role selection token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Pending authentication token is invalid or has expired. Please sign in with Google again."
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "pending_role":
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception

def blacklist_token(token: str) -> None:
    """Adds a token to the active in-memory logout blacklist."""
    BLACKLISTED_TOKENS.add(token)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """FastAPI Injection dependency which validates JWT token and returns active user context."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token in BLACKLISTED_TOKENS:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") == "pending_role":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account setup incomplete. Please select a user role first."
            )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, role=payload.get("role"), user_id=payload.get("user_id"))
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    if getattr(user, "account_status", "active") == "pending_role":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account activation pending role selection."
        )
    return user

from typing import Optional, List, Union

def require_role(allowed_roles: Union[List[str], str]):
    """FastAPI Authorization Dependency enforcing role-based endpoint permissions."""
    if isinstance(allowed_roles, str):
        allowed_list = [allowed_roles]
    else:
        allowed_list = list(allowed_roles)
    
    normalized_allowed = [normalize_role(r) for r in allowed_list]

    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        user_role = normalize_role(getattr(current_user, "role", "researcher"))
        
        # Access granted if user role is allowed or if user is administrator
        if user_role not in normalized_allowed and user_role != "administrator":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden. Insufficient role permissions."
            )
        return current_user
    return role_dependency

