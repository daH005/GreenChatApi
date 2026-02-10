from collections import UserList as CustomList

from datetime import datetime
from os import PathLike
from pathlib import Path
from typing import Union, Self, Protocol

__all__ = (
    'IBaseModel',
    'IAuthToken',
    'IUser',
    'IChat',
    'IMessage',
    'IMessageStorage',
    'IMessageStorageFile',
    'IUserChatMatch',
    'IBaseList',
    'IUserList',
    'IChatList',
    'IMessageList',
)


class IBaseModel:
    _id: int

    @property
    def id(self) -> int:
        raise NotImplementedError

    @classmethod
    def by_id(cls, id_: int) -> Self:
        raise NotImplementedError


class IAuthToken(IBaseModel):

    _user_id: int
    _value: str
    _is_refresh: bool

    _user: 'IUser'

    @classmethod
    def create(cls, value: str,
               is_refresh: bool,
               user: 'IUser',
               ) -> Self:
        raise NotImplementedError

    @property
    def value(self) -> str:
        raise NotImplementedError

    @classmethod
    def exists(cls, value: str) -> bool:
        raise NotImplementedError

    @classmethod
    def by_value(cls, value: str) -> Self:
        raise NotImplementedError


class IUser(IBaseModel):

    _email: str
    _first_name: str
    _last_name: str

    _tokens: list['IAuthToken']
    _messages: list['IMessage']
    _user_chats_matches: list['IUserChatMatch']

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

    def chats(self, offset: int | None = None,
              size: int | None = None,
              ) -> 'IChatList':
        raise NotImplementedError

    def set_info(self, first_name: str | None = None,
                 last_name: str | None = None,
                 ) -> None:
        raise NotImplementedError


class IChat(IBaseModel):

    _name: str | None
    _is_group: bool

    _messages: list['IMessage']
    _user_chat_matches: list['IUserChatMatch']

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
                                  ) -> tuple[Self, list['IUserChatMatch']]:
        raise NotImplementedError

    @property
    def last_message(self) -> 'IMessage':
        raise NotImplementedError

    def messages(self, offset: int | None = None,
                 size: int | None = None,
                 ) -> 'IMessageList':
        raise NotImplementedError

    def unread_interlocutor_messages_up_to(self, message_id: int,
                                           user_id_to_ignore: int,
                                           ) -> 'IMessageList':
        raise NotImplementedError

    def interlocutor_messages_after_count(self, message_id: int,
                                          user_id_to_ignore: int,
                                          ) -> int:
        raise NotImplementedError

    def users(self) -> 'IUserList':
        raise NotImplementedError

    def check_user_access(self, user_id: int) -> None:
        raise NotImplementedError

    def interlocutor_of_user(self, user_id: int) -> 'IUser':
        raise NotImplementedError

    def all_interlocutors_of_user(self, user_id: int) -> 'IUserList':
        raise NotImplementedError

    def unread_count_of_user(self, user_id: int) -> int:
        raise NotImplementedError

    def last_seen_message_id_of_user(self, user_id: int) -> int:
        raise NotImplementedError

    def set_last_seen_message_id_of_user(self, user_id: int, message_id: int) -> None:
        raise NotImplementedError

    @classmethod
    def between_users(cls, first_user_id: int,
                      second_user_id: int,
                      ) -> 'IChat':
        raise NotImplementedError


class IMessage(IBaseModel):

    _user_id: int
    _chat_id: int
    _replied_message_id: int | None
    _text: str
    _creating_datetime: datetime
    _is_read: bool

    _user: 'IUser'
    _chat: 'IChat'
    _replied_message: Union['IMessage', None]
    _reply_message: Union['IMessage', None]
    _storage: 'IMessageStorage'

    @classmethod
    def create(cls, text: str,
               user: 'IUser',
               chat: 'IChat',
               replied_message: Union['IMessage', None] = None,
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
    def user(self) -> 'IUser':
        raise NotImplementedError

    @property
    def chat(self) -> 'IChat':
        raise NotImplementedError

    def get_storage(self) -> 'IMessageStorage':
        raise NotImplementedError

    def read(self) -> None:
        raise NotImplementedError

    def set_text(self, text: str) -> None:
        raise NotImplementedError

    def set_replied_message_id(self, replied_message_id: int | None) -> None:
        raise NotImplementedError


class IMessageStorage:
    _message: 'IMessage'

    @property
    def message(self) -> 'IMessage':
        raise NotImplementedError

    def exists(self) -> bool:
        raise NotImplementedError

    def update(self, files: list['IMessageStorageFile']) -> None:
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


class IMessageStorageFile(Protocol):
    filename: str

    def save(self, path: PathLike[str]) -> None:
        pass


class IUserChatMatch(IBaseModel):

    _user_id: int
    _chat_id: int
    _last_seen_message_id: int | None

    _user: 'IUser'
    _chat: 'IChat'

    @property
    def user(self) -> 'IUser':
        raise NotImplementedError

    @property
    def chat(self) -> 'IChat':
        raise NotImplementedError

    @property
    def last_seen_message_id(self) -> int:
        raise NotImplementedError

    @classmethod
    def chat_if_user_has_access(cls, user_id: int,
                                chat_id: int,
                                ) -> 'IChat':
        raise NotImplementedError

    @classmethod
    def users_of_chat(cls, chat_id: int) -> 'IUserList':
        raise NotImplementedError

    @classmethod
    def chats_of_user(cls, user_id: int,
                      offset: int | None = None,
                      size: int | None = None,
                      ) -> 'IChatList':
        raise NotImplementedError

    @classmethod
    def interlocutor_of_user_of_chat(cls, user_id: int,
                                     chat_id: int,
                                     ) -> 'IUser':
        raise NotImplementedError

    @classmethod
    def private_chat_between_users(cls, first_user_id: int,
                                   second_user_id: int,
                                   ) -> 'IChat':
        raise NotImplementedError

    @classmethod
    def all_interlocutors_of_all_chats_of_user(cls, user_id: int) -> 'IUserList':
        raise NotImplementedError

    @classmethod
    def last_seen_message_id_of_user(cls, user_id: int, chat_id: int) -> int:
        raise NotImplementedError

    @classmethod
    def set_last_seen_message_id_of_user(cls, user_id: int, chat_id: int, message_id: int) -> None:
        raise NotImplementedError


class IBaseList(CustomList[Union['IUser', 'IChat', 'IMessage']]):

    def ids(self) -> list[int]:
        raise NotImplementedError


class IUserList(IBaseList, CustomList['IUser']):
    pass


class IChatList(IBaseList, CustomList['IChat']):
    _user_id: int


class IMessageList(IBaseList, CustomList['IMessage']):
    pass
