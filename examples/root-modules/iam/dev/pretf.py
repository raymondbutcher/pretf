from pretf import workflow


def pretf_workflow():
    workflow.mirror_files("../../modules/stack/*", "../../modules/stack-iam/*")
    return workflow.default()
