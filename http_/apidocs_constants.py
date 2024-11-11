__all__ = (
    'EMAIL_CHECK_SPECS',
    'LOGIN_SPECS',
    'REFRESH_ACCESS_SPECS',
    'USER_INFO_SPECS',
    'USER_AVATAR_SPECS',
    'USER_BACKGROUND_SPECS',
    'USER_INFO_EDIT_SPECS',
    'USER_AVATAR_EDIT_SPECS',
    'USER_BACKGROUND_EDIT_SPECS',
    'USER_CHATS_SPECS',
    'CODE_SEND_SPECS',
    'CODE_CHECK_SPECS',
    'CHAT_HISTORY_SPECS',
    'CHAT_MESSAGES_FILES_SAVE_SPECS',
    'CHAT_MESSAGES_FILES_NAMES_SPECS',
    'CHAT_MESSAGES_FILES_GET_SPECS',
)


def _make_simple_request_response(status_code: int) -> dict:
    return {
        'schema': {
            'type': 'object',
            'properties': {
                'status': {'type': 'integer', 'example': status_code}
            },
        }
    }


_USER_TAGS = ['User']
_CHAT_TAGS = ['Chat']

_SIMPLE_REQUEST_RESPONSES = {
    200: _make_simple_request_response(200),
    201: _make_simple_request_response(201),
    400: _make_simple_request_response(400),
    403: _make_simple_request_response(403),
    404: _make_simple_request_response(404),
    409: _make_simple_request_response(409),
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

_USER_INFO_SCHEMA = {
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
        'email': {
            'type': 'string',
        },
    },
}

_CHAT_MESSAGE_SCHEMA = {
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
    },
}

EMAIL_CHECK_SPECS = {
    'tags': _USER_TAGS,
    'parameters': [
        {
            'name': 'email',
            'in': 'query',
            'type': 'string',
            'required': True,
        },
    ],
    'responses': {
        200: {
            'schema': {
                'type': 'object',
                'properties': {
                    'isAlreadyTaken': {
                        'type': 'boolean',
                    },
                },
            },
        },
        400: _SIMPLE_REQUEST_RESPONSES[400],
    },
}

LOGIN_SPECS = {
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
    },
}

REFRESH_ACCESS_SPECS = {
    'tags': _USER_TAGS,
    'parameters': [
        _REFRESH_TOKEN_COOKIE,
        _CSRF_TOKEN_HEADER,
    ],
    'responses': {
        200: _SIMPLE_REQUEST_RESPONSES[200],
    },
}

USER_INFO_SPECS = {
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
            'schema': _USER_INFO_SCHEMA,
        },
        400: _SIMPLE_REQUEST_RESPONSES[400],
        404: _SIMPLE_REQUEST_RESPONSES[404],
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
        400: _SIMPLE_REQUEST_RESPONSES[400],
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
        400: _SIMPLE_REQUEST_RESPONSES[400],
    }
}

USER_INFO_EDIT_SPECS = {
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
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer',
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
                    'usersIds': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                    },
                    'lastMessage': _CHAT_MESSAGE_SCHEMA,
                },
            }
        },
    }
}

CODE_SEND_SPECS = {
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
        200: _SIMPLE_REQUEST_RESPONSES[200],
        400: _SIMPLE_REQUEST_RESPONSES[400],
        409: _SIMPLE_REQUEST_RESPONSES[409],
    },
}

CODE_CHECK_SPECS = {
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
                    'codeIsValid': {
                        'type': 'boolean',
                    }
                }
            }
        },
        400: _SIMPLE_REQUEST_RESPONSES[400],
    },
}

CHAT_HISTORY_SPECS = {
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
            'name': 'offsetFromEnd',
            'in': 'query',
            'type': 'integer',
            'required': False,
        }
    ],
    'responses': {
        200: {
            'schema': {
                'type': 'object',
                'properties': {
                    'messages': {
                        'type': 'array',
                        'items': _CHAT_MESSAGE_SCHEMA,
                    }
                }
            }
        },
        400: _SIMPLE_REQUEST_RESPONSES[400],
        403: _SIMPLE_REQUEST_RESPONSES[403],
    }
}

CHAT_MESSAGES_FILES_SAVE_SPECS = {
    'tags': _CHAT_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        {
            'name': 'file',
            'in': 'body',
            'type': 'file',
            'required': True,
        },
    ],
    'responses': {
        201: {
            'schema': {
                'type': 'object',
                'properties': {
                    'storageId': {
                        'type': 'number',
                    }
                }
            }
        },
        400: _SIMPLE_REQUEST_RESPONSES[400],
    },
}

CHAT_MESSAGES_FILES_NAMES_SPECS = {
    'tags': _CHAT_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        {
            'name': 'storageId',
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
                    'filenames': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                        }
                    }
                }
            }
        }
    },
}

CHAT_MESSAGES_FILES_GET_SPECS = {
    'tags': _CHAT_TAGS,
    'parameters': [
        _ACCESS_TOKEN_COOKIE,
        {
            'name': 'storageId',
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
        }
    },
}
