import io
import os

from tomlkit import loads


class Configula:
    """
    Creates a single configuration by merging settings defined in:
        1. in environment variables
        2. in toml file

    Values provided in **environment variables have priority** over values from
    toml configuration file.

    By default all environment variables are prefixed with 'PAPERMERGE'. By
    default `__` (two underscores) is used as delimiter in environment
    variables names. For example, given following toml file:

        [main]
            secret_key = 1234

        [ocr]
            default_language = 'deu'

    corespondent environment variables names are PAPERMERGE__MAIN__SECRET_KEY
    and PAPERMERGE__OCR__DEFAULT_LANGUAGE - notice two underscores separate
    section name from prefix and variable name. Environment variable name
    format is (all in uppercase):

         <prefix><delimiter><section><delimiter><variable>

    Although in toml files you can place variable names outside sections, in
    Configula all variables **must be placed in sections**.

    By default Configula looks up for following toml file:

        - /etc/papermerge/papermerge.toml
        - /etc/papermerge.toml
        - papermerge.toml

    If you have custom location (or custom file name), use
    ``PAPERMERGE__CONFIG``(notice double underscores) environment variable to
    point to it:

        PAPERMERGE__CONFIG=/app/config/pm.toml

    Example of usage:

        from configula import Configula

        config = Configula()

        default_language = config.get('ocr', 'default_language')
        secret_key = config.get('main', 'secret_key')
        debug = config.get('main', 'debug', default=False)
    """
    MYSQL_TYPE = ('my', 'mysql', 'maria', 'mariadb')
    POSTGRES_TYPE = ('pg', 'postgre', 'postgres', 'postgresql')
    DEFAULT_PREFIX = 'PAPERMERGE'
    DEFAULT_DELIMITER = '__'
    DEFAULT_LOCATIONS = [
        "/etc/papermerge/papermerge.toml",
        "/etc/papermerge.toml",
        "papermerge.toml"
    ]
    DEFAULT_CONFIG_VAR_NAME = "PAPERMERGE__CONFIG"

    def __init__(
        self,
        prefix=None,
        delimiter=None,
        config_locations=None,
        config_env_var_name=None
    ):
        """
        `config_locations` (list): a list of string file paths
            where to load configurations from
        `config_env_var_name` (str): in case `config_locations` was
            not provided, load file configurations
        from a file pointed by this environment variable
        `prefix` (str): all configurations provided by environment
            variables will be prefixed with this value
        `delimiter` (str): default delimiter is `__` (two underscores)
            i.e. <prefix>__<section>__<value>

        Example:

            Configula(
                prefix='PAPERMERGE',
                config_locations=[
                    'papermerge.toml',
                    '/etc/papermerge.toml'
                ],
                config_env_var_name='PAPERMERGE__CONFIG'
            )

        In case papermerge.toml was not found in current location
        and /etc/papermerge.toml does not exists, it continue look for
        configuration file by looking at PAPERMERGE__CONFIG environment
        variable. If PAPERMERGE__CONFIG environment variable exists and is
        (for example):

            PAPERMERGE__CONFIG=/home/eugen/papermerge.toml

        will load configurations from /home/eugen/papermerge.toml.

        Environment variables values have HIGHTEST priority.
        If both toml configuration file is present and corresponding
        environment variable is present - environment variable gets
        priority over corresponding value found in toml file.
        """
        if config_locations is None:
            self.config_locations = self.DEFAULT_LOCATIONS
        else:
            self.config_locations = config_locations

        if config_env_var_name is None:
            self.config_env_var_name = self.DEFAULT_CONFIG_VAR_NAME
        else:
            self.config_env_var_name = config_env_var_name

        if prefix is None:
            self.prefix = self.DEFAULT_PREFIX
        else:
            self.prefix = prefix

        if delimiter is None:
            self.delimiter = self.DEFAULT_DELIMITER
        else:
            self.delimiter = delimiter

        self._toml_config = self.load_toml()

    def _loads(self, file_path):
        with io.open(file_path, encoding="utf-8") as f:
            return loads(f.read())

    def load_toml(self):
        """
        Loads toml configuration file from self.config_locations or
        from location pointed by self.config_env_var_name.

        Returns None in case toml configuration file was not found.
        Returns a dictionary of configuration if toml config was found.
        """
        for config_file in self.config_locations:
            if os.path.exists(config_file):
                return self._loads(config_file)

        config_file = os.environ.get(self.config_env_var_name, False)
        if config_file and os.path.exists(config_file):
            return self._loads(config_file)

    def get(self, section_name, var_name, default=None):
        """
        Reads `var_name` in section `section_name` either from toml config
        or from environment variable.

        In case no value is found in above sources value provided as `default`
        will be returned.
        """
        pref = self.prefix
        delim = self.delimiter
        env_name = f"{pref}{delim}{section_name}{delim}{var_name}".upper()

        try:
            env_value = os.getenv(env_name)
            value = env_value or self._toml_config[section_name][var_name]
        except Exception as _:
            value = default

        return value

    def get_django_databases(self, proj_root):
        """Returns dictionary for django DATABASES settings"""
        # by default, if no value is provided for database, use
        # sqlite3 with file located in `proj_root`
        section = 'database'
        result = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": os.path.join(
                    self.get(
                        section,
                        'dir',
                        default=proj_root
                    ),
                    'db.sqlite3'
                )
            }
        }

        if self.get(section, 'type', False) in self.POSTGRES_TYPE:
            result["default"] = {
                "ENGINE": "django.db.backends.postgresql_psycopg2",
                "NAME": self.get(section, "name", "papermerge"),
                "USER": self.get(section, "user", "papermerge"),
            }
            result["default"]["PASSWORD"] = self.get(section, 'password', "")
            result["default"]["HOST"] = self.get(
                section,
                'host',
                'localhost'
            )
            result["default"]["PORT"] = self.get(section, 'port', 5432)
        elif self.get(section, 'type', False) in self.MYSQL_TYPE:
            result['default'] = {
                "ENGINE": "django.db.backends.mysql",
                "NAME": self.get(section, 'name', 'papermerge'),
                "USER": self.get(section, 'user', 'papermerge'),
            }
            result["default"]["PASSWORD"] = self.get(section, 'password', '')
            result["default"]["HOST"] = self.get(
                section, 'host', 'localhost'
            )
            result["default"]["PORT"] = self.get(section, 'port', 3306)

        return result

    @property
    def has_mysql(self):
        return self.get('database', 'type') in self.MYSQL_TYPE
