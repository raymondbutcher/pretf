__version__ = '0.0.1'


class tf:

    def __init__(self, name, data):
        self.__name = name
        self.__data = data

    def __iter__(self):
        result = {}
        here = result
        for part in self.__name.split('.'):
            here[part] = {}
            here = here[part]
        here.update(self.__data)
        return iter(result.items())

    def __getattr__(self, attr):

        parts = self.__name.split('.')

        if parts[0] == 'resource':
            parts.pop(0)
        elif parts[0] == 'variable':
            parts[0] = 'var'

        parts.append(attr)

        return '${' + '.'.join(parts) + '}'

    def __str__(self):
        return self.__name
