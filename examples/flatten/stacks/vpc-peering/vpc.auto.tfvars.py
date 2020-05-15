from pretf.api import get_outputs, log


def pretf_variables(var):
    dev = get_outputs("vpc/dev")
    if not dev:
        raise log.bad("vpc/dev stack has no outputs")

    prod = get_outputs("vpc/prod")
    if not dev:
        raise log.bad("vpc/prod stack has no outputs")

    yield {
        "dev_vpc_id": dev["vpc_id"],
        "prod_vpc_id": prod["vpc_id"],
    }
