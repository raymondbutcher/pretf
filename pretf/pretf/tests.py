import inspect
import json
import os
import sys
import warnings
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any as AnyType
from unittest import TestCase

from pretf import cli


class Any:
    def __eq__(self, other: AnyType) -> bool:
        return True


class TerraformTestCase(TestCase):

    maxDiff = None

    def chdir(self, path: str) -> None:

        self.addCleanup(os.chdir, os.getcwd())

        caller_frame = inspect.currentframe().f_back  # type: ignore
        caller_info = inspect.getframeinfo(caller_frame)
        caller_file = caller_info.filename
        caller_directory = Path(caller_file).parent

        os.chdir(caller_directory / path)

    def terraform(self, *args: str, returncode: int = 0) -> CompletedProcess:

        # Ignore "Boto3 ResourceWarning: unclosed <ssl.SSLSocket ...>"
        # because it is just HTTP connections that get reused or closed
        # as necessary.
        warnings.simplefilter("ignore", ResourceWarning)

        # Make Terraform output more suitable for tests.
        os.environ["TF_IN_AUTOMATION"] = "1"
        os.environ["PRETF_CAPTURE_OUTPUT"] = "1"

        argv = sys.argv
        sys.argv = ["terraform", *args]

        try:
            proc = cli.run()
        finally:
            sys.argv = argv

        if returncode is not None and proc.returncode != returncode:
            raise AssertionError(
                f"process return code {proc.returncode} != {returncode}"
            )

        return proc

    def terraform_apply(self, returncode: int = 0) -> CompletedProcess:
        return self.terraform(
            "apply", "-input=false", "-auto-approve=true", returncode=returncode
        )

    def terraform_destroy(self, returncode: int = 0) -> CompletedProcess:
        return self.terraform(
            "destroy", "-input=false", "-auto-approve=true", returncode=returncode
        )

    def terraform_init(self, returncode: int = 0) -> CompletedProcess:
        return self.terraform("init", "-input=false", returncode=returncode)

    def terraform_output_json(self, returncode: int = 0) -> dict:
        proc = self.terraform("output", "-json", returncode=returncode)
        return json.loads(proc.stdout)
