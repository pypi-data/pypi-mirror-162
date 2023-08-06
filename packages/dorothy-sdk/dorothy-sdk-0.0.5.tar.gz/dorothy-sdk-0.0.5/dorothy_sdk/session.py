import os
import requests


class Session(requests.Session):
    _token = None
    _token_file = '/tmp/dorotysdk/credentials.txt'
    _environment_variable_name = 'DOROTYSDK_ACCESS_TOKEN'

    def __init__(self, token: str = None, **options):
        super().__init__()
        if not token:
            self._fetch_token(**options)
        else:
            self._token = token
        self.headers.update({"Authorization": f"Token {self._token}"})

    def set_token(self, token: str) -> None:
        """
        Metodo responsável por fazer o set da variavel _token
        :param token: String com o token de acesso ao Dorothy
        :return: None
        """
        self._token = token

    def _fetch_token(self, **options):
        if options.get('path', ''):
            if os.path.exists(options.get('path')):
                self._token_file = options.get('path')
            else:
                FileNotFoundError("Credentials file passed as parameter not found.")

        token = os.environ.get(self._environment_variable_name, '')
        if not token:
            if os.path.exists(self._token_file):
                with open(self._token_file, mode='r', encoding='utf-8') as credentials_file:
                    self._token = credentials_file.read().replace('\n', '').replace('\t', '').replace('\r', '').strip()
            else:
                raise RuntimeError("Access credential not found. The credential can be entered either as a parameter "
                                   "or via a credentials file or environment variable")
        else:
            self._token = token
