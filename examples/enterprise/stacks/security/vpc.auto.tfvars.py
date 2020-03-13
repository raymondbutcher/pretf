from pretf.test import PretfProxy


def pretf_variables(var):

    vpc = PretfProxy(cwd=f"../../vpc/{var.environment}").output()

    yield {
        "vpc_id": vpc["vpc_id"]["value"],
    }
