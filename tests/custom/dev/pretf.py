import pretf


def sources():
    yield '.'


def params():
    yield 'users', ['ray', 'violet']


def remove(created):
    pretf.remove('*.tf.json', exclude=created)
