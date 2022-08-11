import os
import sys
import json
from json import loads as json_loads
from pathlib import Path
from subprocess import CompletedProcess
from types import TracebackType
from typing import Any, Optional, Type, Union

from pretf import util, workflow


class SensitiveValue:
    def __init__(self, value: Any):
        self.value = value


class TerraformCommand:
    def __init__(self, cwd: Union[Path, str] = "", verbose: Optional[bool] = False):
        if not isinstance(cwd, Path):
            cwd = Path(cwd)
        self.cwd = cwd
        self.env = os.environ.copy()
        self.env["TF_IN_AUTOMATION"] = "1"
        self.env["PRETF_VERBOSE"] = "1" if verbose else "0"
        self.verbose = verbose

    # Calling the object just returns another object with the specified path.

    def __call__(self, cwd: Union[Path, str] = "") -> "TerraformCommand":
        return self.__class__(cwd or self.cwd)

    # Context manager.
    # It doesn't do anything but can make the test code easier to follow.

    def __enter__(self) -> "TerraformCommand":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        return None

    # Terraform command.

    def execute(self, *args: str) -> CompletedProcess:
        return workflow.execute_terraform(
            args=args,
            cwd=self.cwd,
            env=self.env,
            capture=True,
            verbose=self.verbose,
        )

    # Terraform shortcuts.

    def apply(self, *args: str) -> dict:
        """
        Runs terraform apply, parses the output for output values,
        and returns them as a dictionary.

        """

        apply_args = ["apply", "-json", "-auto-approve=true"]
        for arg in args:
            if arg not in apply_args:
                apply_args.append(arg)

        proc = self.execute(*apply_args)

        outputs = None
        for line in proc.stdout.splitlines():
            
            # sometimes even with '-json' terraform creates non-json messages
            # like the one about acquiring state lock.
            try:
                log = json_loads(line)
            except json.decoder.JSONDecodeError:
                log = {"non-json-log": str(line)}
                       
            if log["type"] == "outputs":
                outputs = log["outputs"]

        if outputs is None:
            if proc.stderr:
                print(proc.stderr, file=sys.stderr)
            raise ValueError(f"Could not parse outputs from: {proc.stdout}")

        values = {}

        for name in outputs:
            value = outputs[name]["value"]
            if outputs[name]["sensitive"]:
                value = SensitiveValue(value)
            values[name] = value

        return values

    def destroy(self, *args: str) -> str:
        """
        Runs terraform destroy and returns the stdout.

        """

        destroy_args = ["destroy", "-input=false", "-auto-approve=true", "-no-color"]
        for arg in args:
            if arg not in destroy_args:
                destroy_args.append(arg)
        return self.execute(*destroy_args).stdout

    def get(self, *args: str) -> str:
        """
        Runs terraform get and returns the stdout.

        """

        get_args = ["get", "-no-color"]
        for arg in args:
            if arg not in get_args:
                get_args.append(arg)
        return self.execute(*get_args).stdout

    def init(self, *args: str) -> str:
        """
        Runs terraform init and returns the stdout.

        """

        init_args = ["init", "-input=false", "-no-color"]
        for arg in args:
            if arg not in init_args:
                init_args.append(arg)
        return self.execute(*init_args).stdout

    def output(self, *args: str) -> dict:
        """
        Runs terraform output and returns the JSON.

        """

        output_args = ["output", "-json"]
        for arg in args:
            if arg not in output_args:
                output_args.append(arg)
        return json_loads(self.execute(*output_args).stdout)

    def plan(self, *args: str) -> str:
        """
        Runs terraform plan and returns the stdout.

        """

        plan_args = ["plan", "-input=false", "-no-color"]
        for arg in args:
            if arg not in plan_args:
                plan_args.append(arg)
        return self.execute(*plan_args).stdout


class PretfCommand(TerraformCommand):
    def execute(self, *args: str) -> CompletedProcess:
        return util.execute(
            file="pretf",
            args=["pretf"] + list(args),
            cwd=self.cwd,
            env=self.env,
            capture=True,
            verbose=self.verbose,
        )
