from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class FileEntry(Base):
    __tablename__ = 'files'

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(nullable=True)
    local_path: Mapped[str] = mapped_column(nullable=False)
