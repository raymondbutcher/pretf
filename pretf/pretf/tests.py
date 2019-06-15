import json
import os
import sys
import warnings
from pathlib import Path
from subprocess import CompletedProcess
from unittest import TestCase

from pretf import cli


class TerraformTestCase(TestCase):

    cwd = ""
    _cwd = ""
    init = False
    apply = False
    destroy = False

    @classmethod
    def setUpClass(cls) -> None:

        # Ignore "Boto3 ResourceWarning: unclosed <ssl.SSLSocket ...>"
        # because it is just HTTP connections that get reused or closed
        # as necessary.
        warnings.simplefilter("ignore", ResourceWarning)

        # Change the working directory while running tests.
        cls._cwd = str(Path.cwd())
        if cls.cwd:
            os.chdir(cls.cwd)

        # Make Terraform output more suitable for tests.
        os.environ["TF_IN_AUTOMATION"] = "1"
        os.environ["PRETF_CAPTURE_OUTPUT"] = "1"

        # Run terraform init.
        if cls.init:
            cls.terraform_init()

        # Run terraform apply.
        if cls.init:
            cls.terraform_apply()

    @classmethod
    def tearDownClass(cls) -> None:
        try:

            # Run terraform destroy.
            if cls.destroy:
                cls.terraform_destroy()

        finally:

            # Retore the old working directory.
            os.chdir(cls._cwd)

    @classmethod
    def terraform(cls, *args: str, returncode: int = 0) -> CompletedProcess:

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

    @classmethod
    def terraform_apply(cls, returncode: int = 0) -> CompletedProcess:
        return cls.terraform(
            "apply", "-input=false", "-auto-approve=true", returncode=returncode
        )

    @classmethod
    def terraform_destroy(cls, returncode: int = 0) -> CompletedProcess:
        return cls.terraform(
            "destroy", "-input=false", "-auto-approve=true", returncode=returncode
        )

    @classmethod
    def terraform_init(cls, returncode: int = 0) -> CompletedProcess:
        return cls.terraform("init", "-input=false", returncode=returncode)

    @classmethod
    def terraform_output_json(cls, returncode: int = 0) -> dict:
        proc = cls.terraform("output", "-json", returncode=returncode)
        return json.loads(proc.stdout)
