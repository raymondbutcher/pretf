from pretf.api import block


def pretf_files():
    # This downloads the module and then creates symlinks from that module
    # into the working directory.

    yield block("module", "vpc", {
        "source": "claranet/vpc-modules/aws//modules/vpc",
        "version": "1.0.1",
    })
