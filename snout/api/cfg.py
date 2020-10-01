import os
from datetime import datetime
from glob import glob
from pathlib import Path

import appdirs
from strictyaml import Datetime, Float, Int, Map, MapPattern, Optional, Seq, Str, load

from snout.api import classproperty
from snout.api.agent import SnoutAgent
from snout.api.log import Logger


class Config(object):
    appname = 'Snout'
    appauthor = 'NISLAB'

    custom_snoutfile_paths = []

    _settings = None

    @classproperty
    def settings(cls):
        if not cls._settings:
            cls._settings = Settings()
        return cls._settings

    # def __getattribute__(self, key):
    #     print('HIT GETATTRIBUTE HOOK')
    #     setattr(self, key, 'hello')
    #     return getattr(self, key)
    #     self.__dict__[key] = 'HELLO'
    #     return "HELLO"

    @classmethod
    def ensure_configpath(cls):
        Path(appdirs.user_config_dir(cls.appname)).mkdir(parents=True, exist_ok=True)

    @classmethod
    def snoutfile_paths(cls, custompath=None):
        cls.ensure_configpath()
        if custompath:
            if isinstance(custompath, str):
                custompath = [custompath]
            if isinstance(custompath, list):
                cls.custom_snoutfile_paths = custompath + cls.custom_snoutfile_paths
            else:
                raise TypeError(
                    f'A provided custompath must be a string or list ({type(custompath)} provided).'
                )
        return [
            *cls.custom_snoutfile_paths,
            appdirs.user_config_dir(cls.appname),
        ]

    @classmethod
    def snoutfiles(cls, custompath=None, pattern=None):
        searchpath = Config.snoutfile_paths(custompath=custompath)
        if not pattern:
            pattern = '*.snoutfile'
        snoutfiles = []
        for path in searchpath:
            snoutfiles += sorted(glob(os.sep.join([path, pattern])))
        snoutfiles = list(set(snoutfiles))
        return snoutfiles


class Settings(Logger):
    schema = Map(
        {
            'meta': Map(
                {
                    'created': Datetime(),
                    'modified': Datetime(),
                }
            ),
            Optional('app', default=None): MapPattern(
                Str(),
                Str() | Int() | Float() | Datetime() | Seq(Str() | Int() | Float() | Datetime()),
            ),
            Optional('docker', default=None): MapPattern(
                Str(),
                Str() | Int() | Float() | Datetime() | Seq(Str() | Int() | Float() | Datetime()),
            ),
        }
    )

    def __init__(self):
        super().__init__(self)
        self._configfile = os.sep.join([appdirs.user_config_dir(Config.appname), 'settings.yaml'])
        Config.ensure_configpath()

        self.logger.debug(f'Settings file is {self._configfile}.')
        try:
            with open(self._configfile) as f:
                self._data = load(f.read(), Settings.schema).data
        except FileNotFoundError:
            curdate = datetime.now()
            defaultconf = load(
                f"""
meta:
    created: {curdate}
    modified: {curdate}
""",
                Settings.schema,
            )
            with open(self._configfile, 'w') as f:
                f.write(defaultconf.as_yaml())
            self._data = defaultconf

    def __getattr__(self, key):
        return SettingsItem(self._data[key], self, key)


class SettingsItem:
    def __init__(self, data, settings, path):
        self._data = data
        self._settings = settings
        self._path = path

    def __getattr__(self, key):
        return SettingsItem(self._data[key], self._settings, '.'.join([self._path, key]))

    def __repr__(self):
        return f'SettingsItem({repr(self._data)})'

    @property
    def value(self):
        return self._data.value

    def isleaf(self):
        return not isinstance(self._data, dict)

    def children(self):
        if not isinstance(self._data, dict):
            return None
        return self._data.keys()


class Snoutfile(SnoutAgent):

    schema = Map(
        {
            'meta': Map(
                {
                    'name': Str(),
                    'description': Str(),
                    'author': Str(),
                    'email': Str(),
                    'date': Datetime(),
                }
            ),
            'instrument': MapPattern(
                Str(),
                Map(
                    {
                        'class': Str(),
                        Optional('protocol', default=None): Str(),
                        'path': Str(),
                        Optional('args', default=None): Seq(Str()) | Str(),
                        Optional('kwargs', default=None): Str() | MapPattern(Str(), Str()),
                        Optional('output', default='pipeline'): Str(),
                    }
                ),
            ),
            Optional('parameters', default=None): MapPattern(
                Str(), Str() | Seq(Str() | Int() | Float()) | Int() | Float()
            ),
            'steps': Seq(
                MapPattern(
                    Str(),
                    Map(
                        {
                            'instrument': Str(),
                            'command': Str(),
                            'condition': Map(
                                {
                                    'type': Str(),
                                    'criteria': Int()
                                    | Float()
                                    | Str()
                                    | Seq(Int() | Float() | Str()),
                                }
                            ),
                        }
                    ),
                )
            ),
            Optional('runs', default=1): Int(),
            Optional('pipeline', default=None): Seq(
                MapPattern(Str(), MapPattern(Str(), Str() | Int() | Float()))
            ),
        }
    )

    @staticmethod
    def factory(filepaths=None):
        filepaths = Config.snoutfiles(custompath=filepaths)
        Logger.logger.info(str(filepaths))
        snoutfiles = []
        for path in filepaths:
            Logger.logger.info(f'Trying {path}:')
            snoutfiles.append(Snoutfile(path))
        return snoutfiles

    def __init__(self, path, name=None, app=None):
        super().__init__(name=name, app=app)
        self._path = path
        if self._path:
            self.logger.info(f'Initializing from file {self.path}...')
            with open(self.path) as f:
                self._data = load(f.read(), Snoutfile.schema).data

    @property
    def path(self):
        return self._path

    @property
    def data(self):
        try:
            return self._data
        except AttributeError:
            return {}
