import datetime
import uuid
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean, Enum as SQLAlchemyEnum, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from db.base_class import Base

class OtpPurpose(Enum):
    SIGNUP = "SIGNUP"
    LOGIN = "LOGIN"
    FORGOT_PASSWORD = "FORGOT_PASSWORD"
    CHANGE_PASSWORD = "CHANGE_PASSWORD"

class OtpCodes(Base):
    __tablename__ = "otp_codes"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("Users.id"), nullable=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    otp_hash: Mapped[str] = mapped_column(String)
    purpose: Mapped[OtpPurpose] = mapped_column(SQLAlchemyEnum(OtpPurpose), index=True)
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=5)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)
