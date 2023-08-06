"""
- ConfigError
    - NoEnvVarSetUpError
- ConnectionError
- DatabaseAPIError
    - AuthCredentialsAPIError
        - NoCookiesError
        - NoTokenError
- DodoAPIError
"""


class HTTPAPIConnectionError(Exception):
    pass


class DodoAPIError(Exception):
    pass


class DatabaseAPIError(Exception):
    pass


class AuthCredentialsAPIError(DatabaseAPIError):

    def __init__(self, *args, account_name: str):
        super().__init__(*args)
        self.account_name = account_name


class NoCookiesError(AuthCredentialsAPIError):
    pass


class NoTokenError(AuthCredentialsAPIError):
    pass


class ConfigError(Exception):
    pass


class NoEnvVarSetUpError(ConfigError):

    def __init__(self, *args, env_var_name: str):
        super().__init__(f'Environment variable "{env_var_name}" is not set up', *args)
        self.env_var_name = env_var_name
