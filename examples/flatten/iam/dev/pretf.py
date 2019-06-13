from pretf import workflow


def pretf_workflow():
    workflow.mirror_files("../../*", "../*", include_directories=False)
    return workflow.default()
