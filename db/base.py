from sqlalchemy.orm import DeclarativeBase

__all__ = (
    'BaseModel',
)


class BaseModel(DeclarativeBase):
    id: int

    def __repr__(self) -> str:
        return type(self).__name__ + f'<{self.id}>'
