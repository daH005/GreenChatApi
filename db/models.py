from __future__ import annotations
from sqlalchemy import (  # pip install sqlalchemy
    create_engine,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    Engine,
)
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    Mapped,
    relationship,
    sessionmaker,
    scoped_session,
)
from datetime import datetime

from api.hinting import raises
from api.config import DB_URL
from api.db.encryption import make_auth_token

__all__ = (
    'session',
    'BaseModel',
    'User',
    'Chat',
    'UserChatMatch',
    'ChatMessage',
)

engine: Engine = create_engine(url=DB_URL)
session: scoped_session = scoped_session(
    sessionmaker(autocommit=False,
                 autoflush=False,
                 bind=engine,
                 )
)


class BaseModel(DeclarativeBase):
    id: int

    def __repr__(self) -> str:
        return type(self).__name__ + f'<{self.id}>'


class User(BaseModel):

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    auth_token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    chats_messages: Mapped[list['ChatMessage']] = relationship(
        back_populates='user',
        order_by='ChatMessage.creating_datetime',
        cascade='all, delete',
    )
    user_chats_matches: Mapped[list['UserChatMatch']] = relationship(
        back_populates='user',
        cascade='all, delete',
    )

    @classmethod
    def new_by_password(cls, username: str,
                        password: str,
                        email: str,
                        first_name: str,
                        last_name: str,
                        ) -> User:
        return User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            auth_token=make_auth_token(username=username, password=password),
        )

    @classmethod
    @raises(ValueError)
    def auth_by_username_and_password(cls, username: str,
                                      password: str,
                                      ) -> User:
        auth_token: str = make_auth_token(username=username, password=password)
        return cls.auth_by_token(auth_token=auth_token)

    @classmethod
    @raises(ValueError)
    def auth_by_token(cls, auth_token: str) -> User:
        user: User | None = session.query(cls).filter(cls.auth_token == auth_token).first()
        if user is not None:
            return user
        raise ValueError

    @classmethod
    def _data_is_already_taken(cls, field_name: str,
                               value: str,
                               ) -> bool:
        user: User | None = session.query(cls).filter(getattr(cls, field_name) == value).first()
        return user is not None

    @classmethod
    def username_is_already_taken(cls, username_to_check: str) -> bool:
        return cls._data_is_already_taken('username', username_to_check)

    @classmethod
    def email_is_already_taken(cls, email_to_check: str) -> bool:
        return cls._data_is_already_taken('email', email_to_check)


class Chat(BaseModel):

    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    is_group: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    messages: Mapped[list['ChatMessage']] = relationship(
        back_populates='chat',
        order_by='-ChatMessage.id',
        cascade='all, delete',
    )
    users_chats_matches: Mapped[list['UserChatMatch']] = relationship(
        back_populates='chat',
        cascade='all, delete',
    )

    @property
    @raises(IndexError)
    def last_message(self) -> ChatMessage:
        return self.messages[0]  # type: ignore

    @raises(ValueError)
    def interlocutor(self, user_id: int) -> User:
        return UserChatMatch.interlocutor(chat_id=self.id, user_id=user_id)

    def users(self) -> list[User]:
        return UserChatMatch.users_in_chat(chat_id=self.id)


class ChatMessage(BaseModel):

    __tablename__ = 'chats_messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    creating_datetime: Mapped[datetime] = mapped_column(DATETIME(fsp=6), default=datetime.utcnow)

    user: Mapped['User'] = relationship(back_populates='chats_messages', uselist=False)
    chat: Mapped['Chat'] = relationship(back_populates='messages', uselist=False)


class UserChatMatch(BaseModel):

    __tablename__ = 'users_chats'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'), nullable=False)

    user: Mapped['User'] = relationship(back_populates='user_chats_matches', uselist=False)
    chat: Mapped['Chat'] = relationship(back_populates='users_chats_matches', uselist=False)

    @classmethod
    @raises(PermissionError)
    def chat_if_user_has_access(cls, user_id: int,
                                chat_id: int,
                                ) -> Chat:
        match: UserChatMatch | None = session.query(cls).filter(
            cls.user_id == user_id, cls.chat_id == chat_id
        ).first()
        if match is not None:
            return match.chat
        raise PermissionError

    @classmethod
    def users_in_chat(cls, chat_id: int) -> list[User]:
        matches: list[cls] = session.query(cls).filter(cls.chat_id == chat_id).all()  # type: ignore
        return [match.user for match in matches]

    @classmethod
    def user_chats(cls, user_id: int) -> list[Chat]:
        matches: list[cls] = session.query(cls).filter(cls.user_id == user_id).all()  # type: ignore
        return sorted([match.chat for match in matches], key=cls._value_for_user_chats_sort, reverse=True)

    @staticmethod
    def _value_for_user_chats_sort(chat: Chat) -> float:
        try:
            return chat.last_message.creating_datetime.timestamp()
        except IndexError:
            return 0.0

    @classmethod
    @raises(ValueError)
    def interlocutor(cls, user_id: int,
                     chat_id: int,
                     ) -> User | None:
        interlocutor_match: cls | None = session.query(cls).filter(cls.user_id != user_id,
                                                                   cls.chat_id == chat_id,
                                                                   ).first()  # type: ignore
        if interlocutor_match is not None:
            return interlocutor_match.user
        raise ValueError

    @classmethod
    @raises(ValueError)
    def find_private_chat(cls, first_user_id: int,
                          second_user_id: int,
                          ) -> Chat:
        # FixMe: Улучшить, если появятся идеи о лучшей реализации, вероятно, с использованием более лучших SQL-запросов.
        chats_ids = []

        matches: list[cls] = session.query(cls).filter(  # type: ignore
            (cls.user_id == first_user_id) | (cls.user_id == second_user_id),
        ).all()
        for match in matches:
            if match.chat.is_group:
                continue
            if match.chat_id in chats_ids:
                return match.chat
            chats_ids.append(match.chat_id)

        raise ValueError

    @classmethod
    def find_all_interlocutors(cls, user_id: int) -> list[User]:
        interlocutors = set()

        chats = cls.user_chats(user_id)
        for chat in chats:
            users = cls.users_in_chat(chat.id)
            interlocutors.update(users)

        self_user: User = session.get(User, user_id)  # noqa
        if self_user in interlocutors:
            interlocutors.remove(self_user)

        return list(interlocutors)
