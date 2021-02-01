import os
from datetime import datetime
from glob import glob
from pathlib import Path

import appdirs
from strictyaml import Datetime, EmptyDict, Float, Int, Map, MapPattern, Optional, Seq, Str, load

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
                Str()
                | Int()
                | Float()
                | Datetime()
                | Seq(Str() | Int() | Float() | Datetime())
                | EmptyDict()
                | MapPattern(
                    Str(),
                    Str()
                    | Int()
                    | Float()
                    | Datetime()
                    | Seq(Str() | Int() | Float() | Datetime())
                    | EmptyDict()
                    | MapPattern(
                        Str(),
                        Str()
                        | Int()
                        | Float()
                        | Datetime()
                        | Seq(Str() | Int() | Float() | Datetime())
                        | EmptyDict(),
                    ),
                ),
            ),
            Optional('docker', default=None): MapPattern(
                Str(),
                Str()
                | Int()
                | Float()
                | Datetime()
                | Seq(Str() | Int() | Float() | Datetime())
                | EmptyDict()
                | MapPattern(
                    Str(),
                    Str()
                    | Int()
                    | Float()
                    | Datetime()
                    | Seq(Str() | Int() | Float() | Datetime())
                    | EmptyDict()
                    | MapPattern(
                        Str(),
                        Str()
                        | Int()
                        | Float()
                        | Datetime()
                        | Seq(Str() | Int() | Float() | Datetime())
                        | EmptyDict(),
                    ),
                ),
            ),
        }
    )
    _schema_depth = {
        'meta': 2,
        'app': 4,
        'docker': 4,
    }

    def __init__(self, __configfile=None):
        super().__init__()

        # Set up settings file
        self._configfile = (
            os.sep.join([appdirs.user_config_dir(Config.appname), 'settings.yaml'])
            if not __configfile
            else __configfile
        )
        Config.ensure_configpath()
        self.logger.debug(f'Settings file is {self._configfile}.')

        # Read settings or apply default template
        try:
            with open(self._configfile) as f:
                self._data = load(f.read(), Settings.schema)
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
            self._data = defaultconf
            self.save()

    def save(self):
        try:
            with open(self._configfile, 'w') as f:
                f.write(self._data.as_yaml())
            return True
        except Exception as e:
            self.logger.error(f'Config file could not be written ({e})')
            return False

    def get(self, key):
        keypath = key.split('.')
        d = self._data
        while keypath:
            k = keypath.pop(0)
            if k in d.keys():
                if keypath:
                    d = d[k]
                else:
                    return d[k].data
        raise ValueError('Settings key not found.')

    def set(self, key, value):
        keypath = key.split('.')
        for section, allowed_depth in Settings._schema_depth.items():
            if keypath[0] == section and len(keypath) > allowed_depth:
                raise ValueError(
                    f'The {section} section does not allow more than {allowed_depth} levels.'
                )
        d = self._data
        while keypath:
            k = keypath.pop(0)
            if k in d.keys():  # the key already exists
                if keypath:
                    d = d[k]  # iterate to the next node
                else:
                    self.logger.debug(f'Changing Settings item *{key}* from {d[k]} to {value}.')
                    d[k] = value  # set the value of the leaf
                    self.save()
                    return
            else:  # the key doesn't exist yet
                if keypath:  # there is still path left to cover
                    # create a dictionary containing the remaining path
                    newd = {}
                    d2 = newd
                    while keypath:
                        k2 = keypath.pop(0)
                        if keypath:
                            d2[k2] = {}
                            d2 = d2[k2]
                        else:
                            d2[k2] = value
                    # insert the dictionary into the main structure at the (previous) leaf

                    self.logger.debug(f'Creating new Settings item *{key}* with value {value}.')
                    d[k] = newd
                else:  # there is no path element left (this is a leaf)
                    self.logger.debug(f'Creating new Settings item *{key}* with value {value}.')
                    d[k] = value  # set the value of the leaf
                self.save()
                return


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
                        Optional('path', default=None): Str(),
                        Optional('args', default=None): Seq(Str()) | Str(),
                        Optional('kwargs', default=None): Str() | MapPattern(Str(), Str()),
                        Optional('output', default='transcript'): Str(),
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

    def __init__(self, path=None, data=None, name=None, app=None):
        super().__init__(name=name, app=app)
        self._path = path
        if data:
            self.logger.info('Initializing from data...')
            self._data = load(data, Snoutfile.schema).data
        elif self._path:
            self.logger.info(f'Initializing from file {self.path}...')
            with open(self.path) as f:
                self._data = load(f.read(), Snoutfile.schema).data
        else:
            raise Exception(
                'Snoutfile cannot be initialized with no path or data (neither provided).'
            )

    @property
    def path(self):
        return self._path

    @property
    def data(self):
        try:
            return self._data
        except AttributeError:
            return {}
