from __future__ import annotations
from line_profiler import profile
from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
)
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    Mapped,
    relationship,
)
from datetime import datetime

from common.hinting import raises
from db.builder import db_builder

__all__ = (
    'BaseModel',
    'BlacklistToken',
    'User',
    'Chat',
    'ChatMessage',
    'UserChatMatch',
    'UnreadCount',
)


class BaseModel(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)

    def __repr__(self) -> str:
        return type(self).__name__ + f'<{self.id}>'


class BlacklistToken(BaseModel):
    __tablename__ = 'blacklist_tokens'

    jti: Mapped[str] = mapped_column(String(500), unique=True)

    @classmethod
    def exists(cls, jti: str) -> bool:
        return db_builder.session.query(cls).filter(cls.jti == jti).first() is not None


class User(BaseModel):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, default='New')
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, default='User')

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
    @raises(ValueError)
    def by_email(cls, email: str) -> User:
        user: User | None = db_builder.session.query(cls).filter(cls.email == email).first()
        if user is None:
            raise ValueError
        return user

    @classmethod
    def email_is_already_taken(cls, email: str) -> bool:
        return cls._data_is_already_taken('email', email)

    @classmethod
    def _data_is_already_taken(cls, field_name: str,
                               value: str,
                               ) -> bool:
        user: User | None = db_builder.session.query(cls).filter(getattr(cls, field_name) == value).first()
        return user is not None


class Chat(BaseModel):
    __tablename__ = 'chats'

    name: Mapped[str] = mapped_column(String(100), nullable=True)
    is_group: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    messages: Mapped[list['ChatMessage']] = relationship(
        back_populates='chat',
        order_by='-ChatMessage.id',
        cascade='all, delete',
        lazy='dynamic',
    )
    users_chats_matches: Mapped[list['UserChatMatch']] = relationship(
        back_populates='chat',
        cascade='all, delete',
    )

    @property
    @raises(IndexError)
    def last_message(self) -> ChatMessage:
        return self.messages[0]  # type: ignore

    def users(self) -> list[User]:
        return UserChatMatch.users_of_chat(chat_id=self.id)

    def unread_messages_of_user(self, user_id: int) -> list[ChatMessage]:
        return self.messages.filter(ChatMessage.is_read == False, ChatMessage.user_id != user_id).all()  # noqa

    @raises(ValueError)
    def interlocutor_of_user(self, user_id: int) -> User:
        return UserChatMatch.interlocutor_of_user_of_chat(chat_id=self.id, user_id=user_id)

    def unread_count_of_user(self, user_id: int) -> UnreadCount:
        return UserChatMatch.unread_count_of_user_of_chat(user_id=user_id, chat_id=self.id)


class ChatMessage(BaseModel):
    __tablename__ = 'chats_messages'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    creating_datetime: Mapped[datetime] = mapped_column(DATETIME(fsp=6), default=datetime.utcnow)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped['User'] = relationship(back_populates='chats_messages', uselist=False)
    chat: Mapped['Chat'] = relationship(back_populates='messages', uselist=False)


class UserChatMatch(BaseModel):
    __tablename__ = 'users_chats'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'), nullable=False)

    user: Mapped['User'] = relationship(back_populates='user_chats_matches', uselist=False)
    chat: Mapped['Chat'] = relationship(back_populates='users_chats_matches', uselist=False)
    unread_count: Mapped['UnreadCount'] = relationship(
        back_populates='user_chat_match',
        cascade='all, delete',
        uselist=False,
    )

    @classmethod
    @profile
    @raises(PermissionError)
    def chat_if_user_has_access(cls, user_id: int,
                                chat_id: int,
                                ) -> Chat:
        match: UserChatMatch | None = db_builder.session.query(cls).filter(
            cls.user_id == user_id, cls.chat_id == chat_id
        ).first()
        if match is not None:
            return match.chat
        raise PermissionError

    @classmethod
    @profile
    def users_of_chat(cls, chat_id: int) -> list[User]:
        matches: list[cls] = db_builder.session.query(cls).filter(cls.chat_id == chat_id).all()  # type: ignore
        return [match.user for match in matches]

    @classmethod
    @profile
    def chats_of_user(cls, user_id: int) -> list[Chat]:
        matches: list[cls] = db_builder.session.query(cls).filter(cls.user_id == user_id).all()  # type: ignore
        return sorted([match.chat for match in matches], key=cls._value_for_user_chats_sort, reverse=True)

    @staticmethod
    def _value_for_user_chats_sort(chat: Chat) -> float:
        try:
            return chat.last_message.creating_datetime.timestamp()
        except IndexError:
            return 0.0

    @classmethod
    @profile
    @raises(ValueError)
    def interlocutor_of_user_of_chat(cls, user_id: int,
                                     chat_id: int,
                                     ) -> User:
        interlocutor_match: cls | None = db_builder.session.query(cls).filter(cls.user_id != user_id,
                                                                              cls.chat_id == chat_id,
                                                                              ).first()  # type: ignore
        if interlocutor_match is not None:
            return interlocutor_match.user
        raise ValueError

    @classmethod
    @profile
    @raises(ValueError)
    def private_chat_between_users(cls, first_user_id: int,
                                   second_user_id: int,
                                   ) -> Chat:
        chats_ids = []

        matches: list[cls] = db_builder.session.query(cls).filter(  # type: ignore
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
    @profile
    def all_interlocutors_of_user(cls, user_id: int) -> list[User]:
        interlocutors = set()

        chats = cls.chats_of_user(user_id)
        for chat in chats:
            users = cls.users_of_chat(chat.id)
            interlocutors.update(users)

        self_user: User = db_builder.session.get(User, user_id)  # noqa
        if self_user in interlocutors:
            interlocutors.remove(self_user)

        return list(interlocutors)

    @classmethod
    @profile
    def unread_count_of_user_of_chat(cls, user_id: int,
                                     chat_id: int,
                                     ) -> UnreadCount:
        match: cls | None = db_builder.session.query(cls).filter(cls.user_id == user_id,
                                                                 cls.chat_id == chat_id,
                                                                 ).first()  # type: ignore
        return match.unread_count


class UnreadCount(BaseModel):
    __tablename__ = 'unread_counts'

    user_chat_match_id: Mapped[int] = mapped_column(ForeignKey('users_chats.id'), nullable=False)
    value: Mapped[int] = mapped_column(Integer, default=0)

    user_chat_match: Mapped['UserChatMatch'] = relationship(back_populates='unread_count', uselist=False)
