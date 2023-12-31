import datetime

from sqlalchemy import DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class FileEntry(Base):
    __tablename__ = 'files_info'

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    owner: Mapped[int] = mapped_column(nullable=False, index=True)
    access: Mapped[int] = mapped_column(nullable=False)
    filename: Mapped[str] = mapped_column(nullable=True)

    locations: Mapped[list[str]] = mapped_column(JSON(), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now()
    )
