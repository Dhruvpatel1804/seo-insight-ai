import datetime
import uuid
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean, Enum as SQLAlchemyEnum, Integer
from sqlalchemy.dialects.postgresql import UUID
from core.security import pwd_context
from db.base_class import Base

class UserTypeEnum(Enum):
    SUPERUSER = "SUPERUSER"
    USER = "USER"
    # STAFF = "STAFF"

class Users(Base):
    __tablename__ = "Users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[int | None] = mapped_column(Integer, nullable=True) # Integer doesn't take max_length
    password: Mapped[str] = mapped_column(String)
    user_type: Mapped[UserTypeEnum] = mapped_column(SQLAlchemyEnum(UserTypeEnum), default=UserTypeEnum.USER)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    def set_password(self, password):
        # Hash the password using bcrypt
        self.password = pwd_context.hash(password)

    def verify_password(self, password):
        # Verify the password using bcrypt
        return pwd_context.verify(password, self.password)

