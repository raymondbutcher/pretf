from .render import Block


class API:
    def __call__(self, path, body=None):
        return Block(path, body)


tf = API()
