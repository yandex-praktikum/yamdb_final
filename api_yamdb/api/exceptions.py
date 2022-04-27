class APIError(Exception):
    """базовый класс для всех исключений."""
    pass


class UserValueError(APIError):
    """Имя пользователя не существет в базе."""
    pass


class MailValueError(APIError):
    """Адрес почты не уникален."""
    pass
