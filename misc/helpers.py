# coding: utf-8

from datetime import datetime
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sys import exit

from configs.db import oracle_url
from misc.log import logger

engine_oracle = create_engine(oracle_url, echo=False)
factory = sessionmaker(bind=engine_oracle, autocommit=False, autoflush=False)
session = factory()


def exit_on_fail(log_module: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                session.rollback()
                error_text = "Exception occurred"
                logger.getLogger(log_module).error(error_text, exc_info=True)
                print(f">>>>> {error_text}: {repr(e)}")
                exit(1)

        return wrapper

    return decorator


def str_to_datetaime(s: str, format: str):
    if not s:
        return None

    return datetime.strptime(s, format)


def transform_list_to_str(elems: list, delimeter: str = ";") -> str:
    return delimeter.join([elem["data"] for elem in elems])
