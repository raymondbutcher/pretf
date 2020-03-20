from pretf.api import get_outputs


def pretf_variables(var):
    dev = get_outputs("../../vpc/dev")
    prod = get_outputs("../../vpc/prod")
    yield {
        "dev_vpc_id": dev["vpc_id"],
        "prod_vpc_id": prod["vpc_id"],
    }
