from datetime import datetime
from typing import Union, Self, cast

from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    func,
    Subquery,
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
from db.builders import db_sync_builder
from db.exceptions import (
    DBEntityNotFoundException,
    DBEntityIsForbiddenException,
)
from db.i import (
    IBaseModel,
    IAuthToken,
    IUser,
    IChat,
    IMessage,
    IUserChatMatch,
)
from db.json_mixins import (
    UserJSONMixin,
    ChatJSONMixin,
    MessageJSONMixin,
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
)


class BaseModel(DeclarativeBase, IBaseModel):
    _id: Mapped[int] = mapped_column(primary_key=True, name='id')

    @property
    def id(self) -> int:
        return self._id

    @classmethod
    @raises(DBEntityNotFoundException)
    def by_id(cls, id_: int) -> Self:
        obj: cls = cast(cls, db_sync_builder.session.get(cls, id_))
        if not obj:
            raise DBEntityNotFoundException

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
        return db_sync_builder.session.query(cls).filter(cls._value == value).first() is not None

    @classmethod
    @raises(DBEntityNotFoundException)
    def by_value(cls, value: str) -> Self:
        token: cls | None = db_sync_builder.session.query(cls).filter(cls._value == value).first()
        if token is None:
            raise DBEntityNotFoundException

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
    @raises(DBEntityNotFoundException)
    def by_email(cls, email: str) -> Self:
        user: cls | None = db_sync_builder.session.query(cls).filter(cls._email == email).first()
        if user is None:
            raise DBEntityNotFoundException

        return user

    def chats(self, offset: int | None = None,
              size: int | None = None,
              ) -> 'ChatList':
        return UserChatMatch.chats_of_user(self.id, offset, size)

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
        order_by='-Message._creating_datetime',
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
                                  ) -> tuple[Self, list['UserChatMatch']]:
        matches: list[UserChatMatch] = []
        chat: cls = cls.create(**kwargs)

        for user_id in user_ids:
            match: UserChatMatch = UserChatMatch(
                _user_id=user_id,
                _chat=chat,
            )
            matches.append(match)

        return chat, matches

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
        return MessageList(
            cast(Query[Message], self._messages).limit(size).offset(offset).all(),
        )

    def unread_interlocutor_messages_up_to(self, message_id: int,
                                           user_id: int,
                                           ) -> 'MessageList':
        return MessageList(
            cast(Query[Message], self._messages).filter(
                Message._id <= message_id,  # noqa
                Message._is_read == False,  # noqa
                Message._user_id != user_id,  # noqa
            ).all(),
        )

    def interlocutor_messages_after_count(self, message_id: int,
                                          user_id: int,
                                          ) -> int:
        return cast(Query[Message], self._messages).filter(
            Message._id > message_id,  # noqa
            Message._user_id != user_id,  # noqa
        ).count()

    def users(self) -> 'UserList':
        return UserList(UserChatMatch.users_of_chat(self.id))

    @raises(DBEntityIsForbiddenException)
    def check_user_access(self, user_id: int) -> None:
        UserChatMatch.chat_if_user_has_access(user_id, self.id)

    @raises(DBEntityNotFoundException)
    def interlocutor_of_user(self, user_id: int) -> 'User':
        return UserChatMatch.interlocutor_of_user_of_chat(user_id, self.id)

    def all_interlocutors_of_user(self, user_id: int) -> 'UserList':
        users: UserList = self.users()
        return UserList([user for user in users if user.id != user_id])

    @raises(DBEntityNotFoundException)
    def unread_count_of_user(self, user_id: int) -> int:
        last_seen_message_id: int = self.last_seen_message_id_of_user(user_id)
        return self.interlocutor_messages_after_count(last_seen_message_id, user_id)

    @raises(DBEntityNotFoundException)
    def last_seen_message_id_of_user(self, user_id: int) -> int:
        return UserChatMatch.last_seen_message_id_of_user(user_id, self.id)

    @raises(DBEntityNotFoundException)
    def set_last_seen_message_id_of_user(self, user_id: int, message_id: int) -> None:
        UserChatMatch.set_last_seen_message_id_of_user(user_id, self.id, message_id)

    @classmethod
    @raises(DBEntityNotFoundException)
    def between_users(cls, first_user_id: int,
                      second_user_id: int,
                      ) -> Self:
        return UserChatMatch.private_chat_between_users(first_user_id, second_user_id)


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

    def get_storage(self) -> 'MessageStorage':
        if not hasattr(self, '_storage'):
            self._storage = MessageStorage(self)
        return cast(MessageStorage, self._storage)

    def read(self) -> None:
        self._is_read = cast(Mapped[bool], True)

    def set_text(self, text: str) -> None:
        self._text = cast(Mapped[str], text)

    def set_replied_message_id(self, replied_message_id: int | None) -> None:
        self._replied_message_id = cast(Mapped[int], replied_message_id)


class UserChatMatch(BaseModel, IUserChatMatch):
    __tablename__ = 'user_chat_matches'

    _user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), name='user_id', nullable=False)
    _chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id', ondelete='CASCADE'), name='chat_id', nullable=False)
    # This is not full-mapped message ID, this is rather a position of user reading.
    _last_seen_message_id: Mapped[int] = mapped_column(Integer, name='last_seen_message_id', default=-1)

    _user: Mapped['User'] = relationship(
        back_populates='_user_chats_matches',
        uselist=False,
    )
    _chat: Mapped['Chat'] = relationship(
        back_populates='_user_chat_matches',
        uselist=False,
    )

    @property
    def user(self) -> User:
        return self._user

    @property
    def chat(self) -> Chat:
        return self._chat

    @property
    def last_seen_message_id(self) -> int:
        return self._last_seen_message_id

    @classmethod
    @raises(DBEntityIsForbiddenException)
    def chat_if_user_has_access(cls, user_id: int,
                                chat_id: int,
                                ) -> 'Chat':
        match: cls | None = db_sync_builder.session.query(cls).filter(
            cls._user_id == user_id, cls._chat_id == chat_id
        ).first()
        if match is None:
            raise DBEntityIsForbiddenException

        return match.chat

    @classmethod
    def users_of_chat(cls, chat_id: int) -> 'UserList':
        query: Query[cls] = db_sync_builder.session.query(
            cls, User,
        ).join(
            User, User._id == cls._user_id,
        ).filter(
            cls._chat_id == chat_id,
        ).with_entities(User)

        return UserList(
            cast(list[User], query.all()),
        )

    @classmethod
    def chats_of_user(cls, user_id: int,
                      offset: int | None = None,
                      size: int | None = None,
                      ) -> 'ChatList':
        subquery: Subquery = db_sync_builder.session.query(
            cls._chat_id,
            Message._creating_datetime,  # noqa
            func.row_number().over(
                partition_by=cls._chat_id,
                order_by=Message._creating_datetime.desc(),  # noqa
            ).label('rn'),
        ).outerjoin(
            Message, cls._chat_id == Message._chat_id,  # noqa
        ).filter(
            cls._user_id == user_id,
        ).subquery()

        query: Query[Chat] = db_sync_builder.session.query(subquery).join(
            Chat, Chat._id == subquery.c._chat_id,  # noqa
        ).filter(
            subquery.c.rn == 1,
        ).order_by(
            subquery.c._creating_datetime.desc(),  # noqa
        ).with_entities(Chat)

        return ChatList(
            cast(list[Chat], query.limit(size).offset(offset).all()),
            user_id,
        )

    @classmethod
    @raises(DBEntityNotFoundException)
    def interlocutor_of_user_of_chat(cls, user_id: int,
                                     chat_id: int,
                                     ) -> 'User':
        interlocutor_match: cls | None = db_sync_builder.session.query(cls).filter(
            cls._user_id != user_id,
            cls._chat_id == chat_id,
        ).first()
        if interlocutor_match is None:
            raise DBEntityNotFoundException

        return interlocutor_match.user

    @classmethod
    @raises(DBEntityNotFoundException)
    def private_chat_between_users(cls, first_user_id: int,
                                   second_user_id: int,
                                   ) -> 'Chat':
        query: Query[cls] = db_sync_builder.session.query(
            cls, Chat,
        ).join(
            Chat, Chat._id == cls._chat_id,
        ).filter(
            Chat._is_group == False,  # noqa
            cls._user_id.in_([
                first_user_id,
                second_user_id,
            ]),
        ).group_by(cls._chat_id).having(
            func.count(cls._user_id) == 2,
        ).with_entities(Chat)

        chat: Chat | None = cast(Chat | None, query.first())
        if chat is None:
            raise DBEntityNotFoundException

        return chat

    @classmethod
    def all_interlocutors_of_all_chats_of_user(cls, user_id: int) -> 'UserList':
        chat_ids: list[int] = cast(
            list[int],
            [row[0] for row in db_sync_builder.session.query(cls._chat_id).filter(cls._user_id == user_id).all()],
        )
        query: Query[cls] = db_sync_builder.session.query(
            cls, User,
        ).join(
            User, User._id == cls._user_id,
        ).filter(
            cls._user_id != user_id,
            cls._chat_id.in_(chat_ids),
        ).with_entities(User)

        return UserList(
            cast(list[User], query.all()),
        )

    @classmethod
    @raises(DBEntityNotFoundException)
    def last_seen_message_id_of_user(cls, user_id: int, chat_id: int) -> int:
        match: cls | None = db_sync_builder.session.query(cls).filter(
            cls._user_id == user_id,
            cls._chat_id == chat_id,
        ).first()
        if match is None:
            raise DBEntityNotFoundException

        return match._last_seen_message_id

    @classmethod
    @raises(DBEntityNotFoundException)
    def set_last_seen_message_id_of_user(cls, user_id: int, chat_id: int, message_id: int) -> None:
        match: cls | None = db_sync_builder.session.query(cls).filter(
            cls._user_id == user_id,
            cls._chat_id == chat_id,
        ).first()
        if match is None:
            raise DBEntityNotFoundException

        message: Message = Message.by_id(message_id)
        if message.chat.id != chat_id:
            raise DBEntityNotFoundException
        match._last_seen_message_id = message_id


from db.lists import (  # noqa
    UserList,
    ChatList,
    MessageList,
)
from db.message_storage import MessageStorage  # noqa
