from pretf.blocks import output, variable


def pretf_blocks(var):
    yield output.two_attr(value=var.two)
    yield output.two_dict(value=var["two"])
    yield variable.three(default=3)
    yield output.three(value=var.three)
    yield variable.four
    yield output.four(value=var.four)
