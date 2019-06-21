from unittest.mock import ANY

import pytest

from pretf import test


class TestFlatten(test.SimpleTest):
    @pytest.mark.parameterize(
        "stack,env", [("iam", "dev"), ("iam", "prod"), ("vpc", "dev"), ("vpc", "prod")]
    )
    def test_init(self, stack, env):
        self.pretf(f"stacks/{stack}/{env}").init()

    @pytest.mark.parameterize(
        "stack,env,expected",
        [
            ("iam", "dev", {"user_name": "pretf-flatten-dev"}),
            ("iam", "prod", {"user_name": "pretf-flatten-prod"}),
            ("vpc", "dev", {"vpc_id": ANY}),
            ("vpc", "prod", {"vpc_id": ANY}),
        ],
    )
    def test_apply(self, stack, env, expected):
        outputs = self.pretf(f"stacks/{stack}/{env}").apply()
        assert outputs == expected

    @test.always
    @pytest.mark.parameterize(
        "stack,env", [("iam", "dev"), ("iam", "prod"), ("vpc", "dev"), ("vpc", "prod")]
    )
    def test_destroy(self, stack, env):
        self.pretf(f"stacks/{stack}/{env}").destroy()
