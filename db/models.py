from os import listdir
from typing import Union, Self, Final
from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    desc,
)
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    Mapped,
    relationship,
)
from datetime import datetime
from pathlib import Path
from base64 import b64encode, b64decode
from shutil import rmtree

from config import MEDIA_FOLDER
from common.hinting import raises
from db.builder import db_builder
from db.i import (
    BlacklistTokenI,
    UserI,
    ChatI,
    MessageI,
    MessageStorageI,
    MessageStorageFileI,
    UserChatMatchI,
    UnreadCountI,
)
from db.json_mixins import (
    UserJSONMixin,
    ChatJSONMixin,
    MessageJSONMixin,
    UnreadCountJSONMixin,
)
from db.jwt_mixins import UserJWTMixin

__all__ = (
    'BaseModel',
    'BlacklistToken',
    'User',
    'Chat',
    'Message',
    'MessageStorage',
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


class BlacklistToken(BaseModel, BlacklistTokenI):
    __tablename__ = 'blacklist_tokens'

    _jti: Mapped[str] = mapped_column(String(500), name='jti', unique=True)

    @classmethod
    def create(cls, jti: str) -> Self:
        return cls(_jti=jti)

    @property
    def jti(self) -> str:
        return self._jti

    @classmethod
    def exists(cls, jti: str) -> bool:
        return db_builder.session.query(cls).filter(cls._jti == jti).first() is not None


class User(BaseModel, UserJSONMixin, UserJWTMixin, UserI):
    __tablename__ = 'users'

    _email: Mapped[str] = mapped_column(String(200), name='email', nullable=False, unique=True)
    _first_name: Mapped[str] = mapped_column(String(100), name='first_name', nullable=False, default='New')
    _last_name: Mapped[str] = mapped_column(String(100), name='last_name', nullable=False, default='User')

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

    @classmethod
    def email_is_already_taken(cls, email: str) -> bool:
        return cls._data_is_already_taken('_email', email)

    @classmethod
    def _data_is_already_taken(cls, field_name: str,
                               value: str,
                               ) -> bool:
        user: cls | None = db_builder.session.query(cls).filter(getattr(cls, field_name) == value).first()
        return user is not None

    def chats(self) -> 'ChatList':
        return UserChatMatch.chats_of_user(self.id)

    def set_info(self, first_name: str | None = None,
                 last_name: str | None = None,
                 ) -> None:
        if first_name is not None:
            self._first_name = first_name  # type: ignore
        if last_name is not None:
            self._last_name = last_name  # type: ignore


class Chat(BaseModel, ChatJSONMixin, ChatI):
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
                                  ) -> list[Union[Self, 'UserChatMatch', 'UnreadCount']]:
        objects: list[cls | UserChatMatch | UnreadCount] = []

        chat: cls = cls.create(**kwargs)
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
        return self._messages[0]  # type: ignore

    def messages(self) -> 'MessageList':
        return MessageList(self._messages)

    def users(self) -> 'UserList':
        return UserList(UserChatMatch.users_of_chat(self.id))

    @raises(PermissionError)
    def check_user_access(self, user_id: int) -> None:
        UserChatMatch.chat_if_user_has_access(user_id, self.id)

    def unread_messages_of_user(self, user_id: int) -> 'MessageList':
        messages = self._messages.filter(Message._is_read == False, Message._user_id != user_id).all()  # noqa
        return MessageList(messages)

    @raises(ValueError)
    def interlocutor_of_user(self, user_id: int) -> 'User':
        return UserChatMatch.interlocutor_of_user_of_chat(user_id, self.id)

    @raises(PermissionError)
    def unread_count_of_user(self, user_id: int) -> 'UnreadCount':
        return UserChatMatch.unread_count_of_user_of_chat(user_id, self.id)


class Message(BaseModel, MessageJSONMixin, MessageI):
    __tablename__ = 'messages'

    _user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), name='user_id', nullable=False)
    _chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id', ondelete='CASCADE'), name='chat_id', nullable=False)
    _text: Mapped[str] = mapped_column(Text, name='text', nullable=False)
    _creating_datetime: Mapped[datetime] = mapped_column(DATETIME(fsp=6), name='creating_datetime',
                                                         default=datetime.utcnow)
    _is_read: Mapped[bool] = mapped_column(Boolean, name='is_read', default=False)

    _user: Mapped['User'] = relationship(back_populates='_messages', uselist=False)
    _chat: Mapped['Chat'] = relationship(back_populates='_messages', uselist=False)
    _storage: Mapped[Union['MessageStorage', None]] = relationship(
        back_populates='_message',
        cascade='all, delete',
        uselist=False,
    )

    @classmethod
    def create(cls, text: str,
               user: 'User',
               chat: 'Chat',
               storage: Union['MessageStorage', None] = None,
               ) -> Self:
        return cls(_text=text, _user=user, _chat=chat, _storage=storage)

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
    def storage(self) -> Union['MessageStorage', None]:
        return self._storage

    def read(self) -> None:
        self._is_read = True  # type: ignore


class MessageStorage(BaseModel, MessageStorageI):
    __tablename__ = 'message_storages'
    _FILES_PATH: Final[Path] = MEDIA_FOLDER.joinpath('files')

    _message_id: Mapped[int | None] = mapped_column(ForeignKey('messages.id', ondelete='CASCADE'),
                                                         name='message_id')
    _message: Mapped[Union['Message', None]] = relationship(back_populates='_storage', uselist=False)

    @property
    def message(self) -> Union['Message', None]:
        return self._message

    def save(self, files: list['MessageStorageFileI']) -> None:
        file_folder_path: Path = self.path()
        if file_folder_path.exists():
            rmtree(file_folder_path)
        file_folder_path.mkdir()

        secured_filename: str
        for file in files:
            if not file.filename:
                continue

            secured_filename = self._encode_filename(file.filename)
            file.save(file_folder_path.joinpath(secured_filename))

    @raises(FileNotFoundError)
    def filenames(self) -> list[str]:
        filenames: list[str] = listdir(self.path())
        return [self._decode_filename(filename) for filename in filenames]

    @raises(FileNotFoundError)
    def full_path(self, filename: str) -> Path:
        filename: str = self._encode_filename(filename)
        path: Path = self.path().joinpath(filename)
        if not path.exists():
            raise FileNotFoundError
        return path

    def path(self) -> Path:
        return self._FILES_PATH.joinpath(str(self._id))

    @staticmethod
    def _encode_filename(filename: str) -> str:
        return b64encode(filename.encode()).decode()

    @staticmethod
    def _decode_filename(filename: str) -> str:
        return b64decode(filename).decode()


class UserChatMatch(BaseModel, UserChatMatchI):
    __tablename__ = 'user_chat_matches'

    _user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), name='user_id', nullable=False)
    _chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id', ondelete='CASCADE'), name='chat_id', nullable=False)

    _user: Mapped['User'] = relationship(back_populates='_user_chats_matches', uselist=False)
    _chat: Mapped['Chat'] = relationship(back_populates='_user_chat_matches', uselist=False)
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
        matches: list[cls] = db_builder.session.query(cls).filter(cls._chat_id == chat_id).all()  # type: ignore
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

        chats: list[Chat] = filtered_and_ordered_query.with_entities(Chat).all()  # type: ignore

        return ChatList(chats, user_id)

    @classmethod
    @raises(ValueError)
    def interlocutor_of_user_of_chat(cls, user_id: int,
                                     chat_id: int,
                                     ) -> 'User':
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
                                   ) -> 'Chat':
        chat_ids: list[int] = []

        matches: list[cls] = db_builder.session.query(cls).filter(  # type: ignore
            (cls._user_id == first_user_id) | (cls._user_id == second_user_id),
        ).all()
        for match in matches:
            if match.chat.is_group:
                continue
            if match._chat_id in chat_ids:
                return match.chat
            chat_ids.append(match._chat_id)

        raise ValueError

    @classmethod
    def all_interlocutors_of_user(cls, user_id: int) -> 'UserList':
        interlocutors: set[User] = set()  # type: ignore

        chats: ChatList = cls.chats_of_user(user_id)
        for chat in chats:
            users: UserList = cls.users_of_chat(chat.id)
            interlocutors.update(users)  # type: ignore

        self_user: User = db_builder.session.get(User, user_id)  # type: ignore
        if self_user in interlocutors:
            interlocutors.remove(self_user)  # type: ignore

        return UserList(interlocutors)  # type: ignore

    @classmethod
    @raises(PermissionError)
    def unread_count_of_user_of_chat(cls, user_id: int,
                                     chat_id: int,
                                     ) -> 'UnreadCount':
        match: cls | None = db_builder.session.query(cls).filter(cls._user_id == user_id,
                                                                 cls._chat_id == chat_id,
                                                                 ).first()  # type: ignore
        if match is None:
            raise PermissionError

        return match.unread_count


class UnreadCount(BaseModel, UnreadCountJSONMixin, UnreadCountI):
    __tablename__ = 'unread_counts'

    _user_chat_match_id: Mapped[int] = mapped_column(ForeignKey('user_chat_matches.id', ondelete='CASCADE'),
                                                     name='user_chat_match_id', nullable=False)
    _value: Mapped[int] = mapped_column(Integer, name='value', default=0)

    _user_chat_match: Mapped['UserChatMatch'] = relationship(back_populates='_unread_count', uselist=False)

    @property
    def value(self) -> int:
        return self._value

    def set(self, value: int) -> None:
        self._value = value  # type: ignore

    def increase(self) -> None:
        self._value += 1

    def decrease(self) -> None:
        self._value -= 1
        if self._value < 0:
            self._value = 0  # type: ignore


from db.lists import (  # noqa
    UserList,
    ChatList,
    MessageList,
)
