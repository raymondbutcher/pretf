from pretf import workflow


def pretf_workflow(terraform):
    workflow.mirror_files(
        "../modules/stack/stack.tf.py",
        f"../params/vpc.{terraform.workspace}.auto.tfvars",
    )
    return workflow.default()
