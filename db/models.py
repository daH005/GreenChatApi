from __future__ import annotations
from sqlalchemy import (
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
    Session,
)
from datetime import datetime
# from typing import Iterable
from pathlib import Path

from api.db.json_ import (
    ChatMessageJSONDict,
    ChatJSONDict,
    make_json_chat_message_dict,
    make_json_chat_dict,
)

__all__ = (
    'session',
    'User',
    'Chat',
    'UserChat',
    'ChatMessage',
)

# FixMe: Думаю, перейдём на postgres. Или mysql (не работал на нём ещё).
#  URL перенести в конфиг!
path: Path = Path(__file__).resolve().parent
# Подключаемся к БД и создаём сессию (не в универе).
engine: Engine = create_engine('sqlite:///' + str(path.joinpath('db.db')))
session: Session = Session(bind=engine)
# Создаём базовый класс моделей.
BaseModel = declarative_base()


class User(BaseModel):
    """Модель пользователя, имеющего возможность общаться в чатах."""

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False)
    password = Column(String(255), nullable=False)

    @classmethod
    def auth(cls, email: str,
             password: str,
             ) -> User:
        """Возвращает пользователя с указанными `email` и `password`.
        Если пользователя с такими данными не существует, то вызывает `PermissionError`.
        """
        found_user: User | None = session.query(cls).filter(cls.email == email, cls.password == password).first()
        if found_user:
            return found_user
        raise PermissionError


class Chat(BaseModel):
    """Чат. Доступ к нему имеют не все пользователи, он обеспечивается через модель `UserChat`
    со связью 'многие-ко-многим'.
    """

    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    messages = relationship('ChatMessage', backref='chat')

    def to_json_dict(self) -> ChatJSONDict:
        """Формирует словарь данных с ключами в стиле lowerCamelCase."""
        return make_json_chat_dict([message.to_json_dict() for message in self.messages])


class ChatMessage(BaseModel):
    """Рядовое сообщение, относящееся к конкретному чату."""

    __tablename__ = 'chats_messages'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    chat_id = Column(Integer, ForeignKey('chats.id'))
    user = relationship('User', backref='chat_message', uselist=False)
    text = Column(Text, nullable=False)
    creating_datetime = Column(DateTime, default=datetime.now)

    def to_json_dict(self) -> ChatMessageJSONDict:
        """Формирует словарь данных с ключами в стиле lowerCamelCase."""
        return make_json_chat_message_dict(
            user_id=self.user_id,  # type: ignore
            chat_id=self.chat_id,  # type: ignore
            first_name=self.user.first_name,
            last_name=self.user.last_name,
            text=self.text,  # type: ignore
            creating_datetime=self.creating_datetime.isoformat(),
        )


class UserChat(BaseModel):
    """Модель-посредник, реализующая отношение 'многие-ко-многим' и
    определяющая доступ к чатам только для тех пользователей, которые в них состоят.
    """

    __tablename__ = 'users_chats'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    chat_id = Column(Integer, ForeignKey('chats.id'))
    user = relationship('User', backref='user_chat', uselist=False)
    chat = relationship('Chat', backref='user_chat', uselist=False)

    @classmethod
    def chat_if_user_has_access(cls, user_id: int,
                                chat_id: int,
                                ) -> Chat:
        """Возвращает чат, если пользователь в нём состоит.
        Иначе - вызывает `PermissionError`.
        """
        result: UserChat | None = session.query(cls).filter(
            cls.user_id == user_id, cls.chat_id == chat_id
        ).first()
        if result is not None:
            return result.chat
        raise PermissionError

    @classmethod
    def users_in_chat(cls, chat_id: int) -> list[User]:
        """Возвращает список пользователей, состоящих в указанном чате."""
        results = session.query(cls).filter(
            cls.chat_id == chat_id,
        ).all()
        return [result.user for result in results]


# Создаём таблицы в БД.
# Повторный запуск программы не обнуляет данные (даже в случае с sqlite).
# FixMe: Подумать над миграциями (Alembic).
BaseModel.metadata.create_all(engine)

if __name__ == '__main__':
    pass
    # FixMe: Потом удалить тестовые данные.
    # danil = User(
    #     first_name='Данил',
    #     last_name='Шевелёв',
    #     email='danil.shevelev.2004@mail.ru',
    #     password='901239-18fsdgd0sf7g===23421341',  # noqa
    # )
    # danila = User(
    #     first_name='Данила',
    #     last_name='Крохалев',
    #     email='skeletonik.2004@mail.ru',
    #     password='пароль',
    # )
    # ivan = User(
    #     first_name='Иван',
    #     last_name='Шветов',
    #     email='ivan.shvetov.2003@mail.ru',
    #     password='12380493580348gfdg0d-345123--2---'  # noqa
    # )
    # session.add_all([danil, danila, ivan])
    # session.commit()
    #
    # first_chat = Chat()
    # second_chat = Chat()
    # third_chat = Chat()
    # session.add_all([first_chat, second_chat, third_chat])
    # session.commit()
    #
    # session.add(UserChat(
    #     user_id=danil.id,
    #     chat_id=first_chat.id,
    # ))
    # session.add(UserChat(
    #     user_id=danila.id,
    #     chat_id=first_chat.id,
    # ))
    # session.commit()
    #
    # session.add(ChatMessage(
    #     user_id=danil.id,
    #     chat_id=first_chat.id,
    #     text='Hello!',
    # ))
    # session.add(ChatMessage(
    #     user_id=danil.id,
    #     chat_id=first_chat.id,
    #     text='How are you?',
    # ))
    # session.add(ChatMessage(
    #     user_id=danila.id,
    #     chat_id=first_chat.id,
    #     text='Hi! I\'m fine.',
    # ))
    # session.commit()
