from pretf import workflow


def pretf_workflow():
    workflow.mirror_files("../../*.*", "../*.*")
    return workflow.default()
