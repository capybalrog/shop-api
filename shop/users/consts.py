ADMIN = 'admin'

ERRORS = {
    'role': {
        'wrong': 'Такой роли не существует.',
    },
    'email': {
        'exists': 'Пользователь с таким email уже существует.',
    },
    'quantity': {
        'less_than_zero': 'Количество товаров не может быть отрицательным.',
    },
    'username': {
        'exists': 'Пользователь с таким username уже существует.'
    }
}


MAGIC_NUMBERS = {
    'count':{
        'max_decimal_digits': 10,
        'max_decimal_places': 2,
        'max_length': 150,
        'truncated_str': 35
    }
}


USER_ROLES = (
    ('admin', 'Администратор'),
    ('user', 'Пользователь'),
)
