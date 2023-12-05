from __future__ import annotations
from sqlalchemy import (  # pip install sqlalchemy
    create_engine,
    Integer,
    String,
    Text,
    ForeignKey,
    Engine,
)
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    relationship,
    DeclarativeBase,
    sessionmaker,
    scoped_session,
)
from datetime import datetime

from api.db.encryption import make_auth_token
from api.config import DB_URL

__all__ = (
    'BaseModel',
    'session',
    'User',
    'Chat',
    'UserChatMatch',
    'ChatMessage',
)

# Подключаемся к БД и создаём сессию (не в универе).
engine: Engine = create_engine(url=DB_URL)
session: scoped_session = scoped_session(
    sessionmaker(autocommit=False,
                 autoflush=False,
                 bind=engine,
                 )
)


class BaseModel(DeclarativeBase):
    """Базовый класс модели."""


class User(BaseModel):
    """Модель пользователя, имеющего возможность общаться в чатах."""

    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    # username + password в BasicToken.
    auth_token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    chats_messages: Mapped[list['ChatMessage']] = relationship(
        back_populates='user',
        order_by='ChatMessage.creating_datetime',
    )
    user_chats_matches: Mapped[list['UserChatMatch']] = relationship(back_populates='user')

    @classmethod
    def new_by_password(cls, username: str,
                        first_name: str,
                        last_name: str,
                        email: str,
                        password: str,
                        ) -> User:
        """Создаёт пользователя по чистому паролю. Пароль шифруется в BasicToken."""
        return User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            auth_token=make_auth_token(username=username, password=password),
        )

    @classmethod
    def auth_by_username_and_password(cls, username: str,
                                      password: str,
                                      ) -> User:
        """Возвращает пользователя с указанными `username` и `password`.
        Если пользователя с такими данными не существует, то вызывает `ValueError`.
        """
        auth_token: str = make_auth_token(username=username, password=password)
        return cls.auth_by_token(auth_token=auth_token)

    @classmethod
    def auth_by_token(cls, auth_token: str) -> User:
        """Возвращает пользователя с указанным `auth_token`.
        Если пользователя с такими данными не существует, то вызывает `ValueError`.
        """
        user: User | None = session.query(cls).filter(cls.auth_token == auth_token).first()
        if user is not None:
            return user
        raise ValueError


class Chat(BaseModel):
    """Чат. Доступ к нему имеют не все пользователи, он обеспечивается через модель `UserChatMatch`
    со связью 'многие-ко-многим'.
    """

    __tablename__ = 'chats'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    messages: Mapped[list['ChatMessage']] = relationship(
        back_populates='chat',
        order_by='ChatMessage.creating_datetime',
        cascade='all, delete',
    )
    users_chats_matches: Mapped[list['UserChatMatch']] = relationship(back_populates='chat')

    @property
    def last_message(self) -> ChatMessage:
        return self.messages[-1]  # type: ignore

    def interlocutor(self, user_id: int) -> User:
        """Находит собеседника пользователя с `user_id`."""
        return UserChatMatch.interlocutor(chat_id=self.id, user_id=user_id)


class ChatMessage(BaseModel):
    """Рядовое сообщение, относящееся к конкретному чату."""

    __tablename__ = 'chats_messages'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    creating_datetime: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    user: Mapped['User'] = relationship(back_populates='chats_messages', uselist=False)
    chat: Mapped['Chat'] = relationship(back_populates='messages', uselist=False)


class UserChatMatch(BaseModel):
    """Модель-посредник, реализующая отношение 'многие-ко-многим' и
    определяющая доступ к чатам только для тех пользователей, которые в них состоят.
    """

    __tablename__ = 'users_chats'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'), nullable=False)
    user: Mapped['User'] = relationship(back_populates='user_chats_matches', uselist=False)
    chat: Mapped['Chat'] = relationship(back_populates='users_chats_matches', uselist=False)

    @classmethod
    def chat_if_user_has_access(cls, user_id: int,
                                chat_id: int,
                                ) -> Chat:
        """Возвращает чат, если пользователь в нём состоит.
        Иначе - вызывает `PermissionError`.
        """
        match: UserChatMatch | None = session.query(cls).filter(
            cls.user_id == user_id, cls.chat_id == chat_id
        ).first()
        if match is not None:
            return match.chat
        raise PermissionError

    @classmethod
    def users_in_chat(cls, chat_id: int) -> list[User]:
        """Формирует список пользователей, состоящих в указанном чате."""
        matches: list[cls] = session.query(cls).filter(cls.chat_id == chat_id).all()  # type: ignore
        return [match.user for match in matches]

    @classmethod
    def user_chats(cls, user_id: int) -> list[Chat]:
        """Чаты, доступные указанному пользователю.
        Чаты сортируются по дате отправки последних сообщений от самого нового до самого старого.
        """
        matches: list[cls] = session.query(cls).filter(cls.user_id == user_id).all()  # type: ignore
        return sorted([match.chat for match in matches], key=cls._value_for_user_chats_sort, reverse=True)

    @staticmethod
    def _value_for_user_chats_sort(chat: Chat) -> float | int:
        """Выдаёт `datetime` последнего сообщения чата для сортировки в `user_chats`.
        Если у чата вообще нет сообщений, то возвращает 0.
        """
        try:
            return chat.last_message.creating_datetime.timestamp()
        except IndexError:
            return 0

    @classmethod
    def interlocutor(cls, user_id: int,
                     chat_id: int,
                     ) -> User:
        """Находит собеседника в личном чате с `chat_id` для пользователя с `user_id`."""
        interlocutor_match: cls | None = session.query(cls).filter(cls.user_id != user_id,
                                                                   cls.chat_id == chat_id).first()  # type: ignore
        if interlocutor_match is not None:
            return interlocutor_match.user
