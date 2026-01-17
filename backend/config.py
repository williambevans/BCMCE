"""
Configuration Management System
Centralized configuration for BCMCE platform
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field, validator
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Application
    APP_NAME: str = "BCMCE Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    DEBUG: bool = Field(False, env="DEBUG")
    API_PREFIX: str = "/api/v1"

    # Server
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(8000, env="PORT")
    WORKERS: int = Field(4, env="WORKERS")

    # Database
    DATABASE_URL: str = Field(
        "postgresql://bcmce_user:secure_password@localhost:5432/bcmce_db",
        env="DATABASE_URL"
    )
    DB_POOL_SIZE: int = Field(10, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(20, env="DB_MAX_OVERFLOW")

    # Redis
    REDIS_URL: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    REDIS_CACHE_TTL: int = Field(300, env="REDIS_CACHE_TTL")  # 5 minutes

    # Security
    SECRET_KEY: str = Field("change-this-secret-key-in-production", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # CORS
    CORS_ORIGINS: list = Field(
        ["http://localhost:3000", "https://williambevans.github.io"],
        env="CORS_ORIGINS"
    )

    # Email / SMTP
    SMTP_HOST: str = Field("smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(587, env="SMTP_PORT")
    SMTP_USER: str = Field("", env="SMTP_USER")
    SMTP_PASSWORD: str = Field("", env="SMTP_PASSWORD")
    FROM_EMAIL: str = Field("noreply@bcmce.org", env="FROM_EMAIL")
    FROM_NAME: str = Field("BCMCE Platform", env="FROM_NAME")

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = Field(30, env="WS_HEARTBEAT_INTERVAL")  # seconds

    # Business Logic
    OPTION_30_DAY_PREMIUM: float = Field(0.05, env="OPTION_30_DAY_PREMIUM")  # 5%
    OPTION_90_DAY_PREMIUM: float = Field(0.10, env="OPTION_90_DAY_PREMIUM")  # 10%
    OPTION_180_DAY_PREMIUM: float = Field(0.15, env="OPTION_180_DAY_PREMIUM")  # 15%
    OPTION_ANNUAL_PREMIUM: float = Field(0.20, env="OPTION_ANNUAL_PREMIUM")  # 20%

    HH_HOLDINGS_COMMISSION: float = Field(0.40, env="HH_HOLDINGS_COMMISSION")  # 40%
    TRANSACTION_FEE_PERCENT: float = Field(0.025, env="TRANSACTION_FEE_PERCENT")  # 2.5%

    # Alerts
    OPTION_EXPIRY_ALERT_DAYS: int = Field(7, env="OPTION_EXPIRY_ALERT_DAYS")
    PRICE_CHANGE_THRESHOLD_PERCENT: float = Field(5.0, env="PRICE_CHANGE_THRESHOLD_PERCENT")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_PER_MINUTE: int = Field(60, env="RATE_LIMIT_PER_MINUTE")

    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(None, env="LOG_FILE")

    # External APIs
    TXDOT_API_URL: str = Field(
        "https://www.txdot.gov/business/specifications.html",
        env="TXDOT_API_URL"
    )

    # Feature Flags
    ENABLE_WEBSOCKETS: bool = Field(True, env="ENABLE_WEBSOCKETS")
    ENABLE_EMAIL_NOTIFICATIONS: bool = Field(True, env="ENABLE_EMAIL_NOTIFICATIONS")
    ENABLE_PRICE_ALERTS: bool = Field(True, env="ENABLE_PRICE_ALERTS")
    ENABLE_OPTION_TRADING: bool = Field(True, env="ENABLE_OPTION_TRADING")

    # Monitoring
    SENTRY_DSN: Optional[str] = Field(None, env="SENTRY_DSN")
    PROMETHEUS_ENABLED: bool = Field(False, env="PROMETHEUS_ENABLED")

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment setting"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v.upper()

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance

    Usage:
        from backend.config import get_settings

        settings = get_settings()
        print(settings.DATABASE_URL)
    """
    return Settings()


# ============================================================================
# CONFIGURATION HELPERS
# ============================================================================

class DatabaseConfig:
    """Database configuration helper"""

    @staticmethod
    def get_connection_string(settings: Optional[Settings] = None) -> str:
        """Get database connection string"""
        if settings is None:
            settings = get_settings()
        return settings.DATABASE_URL

    @staticmethod
    def get_pool_config(settings: Optional[Settings] = None) -> dict:
        """Get database pool configuration"""
        if settings is None:
            settings = get_settings()

        return {
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_pre_ping": True,
            "echo": settings.DEBUG
        }


class SecurityConfig:
    """Security configuration helper"""

    @staticmethod
    def get_jwt_config(settings: Optional[Settings] = None) -> dict:
        """Get JWT configuration"""
        if settings is None:
            settings = get_settings()

        return {
            "secret_key": settings.SECRET_KEY,
            "algorithm": settings.ALGORITHM,
            "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
        }

    @staticmethod
    def get_cors_config(settings: Optional[Settings] = None) -> dict:
        """Get CORS configuration"""
        if settings is None:
            settings = get_settings()

        return {
            "allow_origins": settings.CORS_ORIGINS,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"]
        }


class EmailConfig:
    """Email configuration helper"""

    @staticmethod
    def get_smtp_config(settings: Optional[Settings] = None) -> dict:
        """Get SMTP configuration"""
        if settings is None:
            settings = get_settings()

        return {
            "host": settings.SMTP_HOST,
            "port": settings.SMTP_PORT,
            "user": settings.SMTP_USER,
            "password": settings.SMTP_PASSWORD,
            "from_email": settings.FROM_EMAIL,
            "from_name": settings.FROM_NAME
        }


class BusinessConfig:
    """Business logic configuration helper"""

    @staticmethod
    def get_option_premiums(settings: Optional[Settings] = None) -> dict:
        """Get option premium percentages"""
        if settings is None:
            settings = get_settings()

        return {
            "30_DAYS": settings.OPTION_30_DAY_PREMIUM,
            "90_DAYS": settings.OPTION_90_DAY_PREMIUM,
            "180_DAYS": settings.OPTION_180_DAY_PREMIUM,
            "ANNUAL": settings.OPTION_ANNUAL_PREMIUM
        }

    @staticmethod
    def calculate_option_price(spot_price: float, duration: str,
                              settings: Optional[Settings] = None) -> float:
        """
        Calculate option strike price

        Args:
            spot_price: Current spot price
            duration: Option duration (30_DAYS, 90_DAYS, etc.)
            settings: Settings instance

        Returns:
            float: Option strike price
        """
        if settings is None:
            settings = get_settings()

        premiums = BusinessConfig.get_option_premiums(settings)
        premium = premiums.get(duration, 0.10)

        return spot_price * (1 + premium)

    @staticmethod
    def calculate_hh_commission(transaction_amount: float,
                               settings: Optional[Settings] = None) -> float:
        """
        Calculate HH Holdings commission

        Args:
            transaction_amount: Transaction amount
            settings: Settings instance

        Returns:
            float: Commission amount
        """
        if settings is None:
            settings = get_settings()

        return transaction_amount * settings.HH_HOLDINGS_COMMISSION

    @staticmethod
    def calculate_transaction_fee(transaction_amount: float,
                                 settings: Optional[Settings] = None) -> float:
        """
        Calculate transaction fee

        Args:
            transaction_amount: Transaction amount
            settings: Settings instance

        Returns:
            float: Transaction fee
        """
        if settings is None:
            settings = get_settings()

        return transaction_amount * settings.TRANSACTION_FEE_PERCENT


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def configure_logging(settings: Optional[Settings] = None):
    """
    Configure application logging

    Args:
        settings: Settings instance
    """
    import logging
    import sys

    if settings is None:
        settings = get_settings()

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if configured)
    if settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.info(f"Logging configured - Level: {settings.LOG_LEVEL}")


# ============================================================================
# ENVIRONMENT INFO
# ============================================================================

def print_environment_info():
    """Print environment information"""
    settings = get_settings()

    print("=" * 70)
    print(f"  {settings.APP_NAME} v{settings.APP_VERSION}")
    print("=" * 70)
    print(f"Environment:     {settings.ENVIRONMENT}")
    print(f"Debug Mode:      {settings.DEBUG}")
    print(f"API Prefix:      {settings.API_PREFIX}")
    print(f"Database:        {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'Not configured'}")
    print(f"Redis:           {settings.REDIS_URL}")
    print(f"WebSockets:      {'Enabled' if settings.ENABLE_WEBSOCKETS else 'Disabled'}")
    print(f"Email Alerts:    {'Enabled' if settings.ENABLE_EMAIL_NOTIFICATIONS else 'Disabled'}")
    print(f"Option Trading:  {'Enabled' if settings.ENABLE_OPTION_TRADING else 'Disabled'}")
    print("=" * 70)


if __name__ == "__main__":
    # Test configuration
    print_environment_info()

    settings = get_settings()

    print("\n📊 Business Configuration:")
    print(f"  30-Day Premium:  {settings.OPTION_30_DAY_PREMIUM * 100}%")
    print(f"  90-Day Premium:  {settings.OPTION_90_DAY_PREMIUM * 100}%")
    print(f"  180-Day Premium: {settings.OPTION_180_DAY_PREMIUM * 100}%")
    print(f"  Annual Premium:  {settings.OPTION_ANNUAL_PREMIUM * 100}%")
    print(f"  HH Commission:   {settings.HH_HOLDINGS_COMMISSION * 100}%")
    print(f"  Transaction Fee: {settings.TRANSACTION_FEE_PERCENT * 100}%")

    print("\n✅ Configuration loaded successfully")
