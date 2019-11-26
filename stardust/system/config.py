import json
import os
import random
import string


class Config:

    def __init__(self, **kwargs):

        if 'path' in kwargs:
            with open(kwargs['path'], 'r') as f:
                data = json.load(f)
        else:
            data = kwargs

        self.workers_count = data.get('workers_count', os.cpu_count())
        self.host = data.get('host', '127.0.0.1')
        self.port = data.get('port', '8000')
        self.secret = data.get('secret', self._generate_secret(64))
        self._system_name = data.get('system_name', 'actor_system')

    @staticmethod
    def _generate_secret(length):
        return ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(length)
        )

    @property
    def system_name(self):
        return f"{self._system_name}@{self.host}:{self.port}"
