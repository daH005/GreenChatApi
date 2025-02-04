from datetime import datetime
from typing import Union, Self, cast

from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    desc,
    CheckConstraint,
    func,
)
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    Mapped,
    relationship,
    Query,
)

from common.hinting import raises
from db.builder import db_builder
from db.i import (
    IBaseModel,
    IAuthToken,
    IUser,
    IChat,
    IMessage,
    IUserChatMatch,
    IUnreadCount,
)
from db.json_mixins import (
    UserJSONMixin,
    ChatJSONMixin,
    MessageJSONMixin,
    UnreadCountJSONMixin,
)
from db.signal_mixins import (
    ChatSignalMixin,
    MessageSignalMixin,
)

__all__ = (
    'BaseModel',
    'AuthToken',
    'User',
    'Chat',
    'Message',
    'UserChatMatch',
    'UnreadCount',
)


class BaseModel(DeclarativeBase, IBaseModel):
    _id: Mapped[int] = mapped_column(primary_key=True, name='id')

    @property
    def id(self) -> int:
        return self._id

    @classmethod
    @raises(ValueError)
    def by_id(cls, id_: int) -> Self:
        obj: cls = cast(cls, db_builder.session.get(cls, id_))
        if not obj:
            raise ValueError
        return obj

    def __repr__(self) -> str:
        return type(self).__name__ + f'<{self.id}>'


class AuthToken(BaseModel, IAuthToken):
    __tablename__ = 'auth_tokens'

    _user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), name='user_id', nullable=False)
    _value: Mapped[str] = mapped_column(String(500), name='value', unique=True)
    _is_refresh: Mapped[bool] = mapped_column(Boolean, name='is_refresh', nullable=False)

    _user: Mapped['User'] = relationship(back_populates='_tokens', uselist=False)

    @classmethod
    def create(cls, value: str,
               is_refresh: bool,
               user: 'User',
               ) -> Self:
        return cls(_value=value, _is_refresh=is_refresh, _user=user)

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def exists(cls, value: str) -> bool:
        return db_builder.session.query(cls).filter(cls._value == value).first() is not None

    @classmethod
    @raises(ValueError)
    def by_value(cls, value: str) -> Self:
        token: cls | None = db_builder.session.query(cls).filter(cls._value == value).first()
        if token is None:
            raise ValueError
        return token


class User(BaseModel, UserJSONMixin, IUser):
    __tablename__ = 'users'

    _email: Mapped[str] = mapped_column(String(200), name='email', nullable=False, unique=True)
    _first_name: Mapped[str] = mapped_column(String(100), name='first_name', nullable=False, default='New')
    _last_name: Mapped[str] = mapped_column(String(100), name='last_name', nullable=False, default='User')

    _tokens: Mapped[list['AuthToken']] = relationship(
        back_populates='_user',
        cascade='all, delete',
    )
    _messages: Mapped[list['Message']] = relationship(
        back_populates='_user',
        cascade='all, delete',
    )
    _user_chats_matches: Mapped[list['UserChatMatch']] = relationship(
        back_populates='_user',
        cascade='all, delete',
    )

    @classmethod
    def create(cls, email: str) -> Self:
        return cls(_email=email)

    @property
    def email(self) -> str:
        return self._email

    @property
    def first_name(self) -> str:
        return self._first_name

    @property
    def last_name(self) -> str:
        return self._last_name

    @classmethod
    @raises(ValueError)
    def by_email(cls, email: str) -> Self:
        user: cls | None = db_builder.session.query(cls).filter(cls._email == email).first()
        if user is None:
            raise ValueError
        return user

    def chats(self) -> 'ChatList':
        return UserChatMatch.chats_of_user(self.id)

    def set_info(self, first_name: str | None = None,
                 last_name: str | None = None,
                 ) -> None:
        if first_name is not None:
            self._first_name = cast(Mapped[str], first_name)
        if last_name is not None:
            self._last_name = cast(Mapped[str], last_name)


class Chat(BaseModel, ChatJSONMixin, ChatSignalMixin, IChat):
    __tablename__ = 'chats'

    _name: Mapped[str | None] = mapped_column(String(100), name='name', nullable=True)
    _is_group: Mapped[bool] = mapped_column(Boolean, name='is_group', nullable=False, default=False)

    _messages: Mapped[list['Message']] = relationship(
        back_populates='_chat',
        order_by='-Message._id',
        cascade='all, delete',
        lazy='dynamic',
    )
    _user_chat_matches: Mapped[list['UserChatMatch']] = relationship(
        back_populates='_chat',
        cascade='all, delete',
    )

    @classmethod
    def new_with_all_dependencies(cls, user_ids: list[int],
                                  **kwargs,
                                  ) -> tuple[Self, list['UserChatMatch', 'UnreadCount']]:
        objects: list[cls | UserChatMatch | UnreadCount] = []
        chat: cls = cls.create(**kwargs)

        for user_id in user_ids:
            match: UserChatMatch = UserChatMatch(
                _user_id=user_id,
                _chat=chat,
            )
            unread_count: UnreadCount = UnreadCount(
                _user_chat_match=match,
            )
            objects += [match, unread_count]

        return chat, objects

    @classmethod
    def create(cls, name: str | None = None,
               is_group: bool = False,
               ) -> Self:
        return cls(_name=name, _is_group=is_group)

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def is_group(self) -> bool:
        return self._is_group

    @property
    @raises(IndexError)
    def last_message(self) -> 'Message':
        return cast(Message, self._messages[0])

    def messages(self, offset: int | None = None,
                 size: int | None = None,
                 ) -> 'MessageList':
        messages: list[Message] = cast(Query[Message], self._messages).offset(offset).limit(size).all()
        return MessageList(messages)

    def unread_interlocutor_messages_up_to(self, message_id: int,
                                           user_id_to_ignore: int,
                                           ) -> 'MessageList':
        messages: list[Message] = cast(Query[Message], self._messages).filter(
            Message._id <= message_id,  # noqa
            Message._is_read == False,  # noqa
            Message._user_id != user_id_to_ignore,  # noqa
        ).all()
        return MessageList(messages)

    def interlocutor_messages_after_count(self, message_id: int,
                                          user_id_to_ignore: int,
                                          ) -> int:
        return cast(Query[Message], self._messages).filter(
            Message._id > message_id,  # noqa
            Message._user_id != user_id_to_ignore,  # noqa
        ).count()

    def users(self) -> 'UserList':
        return UserList(UserChatMatch.users_of_chat(self.id))

    @raises(PermissionError)
    def check_user_access(self, user_id: int) -> None:
        UserChatMatch.chat_if_user_has_access(user_id, self.id)

    @raises(ValueError)
    def interlocutor_of_user(self, user_id: int) -> 'User':
        return UserChatMatch.interlocutor_of_user_of_chat(user_id, self.id)

    @raises(PermissionError)
    def unread_count_of_user(self, user_id: int) -> 'UnreadCount':
        return UserChatMatch.unread_count_of_user_of_chat(user_id, self.id)


class Message(BaseModel, MessageJSONMixin, MessageSignalMixin, IMessage):
    __tablename__ = 'messages'

    _user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), name='user_id', nullable=False)
    _chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id', ondelete='CASCADE'), name='chat_id', nullable=False)
    _replied_message_id: Mapped[int | None] = mapped_column(ForeignKey('messages.id'), name='replied_message_id')
    _text: Mapped[str] = mapped_column(Text, name='text', nullable=False)
    _creating_datetime: Mapped[datetime] = mapped_column(DATETIME(fsp=6), name='creating_datetime',
                                                         default=datetime.utcnow)
    _is_read: Mapped[bool] = mapped_column(Boolean, name='is_read', default=False)

    _user: Mapped['User'] = relationship(
        back_populates='_messages',
        uselist=False,
    )
    _chat: Mapped['Chat'] = relationship(
        back_populates='_messages',
        uselist=False,
    )
    _replied_message: Mapped[Union['Message', None]] = relationship(
        back_populates='_reply_message',
        remote_side='Message._id',
        uselist=False,
    )
    _reply_message: Mapped[Union['Message', None]] = relationship(
        back_populates='_replied_message',
        uselist=False,
    )

    @classmethod
    def create(cls, text: str,
               user: 'User',
               chat: 'Chat',
               replied_message: Union['Message', None] = None,
               ) -> Self:
        return cls(_text=text, _user=user, _chat=chat, _replied_message=replied_message)

    @property
    def text(self) -> str:
        return self._text

    @property
    def creating_datetime(self) -> datetime:
        return self._creating_datetime

    @property
    def is_read(self) -> bool:
        return self._is_read

    @property
    def user(self) -> User:
        return self._user

    @property
    def chat(self) -> Chat:
        return self._chat

    @property
    def storage(self) -> 'MessageStorage':
        if not hasattr(self, '_storage'):
            self._storage = MessageStorage(self)
        return cast(MessageStorage, self._storage)

    def read(self) -> None:
        self._is_read = cast(Mapped[bool], True)

    def set_text(self, text: str) -> None:
        self._text = cast(Mapped[str], text)

    def set_replied_message(self, replied_message_id: int | None) -> None:
        self._replied_message_id = cast(Mapped[int], replied_message_id)


class UserChatMatch(BaseModel, IUserChatMatch):
    __tablename__ = 'user_chat_matches'

    _user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), name='user_id', nullable=False)
    _chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id', ondelete='CASCADE'), name='chat_id', nullable=False)

    _user: Mapped['User'] = relationship(
        back_populates='_user_chats_matches',
        uselist=False,
    )
    _chat: Mapped['Chat'] = relationship(
        back_populates='_user_chat_matches',
        uselist=False,
    )
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
    def unread_count(self) -> 'UnreadCount':
        return self._unread_count

    @classmethod
    @raises(PermissionError)
    def chat_if_user_has_access(cls, user_id: int,
                                chat_id: int,
                                ) -> 'Chat':
        match: cls | None = db_builder.session.query(cls).filter(
            cls._user_id == user_id, cls._chat_id == chat_id
        ).first()
        if match is not None:
            return match.chat
        raise PermissionError

    @classmethod
    def users_of_chat(cls, chat_id: int) -> 'UserList':
        matches = db_builder.session.query(cls).filter(cls._chat_id == chat_id).all()
        matches = cast(list[cls], matches)
        return UserList([match.user for match in matches])

    @classmethod
    def chats_of_user(cls, user_id: int) -> 'ChatList':
        query = db_builder.session.query(cls, Chat, Message)

        joined_query = query.join(
            Chat, Chat._id == cls._chat_id,
        ).join(
            Message, Chat._id == Message._chat_id,  # noqa
            isouter=True,
        )

        filtered_and_ordered_query = joined_query.filter(
            cls._user_id == user_id,
        ).order_by(
            desc(Message._creating_datetime),  # noqa
        )

        chats = filtered_and_ordered_query.with_entities(Chat).all()
        chats = cast(list[Chat], chats)
        return ChatList(chats, user_id)

    @classmethod
    @raises(ValueError)
    def interlocutor_of_user_of_chat(cls, user_id: int,
                                     chat_id: int,
                                     ) -> 'User':
        interlocutor_match: cls | None = db_builder.session.query(cls).filter(
            cls._user_id != user_id,
            cls._chat_id == chat_id,
        ).first()
        if interlocutor_match is not None:
            return interlocutor_match.user
        raise ValueError

    @classmethod
    @raises(ValueError)
    def private_chat_between_users(cls, first_user_id: int,
                                   second_user_id: int,
                                   ) -> 'Chat':
        query = db_builder.session.query(cls, Chat)

        joined_query = query.join(
            Chat, Chat._id == cls._chat_id,
        )

        filtered_query = joined_query.filter(
            Chat._is_group == False,  # noqa
            cls._user_id.in_([
                first_user_id,
                second_user_id,
            ]),
        ).group_by(cls._chat_id).having(
            func.count(cls._user_id) == 2,
        )

        chat: Chat | None = filtered_query.with_entities(Chat).first()
        if chat is None:
            raise ValueError

        return chat

    @classmethod
    def all_interlocutors_of_user(cls, user_id: int) -> 'UserList':
        chat_ids: list[int] = cast(
            list[int],
            db_builder.session.query(cls._chat_id).filter(cls._user_id == user_id).all(),
        )
        query = db_builder.session.query(cls, User)

        joined_query = query.join(
            User, User._id == cls._user_id,
        )

        filtered_query = joined_query.filter(
            cls._user_id != user_id,
            cls._chat_id.in_(chat_ids),
        )

        interlocutors: list[User] = cast(list[User], filtered_query.with_entities(User).all())
        return UserList(interlocutors)

    @classmethod
    @raises(PermissionError)
    def unread_count_of_user_of_chat(cls, user_id: int,
                                     chat_id: int,
                                     ) -> 'UnreadCount':
        match: cls | None = db_builder.session.query(cls).filter(
            cls._user_id == user_id,
            cls._chat_id == chat_id,
        ).first()
        if match is None:
            raise PermissionError

        return match.unread_count


class UnreadCount(BaseModel, UnreadCountJSONMixin, IUnreadCount):
    __tablename__ = 'unread_counts'

    _user_chat_match_id: Mapped[int] = mapped_column(ForeignKey('user_chat_matches.id', ondelete='CASCADE'),
                                                     name='user_chat_match_id', nullable=False)
    _value: Mapped[int] = mapped_column(Integer, name='value', default=0)

    _user_chat_match: Mapped['UserChatMatch'] = relationship(
        back_populates='_unread_count',
        uselist=False,
    )

    __table_args__ = (
        CheckConstraint('value >= 0'),
    )

    @property
    def value(self) -> int:
        return self._value

    def set(self, value: int) -> None:
        self._value = cast(Mapped[int], value)

    def increase(self) -> None:
        self._value += 1

    def decrease(self) -> None:
        self._value -= 1
        if self._value < 0:
            self._value = cast(Mapped[int], 0)


from db.lists import (  # noqa
    UserList,
    ChatList,
    MessageList,
)
from db.message_storage import MessageStorage  # noqa
