""" This module implement singleton decorator  """


def singleton(cls):
    """
    Decorator implementation for decorator

    """
    instance = [None]

    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper
