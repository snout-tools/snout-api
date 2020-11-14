import pkg_resources
from tabulate import tabulate


class Factory(object):

    _plugins = {}

    @staticmethod
    def _print_plugin_table(plugins):
        def k_default(k):
            return k[-1] == '_'

        def k_basename(k):
            return k.split('_')[0]

        def k_keyword(k):
            return k.split('_')[1]

        return tabulate(
            [
                [k_basename(k), k_keyword(k), v.__module__, v.__name__, k_default(k)]
                for k, v in plugins.items()
            ],
            headers=['Basename', 'Keyword', 'Module', 'Class', 'Default'],
        )

    @classmethod
    def plugins(cls):
        if not cls._plugins:
            for plugin in pkg_resources.iter_entry_points('snout_plugins'):
                cls._plugins[plugin.name] = plugin.load()
        return cls._plugins

    @classmethod
    def listall(cls):
        cls._print_plugin_table(cls.plugins())

    def __init__(self, main, variant=None):
        self.main = main
        self.variant = variant

    def ls(self, listall=False, ret=False):
        if listall:
            result = self.__class__._print_plugin_table(self.plugins())
        else:
            result = self.__class__._print_plugin_table(
                dict(
                    filter(lambda elem: elem[0].startswith(f'{self.main}_'), self.plugins().items())
                )
            )
        if ret:
            return result
        print(result)

    def instance(self, variant=None):
        variant = variant or self.variant
        if not variant:
            variant = ''
        for k, v in self.plugins().items():
            main, var = k.split('_')
            if main == self.main and var == str(variant):
                return v
        return None
