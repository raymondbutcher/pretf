import os
import sys
import warnings
from pathlib import Path
from unittest import TestCase

from pretf import cli


class TerraformTestCase(TestCase):

    cwd = None
    init = False
    apply = False
    destroy = False

    @classmethod
    def setUpClass(cls):

        # Ignore "Boto3 ResourceWarning: unclosed <ssl.SSLSocket ...>"
        # because it is just HTTP connections that get reused or closed
        # as necessary.
        warnings.simplefilter("ignore", ResourceWarning)

        # Change the working directory while running tests.
        if cls.cwd:
            cls._cwd = Path.cwd()
            cwd = Path(__file__).parent / cls.cwd
            os.chdir(cwd)

        # Make Terraform output more suitable for tests.
        os.environ["TF_IN_AUTOMATION"] = "1"

        # Run terraform init.
        if cls.init:
            cls.terraform_init()

        # Run terraform apply.
        if cls.init:
            cls.terraform_apply()

    @classmethod
    def tearDownClass(cls):
        try:

            # Run terraform destroy.
            if cls.destroy:
                cls.terraform_destroy()

        finally:

            # Retore the old working directory.
            if cls.cwd:
                os.chdir(cls._cwd)

    @classmethod
    def terraform(cls, *args, assert_exit_code=0):

        argv = sys.argv
        sys.argv = ["terraform", *args]

        try:
            exit_code = cli.run()
        finally:
            sys.argv = argv

        if assert_exit_code is not None and exit_code != assert_exit_code:
            raise AssertionError(f"exit code {exit_code} != {assert_exit_code}")

        return exit_code

    @classmethod
    def terraform_apply(cls, assert_exit_code=0):
        return cls.terraform(
            "apply",
            "-input=false",
            "-auto-approve=true",
            assert_exit_code=assert_exit_code,
        )

    @classmethod
    def terraform_destroy(cls, assert_exit_code=0):
        return cls.terraform(
            "destroy",
            "-input=false",
            "-auto-approve=true",
            assert_exit_code=assert_exit_code,
        )

    @classmethod
    def terraform_init(cls, assert_exit_code=0):
        return cls.terraform("init", "-input=false", assert_exit_code=assert_exit_code)


class TestAWS(TerraformTestCase):

    cwd = ".."
    init = True
    apply = True
    destroy = False

    def test_output(self):
        self.terraform("output", "--json")
        # TODO: get stdout from that and make assertions
