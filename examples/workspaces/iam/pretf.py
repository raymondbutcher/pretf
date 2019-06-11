from pretf.util import import_file


def run():
    with import_file("../src/pretf_workflow.py") as workflow:
        workflow.run()
