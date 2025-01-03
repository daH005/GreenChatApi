from __future__ import annotations
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
from db.lists import (
    ChatList,
    ChatMessageList,
)
from db.json_mixins import (
    UserJSONMixin,
    ChatJSONMixin,
    ChatMessageJSONMixin,
    UnreadCountJSONMixin,
)
from db.jwt_mixins import UserJWTMixin

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
    _id: Mapped[int] = mapped_column(primary_key=True, name='id')

    @property
    def id(self) -> int:
        return self._id

    def __repr__(self) -> str:
        return type(self).__name__ + f'<{self.id}>'


class BlacklistToken(BaseModel):
    __tablename__ = 'blacklist_tokens'

    _jti: Mapped[str] = mapped_column(String(500), unique=True)

    @classmethod
    def exists(cls, jti: str) -> bool:
        return db_builder.session.query(cls).filter(cls._jti == jti).first() is not None


class User(BaseModel, UserJSONMixin, UserJWTMixin):
    __tablename__ = 'users'

    _email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    _first_name: Mapped[str] = mapped_column(String(100), nullable=False, default='New')
    _last_name: Mapped[str] = mapped_column(String(100), nullable=False, default='User')

    _chats_messages: Mapped[list['ChatMessage']] = relationship(
        back_populates='_user',
        cascade='all, delete',
    )
    _user_chats_matches: Mapped[list['UserChatMatch']] = relationship(
        back_populates='_user',
        cascade='all, delete',
    )

    @classmethod
    @raises(ValueError)
    def by_email(cls, email: str) -> User:
        user: User | None = db_builder.session.query(cls).filter(cls._email == email).first()
        if user is None:
            raise ValueError
        return user

    @classmethod
    def email_is_already_taken(cls, email: str) -> bool:
        return cls._data_is_already_taken('_email', email)

    @classmethod
    def _data_is_already_taken(cls, field_name: str,
                               value: str,
                               ) -> bool:
        user: User | None = db_builder.session.query(cls).filter(getattr(cls, field_name) == value).first()
        return user is not None

    def chats(self) -> ChatList:
        return UserChatMatch.chats_of_user(user_id=self.id)

    def set_info(self, first_name: str | None = None,
                 last_name: str | None = None,
                 ) -> None:
        if first_name is not None:
            self._first_name = first_name
        if last_name is not None:
            self._last_name = last_name


class Chat(BaseModel, ChatJSONMixin):
    __tablename__ = 'chats'

    _name: Mapped[str] = mapped_column(String(100), nullable=True)
    _is_group: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    _messages: Mapped[list['ChatMessage']] = relationship(
        back_populates='_chat',
        order_by='-ChatMessage._id',
        cascade='all, delete',
        lazy='dynamic',
    )
    _users_chats_matches: Mapped[list['UserChatMatch']] = relationship(
        back_populates='_chat',
        cascade='all, delete',
    )

    @classmethod
    def new_with_all_dependencies(cls, user_ids: list[int], **kwargs) -> list[Chat | UserChatMatch | UnreadCount]:
        objects: list[Chat | UserChatMatch | UnreadCount] = []

        chat = cls(**kwargs)
        objects.append(chat)

        for user_id in user_ids:
            match: UserChatMatch = UserChatMatch(
                _user_id=user_id,
                _chat=chat,
            )

            unread_count: UnreadCount = UnreadCount(
                _user_chat_match=match,
            )

            objects += [match, unread_count]

        return objects

    @property
    def is_group(self) -> bool:
        return self._is_group

    @property
    @raises(IndexError)
    def last_message(self) -> ChatMessage:
        return self._messages[0]  # type: ignore

    def messages(self) -> ChatMessageList:
        return ChatMessageList(self._messages)

    def users(self) -> list[User]:
        return UserChatMatch.users_of_chat(chat_id=self.id)

    @raises(PermissionError)
    def check_user_access(self, user_id: int) -> None:
        UserChatMatch.chat_if_user_has_access(user_id, self.id)

    def unread_messages_of_user(self, user_id: int) -> ChatMessageList:
        messages = self._messages.filter(ChatMessage._is_read == False, ChatMessage._user_id != user_id).all()  # noqa
        return ChatMessageList(messages)

    @raises(ValueError)
    def interlocutor_of_user(self, user_id: int) -> User:
        return UserChatMatch.interlocutor_of_user_of_chat(chat_id=self.id, user_id=user_id)

    @raises(PermissionError)
    def unread_count_of_user(self, user_id: int) -> UnreadCount:
        return UserChatMatch.unread_count_of_user_of_chat(user_id=user_id, chat_id=self.id)


class ChatMessage(BaseModel, ChatMessageJSONMixin):
    __tablename__ = 'chats_messages'

    _user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    _chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'), nullable=False)
    _text: Mapped[str] = mapped_column(Text, nullable=False)
    _creating_datetime: Mapped[datetime] = mapped_column(DATETIME(fsp=6), default=datetime.utcnow)
    _is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    _storage_id: Mapped[int] = mapped_column(Integer, nullable=True)

    _user: Mapped['User'] = relationship(back_populates='_chats_messages', uselist=False)
    _chat: Mapped['Chat'] = relationship(back_populates='_messages', uselist=False)

    @classmethod
    @raises(ValueError)
    def by_storage_id(cls, storage_id: int) -> ChatMessage:
        chat_message: ChatMessage | None = db_builder.session.query(cls).filter(cls._storage_id == storage_id).first()
        if not chat_message:
            raise ValueError
        return chat_message

    @property
    def is_read(self) -> bool:
        return self._is_read

    @property
    def user(self) -> User:
        return self._user

    @property
    def chat(self) -> Chat:
        return self._chat

    def read(self) -> None:
        self._is_read = True


class UserChatMatch(BaseModel):
    __tablename__ = 'users_chats'

    _user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    _chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'), nullable=False)

    _user: Mapped['User'] = relationship(back_populates='_user_chats_matches', uselist=False)
    _chat: Mapped['Chat'] = relationship(back_populates='_users_chats_matches', uselist=False)
    _unread_count: Mapped['UnreadCount'] = relationship(
        back_populates='_user_chat_match',
        cascade='all, delete',
        uselist=False,
    )

    @property
    def user(self) -> User:
        return self._user

    @property
    def chat(self) -> Chat:
        return self._chat

    @property
    def unread_count(self) -> UnreadCount:
        return self._unread_count

    @classmethod
    @raises(PermissionError)
    def chat_if_user_has_access(cls, user_id: int,
                                chat_id: int,
                                ) -> Chat:
        match: UserChatMatch | None = db_builder.session.query(cls).filter(
            cls._user_id == user_id, cls._chat_id == chat_id
        ).first()
        if match is not None:
            return match.chat
        raise PermissionError

    @classmethod
    def users_of_chat(cls, chat_id: int) -> list[User]:
        matches: list[cls] = db_builder.session.query(cls).filter(cls._chat_id == chat_id).all()  # type: ignore
        return [match.user for match in matches]

    @classmethod
    def chats_of_user(cls, user_id: int) -> ChatList:
        matches: list[cls] = db_builder.session.query(cls).filter(cls._user_id == user_id).all()  # type: ignore
        chats = sorted([match.chat for match in matches], key=cls._value_for_user_chats_sort, reverse=True)
        return ChatList(chats, user_id)

    @staticmethod
    def _value_for_user_chats_sort(chat: Chat) -> float:
        try:
            return chat.last_message._creating_datetime.timestamp()
        except IndexError:
            return 0.0

    @classmethod
    @raises(ValueError)
    def interlocutor_of_user_of_chat(cls, user_id: int,
                                     chat_id: int,
                                     ) -> User:
        interlocutor_match: cls | None = db_builder.session.query(cls).filter(cls._user_id != user_id,
                                                                              cls._chat_id == chat_id,
                                                                              ).first()  # type: ignore
        if interlocutor_match is not None:
            return interlocutor_match.user
        raise ValueError

    @classmethod
    @raises(ValueError)
    def private_chat_between_users(cls, first_user_id: int,
                                   second_user_id: int,
                                   ) -> Chat:
        chats_ids = []

        matches: list[cls] = db_builder.session.query(cls).filter(  # type: ignore
            (cls._user_id == first_user_id) | (cls._user_id == second_user_id),
        ).all()
        for match in matches:
            if match.chat.is_group:
                continue
            if match._chat_id in chats_ids:
                return match.chat
            chats_ids.append(match._chat_id)

        raise ValueError

    @classmethod
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
    @raises(PermissionError)
    def unread_count_of_user_of_chat(cls, user_id: int,
                                     chat_id: int,
                                     ) -> UnreadCount:
        match: cls | None = db_builder.session.query(cls).filter(cls._user_id == user_id,
                                                                 cls._chat_id == chat_id,
                                                                 ).first()  # type: ignore
        if match is None:
            raise PermissionError

        return match.unread_count


class UnreadCount(BaseModel, UnreadCountJSONMixin):
    __tablename__ = 'unread_counts'

    _user_chat_match_id: Mapped[int] = mapped_column(ForeignKey('users_chats.id'), nullable=False)
    _value: Mapped[int] = mapped_column(Integer, default=0)

    _user_chat_match: Mapped['UserChatMatch'] = relationship(back_populates='_unread_count', uselist=False)

    @property
    def value(self) -> int:
        return self._value

    def set(self, value: int) -> None:
        self._value = value

    def increase(self) -> None:
        self._value += 1

    def decrease(self) -> None:
        self._value -= 1
        if self._value < 0:
            self._value = 0
