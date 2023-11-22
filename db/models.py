from __future__ import annotations
from sqlalchemy import (  # pip install sqlalchemy
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Engine,
)
from sqlalchemy.orm import (
    relationship,
    declarative_base,
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
# Создаём базовый класс моделей.
BaseModel = declarative_base()


class User(BaseModel):
    """Модель пользователя, имеющего возможность общаться в чатах."""

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    auth_token = Column(String(255), nullable=False, unique=True)  # username + password в BasicToken.

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
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    messages = relationship('ChatMessage', backref='chat', order_by='ChatMessage.creating_datetime',
                            cascade='all, delete',
                            )

    @property
    def last_message(self) -> ChatMessage:
        return self.messages[-1]  # type: ignore

    def define_chat_name_for_user_id(self, user_id: int) -> str:
        """Определяет имя чата для конкретного пользователя.
        Дело в том, что если чат - не беседа, то имя чата - это имя собеседника.
        """
        if self.name:
            return self.name  # type: ignore
        return UserChatMatch.interlocutor_name(user_id=user_id, chat_id=self.id)  # type: ignore


class ChatMessage(BaseModel):
    """Рядовое сообщение, относящееся к конкретному чату."""

    __tablename__ = 'chats_messages'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    user = relationship('User', backref='chat_message', uselist=False)
    text = Column(Text, nullable=False)
    creating_datetime = Column(DateTime, default=datetime.utcnow)


class UserChatMatch(BaseModel):
    """Модель-посредник, реализующая отношение 'многие-ко-многим' и
    определяющая доступ к чатам только для тех пользователей, которые в них состоят.
    """

    __tablename__ = 'users_chats'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    user = relationship('User', backref='user_chat', uselist=False)
    chat = relationship('Chat', backref='user_chat', uselist=False)

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
        """Чаты, доступные указанному пользователю."""
        matches: list[cls] = session.query(cls).filter(cls.user_id == user_id).all()  # type: ignore
        return [match.chat for match in matches]

    @classmethod
    def interlocutor_name(cls, user_id: int,
                          chat_id: int,
                          ) -> str:
        """Определяет имя собеседника."""
        interlocutor_match: cls | None = session.query(cls).filter(cls.user_id != user_id,
                                                                   cls.chat_id == chat_id).first()  # type: ignore
        if interlocutor_match is not None:
            return interlocutor_match.user.first_name
        raise ValueError
