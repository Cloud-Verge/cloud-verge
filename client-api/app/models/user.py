from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserData(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    oauth_token: Mapped[str] = mapped_column(index=True)
