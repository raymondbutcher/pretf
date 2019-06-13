from pretf import workflow


def pretf_workflow():
    workflow.mirror_files("../../modules/stack/*", "../../modules/stack-vpc/*")
    return workflow.default()
