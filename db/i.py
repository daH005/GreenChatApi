from datetime import datetime
from os import PathLike
from pathlib import Path
from typing import Union, Self, Protocol

__all__ = (
    'BaseI',
    'BlacklistTokenI',
    'UserI',
    'ChatI',
    'MessageI',
    'MessageStorageI',
    'MessageStorageFileI',
    'UserChatMatchI',
    'UnreadCountI',
    'UserListI',
    'ChatListI',
    'MessageListI',
)


class BaseI:
    _id: int

    @property
    def id(self) -> int:
        raise NotImplementedError

    @classmethod
    def by_id(cls, id_: int) -> Self:
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

    _messages: list['MessageI']
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

    def chats(self) -> 'ChatListI':
        raise NotImplementedError

    def set_info(self, first_name: str | None = None,
                 last_name: str | None = None,
                 ) -> None:
        raise NotImplementedError


class ChatI(BaseI):

    _name: str | None
    _is_group: bool

    _messages: list['MessageI']
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
                                  ) -> tuple[Self, list['UserChatMatchI', 'UnreadCountI']]:
        raise NotImplementedError

    @property
    def last_message(self) -> 'MessageI':
        raise NotImplementedError

    def messages(self, offset: int | None = None,
                 size: int | None = None,
                 ) -> 'MessageListI':
        raise NotImplementedError

    def unread_messages_up_to(self, message_id: int) -> 'MessageListI':
        raise NotImplementedError

    def interlocutor_messages_after_count(self, message_id: int,
                                          user_id: int,
                                          ) -> int:
        raise NotImplementedError

    def users(self) -> 'UserListI':
        raise NotImplementedError

    def check_user_access(self, user_id: int) -> None:
        raise NotImplementedError

    def interlocutor_of_user(self, user_id: int) -> 'UserI':
        raise NotImplementedError

    def unread_count_of_user(self, user_id: int) -> 'UnreadCountI':
        raise NotImplementedError


class MessageI(BaseI):

    _user_id: int
    _chat_id: int
    _replied_message_id: int | None
    _text: str
    _creating_datetime: datetime
    _is_read: bool

    _user: 'UserI'
    _chat: 'ChatI'
    _replied_message: Union['MessageI', None]
    _reply_message: Union['MessageI', None]
    _storage: 'MessageStorageI'

    @classmethod
    def create(cls, text: str,
               user: 'UserI',
               chat: 'ChatI',
               replied_message: Union['MessageI', None] = None,
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
    def storage(self) -> 'MessageStorageI':
        raise NotImplementedError

    def read(self) -> None:
        raise NotImplementedError

    def set_text(self, text: str) -> None:
        raise NotImplementedError

    def set_replied_message(self, replied_message_id: int | None) -> None:
        raise NotImplementedError


class MessageStorageI:
    _message: 'MessageI'

    @property
    def message(self) -> 'MessageI':
        raise NotImplementedError

    def exists(self) -> bool:
        raise NotImplementedError

    def update(self, files: list['MessageStorageFileI']) -> None:
        raise NotImplementedError

    def delete(self, filenames: list[str]) -> None:
        raise NotImplementedError

    def delete_all(self) -> None:
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


class MessageStorageFileI(Protocol):
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


class BaseListI(list[Union['UserI', 'ChatI', 'MessageI']]):

    def ids(self) -> list[int]:
        raise NotImplementedError


class UserListI(BaseListI, list['UserI']):
    pass


class ChatListI(BaseListI, list['ChatI']):
    _user_id: int


class MessageListI(BaseListI, list['MessageI']):
    pass
