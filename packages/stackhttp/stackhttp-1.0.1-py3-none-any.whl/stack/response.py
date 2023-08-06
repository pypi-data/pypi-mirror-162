from dataclasses import dataclass, field
from io import TextIOWrapper
from json import dumps
import mimetypes
import os
import re
from types import GeneratorType
from typing import Union

CODES = {
    200: "OK",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    500: "Internal Server Error",
    501: "Not Implemented"
}


@dataclass
class Response(object):
    headers: dict = field(default_factory=lambda: {"Server": "stack"})
    code: int = 200
    status: str = 'OK'
    data: Union[GeneratorType, bytes, str] = b''
    # Transform {key: value} into {sanitized_value: (key, value)}
    shortcut_methods: dict = field(repr=False, default_factory=lambda: {re.sub("[^a-zA-Z ]*", "", value).lower().replace(" ", "_"): (key, value) for key, value in CODES.items()})
    
    def http(self):
        yield f"HTTP/1.1 {self.code} {self.status}".encode('utf-8')
        for k, v in self.headers.items():
            yield f"\r\n{k}: {v}".encode('utf-8')
        yield b"\r\n\r\n"

        if isinstance(self.data, GeneratorType):
            for i in self.data:
                if not isinstance(i, bytes):
                    i = i.encode("utf-8")
                yield i
            return
        yield self.data
    


    @staticmethod
    def file_generator(file: TextIOWrapper):
        while data := file.read(1):
            yield data

    def define_content(self, content_type, content_length, content, encoding='utf-8'):
        self.headers['Content-Type'] = content_type
        if encoding:
            self.headers['Content-Type'] += f"; charset={encoding}"
        self.headers['Content-Length'] = content_length
        self.content = content
        return self

    def add_shortcut_code(self, code, status):
        sanitized_status = re.sub("[^a-zA-Z ]*", "", status).lower().replace(" ", "_")
        self.shortcut_methods[sanitized_status] = (code, status)

    def define_code(self, code, status, page=None, json=None):
        self.code = code
        self.status = status
        if page:
            self.send_file(page)
        elif json:
            self.send_json(json)
    
    def __getattribute__(self, name):
        # Implement dynamic code setting.
        _shortcut_methods = object.__getattribute__(self, "shortcut_methods")
        if name in _shortcut_methods:
            return lambda page=None, json=None: self.define_code(*_shortcut_methods[name], page, json)
        else:
            return object.__getattribute__(self, name)


    def __dir__(self):
        return [*super().__dir__(), *self.shortcut_methods.keys()]

    def send_file(self, path, encoding=None):
        mime_type = mimetypes.guess_type(path)

        file = open(path, 'rb')

        return self.define_content(
            mime_type[0],
            os.stat(path).st_size,
            self.file_generator(file)
        )

    def send_json(self, data):
        data = dumps(data).encode('utf-8')

        return self.define_content(
            'application/json',
            len(data),
            data
        )
