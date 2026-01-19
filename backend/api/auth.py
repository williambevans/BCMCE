"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ██╗  ██╗    ██╗  ██╗          ██╗  ██╗ ██████╗ ██╗     ██████╗ ██╗███╗   ██╗ ██████╗ ███████╗  ║
║   ██║  ██║    ██║  ██║          ██║  ██║██╔═══██╗██║     ██╔══██╗██║████╗  ██║██╔════╝ ██╔════╝  ║
║   ███████║    ███████║          ███████║██║   ██║██║     ██║  ██║██║██╔██╗ ██║██║  ███╗███████╗  ║
║   ██╔══██║    ██╔══██║          ██╔══██║██║   ██║██║     ██║  ██║██║██║╚██╗██║██║   ██║╚════██║  ║
║   ██║  ██║    ██║  ██║          ██║  ██║╚██████╔╝███████╗██████╔╝██║██║ ╚████║╚██████╔╝███████║  ║
║   ╚═╝  ╚═╝    ╚═╝  ╚═╝          ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝  ║
║                                                                           ║
║                 BOSQUE COUNTY MINERAL & COMMODITIES EXCHANGE             ║
║                     Authentication API Endpoints                         ║
║                                                                           ║
║   Operator:    HH Holdings LLC / Bevans Real Estate                      ║
║   Location:    397 Highway 22, Clifton, TX 76634                         ║
║   Broker:      Biri Bevans, Designated Broker                            ║
║   Module:      Authentication API Router                                 ║
║                                                                           ║
║   Copyright:   © 2026 HH Holdings LLC. All rights reserved.              ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

BCMCE Platform - Authentication API
Simplified auth for H.H. Holdings internal team only
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
import sys
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_db, User as UserModel
from models.schemas import UserLogin, User, Token, UserCreate, SuccessResponse
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
    require_admin
)
from config import get_settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login endpoint for H.H. Holdings team members

    **Authentication:**
    - Email and password required
    - Returns JWT access token valid for 8 hours (480 minutes)
    - Token must be included in Authorization header for protected endpoints

    **Default Admin Login:**
    - Email: biri@hhholdings.com
    - Password: HHHoldings2026! (change on first login)

    **Example:**
    ```json
    POST /api/v1/auth/login
    {
        "email": "biri@hhholdings.com",
        "password": "HHHoldings2026!"
    }
    ```

    **Response:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "expires_in": 28800
    }
    ```
    """
    settings = get_settings()

    # Authenticate user
    user = authenticate_user(db, user_login.email, user_login.password)

    if not user:
        logger.warning(f"Failed login attempt for {user_login.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": str(user.id),  # Convert UUID to string for JWT
            "email": user.email,
            "role": user.role
        },
        expires_delta=access_token_expires
    )

    logger.info(f"Successful login: {user.email} (role: {user.role})")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRATION_MINUTES * 60  # Convert to seconds
    }


@router.get("/me", response_model=User)
async def get_me(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get current authenticated user information

    **Authentication Required:**
    - Must include valid JWT token in Authorization header
    - Format: `Authorization: Bearer <token>`

    **Returns:**
    - User profile information
    - Email, full name, role
    - Account status and timestamps

    **Example:**
    ```bash
    GET /api/v1/auth/me
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```

    **Response:**
    ```json
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "biri@hhholdings.com",
        "full_name": "Biri Bevans",
        "role": "admin",
        "is_active": true,
        "created_at": "2026-01-19T10:00:00Z"
    }
    ```
    """
    return current_user


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    admin_user: UserModel = Depends(require_admin)
):
    """
    Register new H.H. Holdings team member (Admin only)

    **Authentication Required:**
    - Admin role required
    - Only H.H. Holdings admin can create new team members

    **User Roles:**
    - `admin`: Full access to all features (Biri Bevans, managers)
    - `user`: Standard team member access (staff)

    **Example:**
    ```json
    POST /api/v1/auth/register
    Authorization: Bearer <admin-token>
    {
        "email": "staff@hhholdings.com",
        "full_name": "John Smith",
        "role": "user",
        "password": "SecurePassword123!"
    }
    ```

    **Response:**
    ```json
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "email": "staff@hhholdings.com",
        "full_name": "John Smith",
        "role": "user",
        "is_active": true,
        "created_at": "2026-01-19T10:30:00Z"
    }
    ```
    """
    # Check if user already exists
    existing_user = db.query(UserModel).filter(UserModel.email == user_create.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {user_create.email} already exists"
        )

    # Validate role (H.H. Holdings internal only)
    if user_create.role not in ["admin", "user"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'admin' or 'user' for H.H. Holdings team"
        )

    # Create new user
    hashed_password = hash_password(user_create.password)

    new_user = UserModel(
        email=user_create.email,
        hashed_password=hashed_password,
        full_name=user_create.full_name,
        role=user_create.role,
        is_active=True,
        supplier_id=None,  # H.H. Holdings staff, not suppliers
        county_id=None     # H.H. Holdings staff, not counties
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(
        f"New user registered: {new_user.email} (role: {new_user.role}) "
        f"by admin {admin_user.email}"
    )

    return new_user


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Logout endpoint (informational only)

    **Note:**
    - JWT tokens are stateless and cannot be invalidated server-side
    - Client should delete the token from local storage
    - Token will expire automatically after 8 hours

    **Best Practice:**
    - Delete token from browser localStorage/sessionStorage
    - Clear Authorization header
    - Redirect user to login page

    **Example:**
    ```bash
    POST /api/v1/auth/logout
    Authorization: Bearer <token>
    ```

    **Response:**
    ```json
    {
        "success": true,
        "message": "Logged out successfully. Please delete your token."
    }
    ```
    """
    logger.info(f"User logout: {current_user.email}")

    return {
        "success": True,
        "message": "Logged out successfully. Please delete your token from local storage."
    }
