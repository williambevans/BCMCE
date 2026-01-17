"""
Authentication and Authorization System
JWT-based authentication for suppliers, counties, and admins
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import logging

from backend.config import get_settings
from backend.database import get_db, User as UserModel
from backend.models.schemas import TokenData

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


# ============================================================================
# PASSWORD UTILITIES
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a password

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        bool: True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT TOKEN UTILITIES
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        data: Data to encode in token
        expires_delta: Token expiration time

    Returns:
        str: JWT token
    """
    settings = get_settings()

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """
    Decode JWT access token

    Args:
        token: JWT token

    Returns:
        TokenData: Decoded token data

    Raises:
        HTTPException: If token is invalid
    """
    settings = get_settings()

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")

        if user_id is None or email is None or role is None:
            raise credentials_exception

        return TokenData(user_id=user_id, email=email, role=role)

    except JWTError:
        raise credentials_exception


# ============================================================================
# USER AUTHENTICATION
# ============================================================================

def authenticate_user(db: Session, email: str, password: str) -> Optional[UserModel]:
    """
    Authenticate user by email and password

    Args:
        db: Database session
        email: User email
        password: User password

    Returns:
        UserModel: User if authenticated, None otherwise
    """
    user = db.query(UserModel).filter(UserModel.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        return None

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        UserModel: Current user

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    token_data = decode_access_token(token)

    user = db.query(UserModel).filter(UserModel.id == token_data.user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


# ============================================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================================

class RoleChecker:
    """
    Dependency to check user role

    Usage:
        @app.get("/admin/endpoint")
        def admin_endpoint(user: UserModel = Depends(RoleChecker(["admin"]))):
            return {"message": "Admin access granted"}
    """

    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserModel = Depends(get_current_user)) -> UserModel:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden. Required roles: {', '.join(self.allowed_roles)}"
            )
        return user


# Convenient role checkers
def require_admin(user: UserModel = Depends(get_current_user)) -> UserModel:
    """Require admin role"""
    return RoleChecker(["admin"])(user)


def require_supplier(user: UserModel = Depends(get_current_user)) -> UserModel:
    """Require supplier role"""
    return RoleChecker(["supplier", "admin"])(user)


def require_county(user: UserModel = Depends(get_current_user)) -> UserModel:
    """Require county role"""
    return RoleChecker(["county", "admin"])(user)


# ============================================================================
# USER REGISTRATION
# ============================================================================

def create_user(
    db: Session,
    email: str,
    password: str,
    full_name: str,
    role: str,
    supplier_id: Optional[int] = None,
    county_id: Optional[int] = None
) -> UserModel:
    """
    Create new user

    Args:
        db: Database session
        email: User email
        password: User password (will be hashed)
        full_name: User full name
        role: User role (supplier, county, admin)
        supplier_id: Supplier ID (for supplier users)
        county_id: County ID (for county users)

    Returns:
        UserModel: Created user

    Raises:
        ValueError: If email already exists or invalid role
    """
    # Check if email already exists
    existing_user = db.query(UserModel).filter(UserModel.email == email).first()
    if existing_user:
        raise ValueError("Email already registered")

    # Validate role
    if role not in ["supplier", "county", "admin"]:
        raise ValueError("Invalid role. Must be 'supplier', 'county', or 'admin'")

    # Validate supplier_id/county_id based on role
    if role == "supplier" and not supplier_id:
        raise ValueError("Supplier ID required for supplier role")

    if role == "county" and not county_id:
        raise ValueError("County ID required for county role")

    # Create user
    user = UserModel(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        role=role,
        supplier_id=supplier_id,
        county_id=county_id,
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"User created: {email} (role: {role})")

    return user


# ============================================================================
# PASSWORD RESET
# ============================================================================

def change_password(
    db: Session,
    user_id: int,
    old_password: str,
    new_password: str
) -> bool:
    """
    Change user password

    Args:
        db: Database session
        user_id: User ID
        old_password: Current password
        new_password: New password

    Returns:
        bool: True if password changed successfully

    Raises:
        ValueError: If old password is incorrect
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not user:
        raise ValueError("User not found")

    if not verify_password(old_password, user.hashed_password):
        raise ValueError("Incorrect current password")

    user.hashed_password = hash_password(new_password)
    db.commit()

    logger.info(f"Password changed for user: {user.email}")

    return True


def reset_password(db: Session, email: str, new_password: str) -> bool:
    """
    Reset user password (admin function)

    Args:
        db: Database session
        email: User email
        new_password: New password

    Returns:
        bool: True if password reset successfully
    """
    user = db.query(UserModel).filter(UserModel.email == email).first()

    if not user:
        raise ValueError("User not found")

    user.hashed_password = hash_password(new_password)
    db.commit()

    logger.info(f"Password reset for user: {email}")

    return True


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def deactivate_user(db: Session, user_id: int) -> bool:
    """
    Deactivate user account

    Args:
        db: Database session
        user_id: User ID

    Returns:
        bool: True if deactivated successfully
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not user:
        raise ValueError("User not found")

    user.is_active = False
    db.commit()

    logger.info(f"User deactivated: {user.email}")

    return True


def activate_user(db: Session, user_id: int) -> bool:
    """
    Activate user account

    Args:
        db: Database session
        user_id: User ID

    Returns:
        bool: True if activated successfully
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not user:
        raise ValueError("User not found")

    user.is_active = True
    db.commit()

    logger.info(f"User activated: {user.email}")

    return True


# ============================================================================
# API KEY AUTHENTICATION (Optional)
# ============================================================================

class APIKeyChecker:
    """
    Dependency to check API key

    Usage:
        @app.get("/api/endpoint")
        def api_endpoint(api_key: str = Depends(APIKeyChecker())):
            return {"message": "API key valid"}
    """

    def __call__(self, api_key: str) -> str:
        settings = get_settings()

        # In production, store API keys in database
        valid_api_keys = os.getenv("API_KEYS", "").split(",")

        if api_key not in valid_api_keys:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key"
            )

        return api_key


if __name__ == "__main__":
    import os

    print("BCMCE Authentication System")
    print("=" * 50)

    # Test password hashing
    test_password = "secure_password_123"
    hashed = hash_password(test_password)
    print(f"✓ Password hashing: {hashed[:20]}...")

    # Test password verification
    is_valid = verify_password(test_password, hashed)
    print(f"✓ Password verification: {is_valid}")

    # Test token creation
    token = create_access_token({"user_id": 1, "email": "test@example.com", "role": "admin"})
    print(f"✓ JWT token: {token[:50]}...")

    print("\n✅ Authentication system initialized successfully")
