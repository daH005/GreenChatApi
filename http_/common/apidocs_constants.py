__all__ = (
    'USER_EMAIL_CODE_SEND_SPECS',
    'USER_EMAIL_CODE_CHECK_SPECS',
    'USER_LOGIN_SPECS',
    'USER_LOGOUT_SPECS',
    'USER_REFRESH_ACCESS_SPECS',
    'USER_SPECS',
    'USER_EDIT_SPECS',
    'USER_AVATAR_SPECS',
    'USER_AVATAR_EDIT_SPECS',
    'USER_BACKGROUND_SPECS',
    'USER_BACKGROUND_EDIT_SPECS',
    'USER_CHATS_SPECS',

    'CHAT_SPECS',
    'CHAT_BY_INTERLOCUTOR_SPECS',
    'CHAT_NEW_SPECS',
    'CHAT_TYPING_SPECS',
    'CHAT_UNREAD_COUNT_SPECS',
    'CHAT_MESSAGES_SPECS',

    'MESSAGE_SPECS',
    'MESSAGE_NEW_SPECS',
    'MESSAGE_EDIT_SPECS',
    'MESSAGE_DELETE_SPECS',
    'MESSAGE_READ_SPECS',
    'MESSAGE_FILES_UPDATE_SPECS',
    'MESSAGE_FILES_DELETE_SPECS',
    'MESSAGE_FILES_NAMES_SPECS',
    'MESSAGE_FILES_GET_SPECS',
)


_USER_TAGS = ['User']
_CHAT_TAGS = ['Chat']
_MESSAGE_TAGS = ['Message']

_SIMPLE_REQUEST_RESPONSES = {
    200: {},
    201: {},
    202: {},
    400: {},
    401: {},
    403: {},
    404: {},
    409: {},
    413: {},
}

_ACCESS_TOKEN_COOKIE = {
    'name': 'access_token_cookie',
    'in': 'cookie',
    'required': True,
    'type': 'string',
}

_REFRESH_TOKEN_COOKIE = {
    'name': 'refresh_token_cookie',
    'in': 'cookie',
    'required': True,
    'type': 'string',
}

_CSRF_TOKEN_HEADER = {
    'name': 'X-CSRF-TOKEN',
    'in': 'header',
    'required': True,
    'type': 'string',
}

_USER_SCHEMA = {
    'type': 'object',
    'required': [
        'id',
        'firstName',
        'lastName',
    ],
    'properties': {
        'id': {
            'type': 'integer',
        },
        'firstName': {
            'type': 'string',
        },
        'lastName': {
            'type': 'string',
        },
        'isOnline': {
            'type': 'boolean',
        },
        'email': {
            'type': ['null', 'string'],
        },
    },
}

_MESSAGE_SCHEMA = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'integer',
        },
        'chatId': {
            'type': 'integer',
        },
        'userId': {
            'type': 'integer',
        },
        'text': {
            'type': 'string',
        },
        'creatingDatetime': {
            'type': 'string',
        },
        'isRead': {
            'type': 'boolean',
        },
        'hasFiles': {
            'type': 'boolean',
        },
        'repliedMessage': {
            'type': {
                'id': {'type': 'integer'},
                'userId': {'type': 'integer'},
                'text': {'type': 'string'},
            },
        },
    },
}

_CHAT_SCHEMA = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'integer',
        },
        'interlocutorId': {
            'type': ['null', 'integer'],
        },
        'name': {
            'type': ['null', 'string'],
        },
        'isGroup': {
            'type': 'boolean',
        },
        'unreadCount': {
            'type': 'integer',
        },
        'userIds': {
            'type': 'array',
            'items': {'type': 'integer'},
        },
        'lastMessage': _MESSAGE_SCHEMA,
    },
}

USER_EMAIL_CODE_SEND_SPECS = {
    'tags': _USER_TAGS,
    'parameters': [
        _CSRF_TOKEN_HEADER,
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                    },
                },
            },
        },
    ],
    'responses': {
        202: _SIMPLE_REQUEST_RESPONSES[202],
        400: _SIMPLE_REQUEST_RESPONSES[400],
        409: _SIMPLE_REQUEST_RESPONSES[409],
    },
}

USER_EMAIL_CODE_CHECK_SPECS = {
    'tags': _USER_TAGS,
    'parameters': [
        {
            'name': 'email',
            'in': 'query',
            'type': 'string',
            'required': True,
        },
        {
            'name': 'code',
            'in': 'query',
            'type': 'integer',
            'required': True,
        },
    ],
    'responses': {
        200: {
            'schema': {
                'type': 'object',
                'properties': {
                    'isThat': {
                        'type': 'boolean',
                    }
                }
            }
        },
        400: _SIMPLE_REQUEST_RESPONSES[400],
    },
}

USER_LOGIN_SPECS = {
    'tags': _USER_TAGS,
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                    },
                    'code': {
                        'type': 'integer',
                        'example': 9999,
                    },
                },
            },
        },
    ],
    'responses': {
        200: _SIMPLE_REQUEST_RESPONSES[200],
        201: _SIMPLE_REQUEST_RESPONSES[201],
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
    },
}

USER_LOGOUT_SPECS = {
    'tags': _USER_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        _CSRF_TOKEN_HEADER,
    ],
    'responses': {
        200: _SIMPLE_REQUEST_RESPONSES[200],
        401: _SIMPLE_REQUEST_RESPONSES[401],
    },
}

USER_REFRESH_ACCESS_SPECS = {
    'tags': _USER_TAGS,
    'parameters': [
        _REFRESH_TOKEN_COOKIE,
        _CSRF_TOKEN_HEADER,
    ],
    'responses': {
        200: _SIMPLE_REQUEST_RESPONSES[200],
        401: _SIMPLE_REQUEST_RESPONSES[401],
    },
}

USER_SPECS = {
    'tags': _USER_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        {
            'name': 'userId',
            'in': 'query',
            'type': 'integer',
            'required': False,
        }
    ],
    'responses': {
        200: {
            'schema': _USER_SCHEMA,
        },
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        404: _SIMPLE_REQUEST_RESPONSES[404],
    }
}

USER_EDIT_SPECS = {
    'tags': _USER_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        _CSRF_TOKEN_HEADER,
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'firstName': {
                        'type': 'string',
                    },
                    'lastName': {
                        'type': 'string',
                    },
                },
            },
        },
    ],
    'responses': {
        200: _SIMPLE_REQUEST_RESPONSES[200],
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
    }
}

USER_AVATAR_SPECS = {
    'tags': _USER_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        {
            'name': 'userId',
            'in': 'query',
            'type': 'integer',
            'required': True,
        }
    ],
    'responses': {
        200: {
            'description': 'Image file bytes',
        },
    }
}

USER_AVATAR_EDIT_SPECS = {
    'tags': _USER_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        _CSRF_TOKEN_HEADER,
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'type': 'string',
            'format': 'byte',
            'description': 'Image file'
        },
    ],
    'responses': {
        200: _SIMPLE_REQUEST_RESPONSES[200],
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
    }
}

USER_BACKGROUND_SPECS = {
    'tags': _USER_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
    ],
    'responses': {
        200: {
            'description': 'Image file bytes',
        },
    }
}

USER_BACKGROUND_EDIT_SPECS = {
    'tags': _USER_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        _CSRF_TOKEN_HEADER,
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'type': 'string',
            'format': 'byte',
            'description': 'Image file'
        },
    ],
    'responses': {
        200: _SIMPLE_REQUEST_RESPONSES[200],
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
    }
}

USER_CHATS_SPECS = {
    'tags': _USER_TAGS,
    'description': 'Chats sorted by "creatingDatetime" of "lastMessage" in descending order.',
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
    ],
    'responses': {
        200: {
            'schema': {
                'type': 'array',
                'items': _CHAT_SCHEMA,
            },
        },
        401: _SIMPLE_REQUEST_RESPONSES[401],
    }
}

CHAT_SPECS = {
    'tags': _CHAT_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        {
            'name': 'chatId',
            'in': 'query',
            'type': 'integer',
            'required': True,
        }
    ],
    'responses': {
        200: {
            'schema': _CHAT_SCHEMA
        },
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        403: _SIMPLE_REQUEST_RESPONSES[403],
        404: _SIMPLE_REQUEST_RESPONSES[404],
    }
}

CHAT_BY_INTERLOCUTOR_SPECS = {
    'tags': _CHAT_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        {
            'name': 'interlocutorId',
            'in': 'query',
            'type': 'integer',
            'required': True,
        }
    ],
    'responses': {
        200: {
            'schema': _CHAT_SCHEMA
        },
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        404: _SIMPLE_REQUEST_RESPONSES[404],
    }
}

CHAT_NEW_SPECS = {
    'tags': _CHAT_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        _CSRF_TOKEN_HEADER,
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'userIds': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                    }
                },
            },
        }
    ],
    'responses': {
        201: _SIMPLE_REQUEST_RESPONSES[201],
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        409: _SIMPLE_REQUEST_RESPONSES[409],
    }
}

CHAT_TYPING_SPECS = {
    'tags': _CHAT_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        _CSRF_TOKEN_HEADER,
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'chatId': {
                        'type': 'integer',
                    }
                },
            },
        }
    ],
    'responses': {
        200: _SIMPLE_REQUEST_RESPONSES[200],
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        403: _SIMPLE_REQUEST_RESPONSES[403],
        404: _SIMPLE_REQUEST_RESPONSES[404],
    }
}

CHAT_UNREAD_COUNT_SPECS = {
    'tags': _CHAT_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        {
            'name': 'chatId',
            'in': 'query',
            'type': 'integer',
            'required': True,
        }
    ],
    'responses': {
        200: {
            'schema': {
                'type': 'object',
                'properties': {
                    'unreadCount': {'type': 'integer'}
                }
            }
        },
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        403: _SIMPLE_REQUEST_RESPONSES[403],
        404: _SIMPLE_REQUEST_RESPONSES[404],
    }
}

CHAT_MESSAGES_SPECS = {
    'tags': _CHAT_TAGS,
    'description': 'Messages sorted by "creatingDatetime" in descending order.',
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        {
            'name': 'chatId',
            'in': 'query',
            'type': 'integer',
            'required': True,
        },
        {
            'name': 'offset',
            'in': 'query',
            'type': 'integer',
            'required': False,
        }
    ],
    'responses': {
        200: {
            'schema': {
                'type': 'array',
                'items': _MESSAGE_SCHEMA,
            }
        },
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        403: _SIMPLE_REQUEST_RESPONSES[403],
        404: _SIMPLE_REQUEST_RESPONSES[404],
    }
}

MESSAGE_SPECS = {
    'tags': _MESSAGE_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        {
            'name': 'messageId',
            'in': 'query',
            'type': 'integer',
            'required': True,
        }
    ],
    'responses': {
        200: {
            'schema': _MESSAGE_SCHEMA,
        },
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        403: _SIMPLE_REQUEST_RESPONSES[403],
        404: _SIMPLE_REQUEST_RESPONSES[404],
    }
}

MESSAGE_NEW_SPECS = {
    'tags': _MESSAGE_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        _CSRF_TOKEN_HEADER,
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'chatId': {
                        'type': 'integer',
                    },
                    'text': {
                        'type': 'string',
                    },
                },
            },
        }
    ],
    'responses': {
        201: _SIMPLE_REQUEST_RESPONSES[201],
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        403: _SIMPLE_REQUEST_RESPONSES[403],
        404: _SIMPLE_REQUEST_RESPONSES[404],
    }
}

MESSAGE_EDIT_SPECS = {
    'tags': _MESSAGE_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        _CSRF_TOKEN_HEADER,
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'messageId': {
                        'type': 'integer',
                    },
                    'text': {
                        'type': 'string',
                    },
                },
            },
        }
    ],
    'responses': {
        200: _SIMPLE_REQUEST_RESPONSES[200],
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        403: _SIMPLE_REQUEST_RESPONSES[403],
        404: _SIMPLE_REQUEST_RESPONSES[404],
    }
}

MESSAGE_DELETE_SPECS = {
    'tags': _MESSAGE_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        _CSRF_TOKEN_HEADER,
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'messageId': {
                        'type': 'integer',
                    },
                },
            },
        }
    ],
    'responses': {
        200: _SIMPLE_REQUEST_RESPONSES[200],
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        403: _SIMPLE_REQUEST_RESPONSES[403],
        404: _SIMPLE_REQUEST_RESPONSES[404],
    }
}

MESSAGE_READ_SPECS = {
    'tags': _MESSAGE_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        _CSRF_TOKEN_HEADER,
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'messageId': {
                        'type': 'integer',
                    },
                },
            },
        }
    ],
    'responses': {
        200: _SIMPLE_REQUEST_RESPONSES[200],
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        403: _SIMPLE_REQUEST_RESPONSES[403],
        404: _SIMPLE_REQUEST_RESPONSES[404],
    }
}

MESSAGE_FILES_UPDATE_SPECS = {
    'tags': _MESSAGE_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        _CSRF_TOKEN_HEADER,
        {
            'name': 'messageId',
            'in': 'query',
            'type': 'integer',
            'required': True,
        },
        {
            'name': 'files',
            'in': 'body',
            'schema': {
                'type': 'file',
            },
            'required': True,
        },
    ],
    'responses': {
        201: _SIMPLE_REQUEST_RESPONSES[201],
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        403: _SIMPLE_REQUEST_RESPONSES[403],
        404: _SIMPLE_REQUEST_RESPONSES[404],
        413: _SIMPLE_REQUEST_RESPONSES[413],
    },
}

MESSAGE_FILES_DELETE_SPECS = {
    'tags': _MESSAGE_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        _CSRF_TOKEN_HEADER,
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'messageId': {
                        'type': 'integer',
                    },
                    'filenames': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                },
            },
        }
    ],
    'responses': {
        200: _SIMPLE_REQUEST_RESPONSES[200],
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        403: _SIMPLE_REQUEST_RESPONSES[403],
        404: _SIMPLE_REQUEST_RESPONSES[404],
    },
}

MESSAGE_FILES_NAMES_SPECS = {
    'tags': _MESSAGE_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        {
            'name': 'messageId',
            'in': 'query',
            'type': 'integer',
            'required': True,
        },
    ],
    'responses': {
        200: {
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'string',
                }
            }
        },
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        403: _SIMPLE_REQUEST_RESPONSES[403],
        404: _SIMPLE_REQUEST_RESPONSES[404],
    },
}

MESSAGE_FILES_GET_SPECS = {
    'tags': _MESSAGE_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        {
            'name': 'messageId',
            'in': 'query',
            'type': 'integer',
            'required': True,
        },
        {
            'name': 'filename',
            'in': 'query',
            'type': 'string',
            'required': True,
        },
    ],
    'responses': {
        200: {
            'schema': {
                'type': 'file',
            }
        },
        400: _SIMPLE_REQUEST_RESPONSES[400],
        401: _SIMPLE_REQUEST_RESPONSES[401],
        403: _SIMPLE_REQUEST_RESPONSES[403],
        404: _SIMPLE_REQUEST_RESPONSES[404],
    },
}
