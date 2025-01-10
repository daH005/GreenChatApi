from datetime import datetime
from pathlib import Path
from typing import Union, Self, Protocol
from os import PathLike

__all__ = (
    'BlacklistTokenI',
    'UserI',
    'ChatI',
    'ChatMessageI',
    'ChatMessageStorageI',
    'ChatMessageStorageFileI',
    'UserChatMatchI',
    'UnreadCountI',
    'UserListI',
    'ChatListI',
    'ChatMessageListI',
)


class BaseI:
    _id: int

    @property
    def id(self) -> int:
        raise NotImplementedError


class BlacklistTokenI:
    _jti: str

    @classmethod
    def create(cls, jti: str) -> Self:
        raise NotImplementedError

    @property
    def jti(self) -> str:
        raise NotImplementedError

    @classmethod
    def exists(cls, jti: str) -> bool:
        raise NotImplementedError


class UserI(BaseI):

    _email: str
    _first_name: str
    _last_name: str

    _chat_messages: list['ChatMessageI']
    _user_chats_matches: list['UserChatMatchI']

    @classmethod
    def create(cls, email: str) -> Self:
        raise NotImplementedError

    @property
    def email(self) -> str:
        raise NotImplementedError

    @property
    def first_name(self) -> str:
        raise NotImplementedError

    @property
    def last_name(self) -> str:
        raise NotImplementedError

    @classmethod
    def by_email(cls, email: str) -> Self:
        raise NotImplementedError

    @classmethod
    def email_is_already_taken(cls, email: str) -> bool:
        raise NotImplementedError

    @classmethod
    def _data_is_already_taken(cls, field_name: str,
                               value: str,
                               ) -> bool:
        raise NotImplementedError

    def chats(self) -> 'ChatListI':
        raise NotImplementedError

    def set_info(self, first_name: str | None = None,
                 last_name: str | None = None,
                 ) -> None:
        raise NotImplementedError


class ChatI(BaseI):

    _name: str | None
    _is_group: bool

    _messages: list['ChatMessageI']
    _user_chat_matches: list['UserChatMatchI']

    @classmethod
    def create(cls, name: str | None = None,
               is_group: bool = False,
               ) -> Self:
        raise NotImplementedError

    @property
    def name(self) -> str | None:
        raise NotImplementedError

    @property
    def is_group(self) -> bool:
        raise NotImplementedError

    @classmethod
    def new_with_all_dependencies(cls, user_ids: list[int],
                                  **kwargs,
                                  ) -> list[Union[Self, 'UserChatMatchI', 'UnreadCountI']]:
        raise NotImplementedError

    @property
    def last_message(self) -> 'ChatMessageI':
        raise NotImplementedError

    def messages(self) -> 'ChatMessageListI':
        raise NotImplementedError

    def users(self) -> 'UserListI':
        raise NotImplementedError

    def check_user_access(self, user_id: int) -> None:
        raise NotImplementedError

    def unread_messages_of_user(self, user_id: int) -> 'ChatMessageListI':
        raise NotImplementedError

    def interlocutor_of_user(self, user_id: int) -> 'UserI':
        raise NotImplementedError

    def unread_count_of_user(self, user_id: int) -> 'UnreadCountI':
        raise NotImplementedError


class ChatMessageI(BaseI):

    _user_id: int
    _chat_id: int
    _text: str
    _creating_datetime: datetime
    _is_read: bool

    _user: 'UserI'
    _chat: 'ChatI'
    _storage: Union['ChatMessageStorageI', None]

    @classmethod
    def create(cls, text: str,
               user: 'UserI',
               chat: 'ChatI',
               storage: Union['ChatMessageStorageI', None] = None,
               ) -> Self:
        raise NotImplementedError

    @property
    def text(self) -> str:
        raise NotImplementedError

    @property
    def creating_datetime(self) -> datetime:
        raise NotImplementedError

    @property
    def is_read(self) -> bool:
        raise NotImplementedError

    @property
    def user(self) -> 'UserI':
        raise NotImplementedError

    @property
    def chat(self) -> 'ChatI':
        raise NotImplementedError

    @property
    def storage(self) -> Union['ChatMessageStorageI', None]:
        raise NotImplementedError

    def read(self) -> None:
        raise NotImplementedError


class ChatMessageStorageI(BaseI):

    _chat_message_id: int | None
    _message: Union['ChatMessageI', None]

    @property
    def message(self) -> Union['ChatMessageI', None]:
        raise NotImplementedError

    def save(self, files: list['ChatMessageStorageFileI']) -> None:
        raise NotImplementedError

    def filenames(self) -> list[str]:
        raise NotImplementedError

    def full_path(self, filename: str) -> Path:
        raise NotImplementedError

    def path(self) -> Path:
        raise NotImplementedError

    @staticmethod
    def _encode_filename(filename: str) -> str:
        raise NotImplementedError

    @staticmethod
    def _decode_filename(filename: str) -> str:
        raise NotImplementedError


class ChatMessageStorageFileI(Protocol):
    filename: str

    def save(self, path: PathLike[str]) -> None:
        pass


class UserChatMatchI(BaseI):

    _user_id: int
    _chat_id: int

    _user: 'UserI'
    _chat: 'ChatI'
    _unread_count: 'UnreadCountI'

    @property
    def user(self) -> 'UserI':
        raise NotImplementedError

    @property
    def chat(self) -> 'ChatI':
        raise NotImplementedError

    @property
    def unread_count(self) -> 'UnreadCountI':
        raise NotImplementedError

    @classmethod
    def chat_if_user_has_access(cls, user_id: int,
                                chat_id: int,
                                ) -> 'ChatI':
        raise NotImplementedError

    @classmethod
    def users_of_chat(cls, chat_id: int) -> 'UserListI':
        raise NotImplementedError

    @classmethod
    def chats_of_user(cls, user_id: int) -> 'ChatListI':
        raise NotImplementedError

    @classmethod
    def interlocutor_of_user_of_chat(cls, user_id: int,
                                     chat_id: int,
                                     ) -> 'UserI':
        raise NotImplementedError

    @classmethod
    def private_chat_between_users(cls, first_user_id: int,
                                   second_user_id: int,
                                   ) -> 'ChatI':
        raise NotImplementedError

    @classmethod
    def all_interlocutors_of_user(cls, user_id: int) -> 'UserListI':
        raise NotImplementedError

    @classmethod
    def unread_count_of_user_of_chat(cls, user_id: int,
                                     chat_id: int,
                                     ) -> 'UnreadCountI':
        raise NotImplementedError


class UnreadCountI(BaseI):

    _user_chat_match_id: int
    _value: int

    _user_chat_match: 'UserChatMatchI'

    @property
    def value(self) -> int:
        raise NotImplementedError

    def set(self, value: int) -> None:
        raise NotImplementedError

    def increase(self) -> None:
        raise NotImplementedError

    def decrease(self) -> None:
        raise NotImplementedError


class UserListI(list['UserI']):
    pass


class ChatListI(list['ChatI']):
    _user_id: int


class ChatMessageListI(list['ChatMessageI']):
    pass
