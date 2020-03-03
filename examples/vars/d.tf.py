from pretf.blocks import output


def pretf_blocks(var):
    yield output.five(value=var.five)
    yield output.six(value=var.six)
    yield output.seven(value=var.seven)
