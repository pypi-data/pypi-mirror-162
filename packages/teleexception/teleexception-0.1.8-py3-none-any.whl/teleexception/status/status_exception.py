# -*- coding:utf-8 -*-
from .http_status import HTTPStatus


class StatusException(Exception):
    def __init__(self, status: HTTPStatus):
        self.code = status.value
        self.message = status.phrase
        self.details = status.description

    def __str__(self):
        return f'code: {self.code}, message: {self.message}, details: {self.details}'
