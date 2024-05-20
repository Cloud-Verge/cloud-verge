from sqlalchemy import JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class FileData(Base):
    __tablename__ = 'files_info'

    id: Mapped[str] = mapped_column(primary_key=True, index=True)

    filename: Mapped[str] = mapped_column(nullable=False)
    locations: Mapped[dict[str, str]] = mapped_column(JSON(), nullable=False)
