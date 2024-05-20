from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class StorageData(Base):
    __tablename__ = 'storages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    http_address: Mapped[str] = mapped_column()
    grpc_address: Mapped[str] = mapped_column()
