from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column


class UserData(DeclarativeBase):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    oauth_token = Mapped[str] = mapped_column(index=True)

    __table_args__ = {
        'postgresql_identity_start': 1
    }
