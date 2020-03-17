from pretf.files import module


def pretf_files():
    # This downloads the module and then creates symlinks from that module
    # into the working directory.

    yield module("claranet/vpc-modules/aws//modules/vpc", version="1.0.0")
