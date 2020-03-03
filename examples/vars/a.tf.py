from pretf.blocks import output, variable


def pretf_blocks(var):
    yield variable.one(default=1)
    yield output.one(value=var.one)
    yield variable.two(default=2)
