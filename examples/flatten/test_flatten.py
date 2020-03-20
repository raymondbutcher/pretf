from unittest.mock import ANY

import pytest

from pretf import test


class TestFlatten(test.SimpleTest):
    @pytest.mark.parametrize(
        "stack,env,expected", [
            ("iam", "dev", {"user_name": "pretf-flatten-dev"}),
            ("iam", "prod", {"user_name": "pretf-flatten-prod"}),
            ("vpc", "dev", {"vpc_id": ANY}),
            ("vpc", "prod", {"vpc_id": ANY}),
            ("vpc-peering", "prod", {"status": "active"}),
        ],
    )
    def test_apply(self, stack, env, expected):
        self.pretf(f"stacks/{stack}/{env}").init()
        outputs = self.pretf(f"stacks/{stack}/{env}").apply()
        assert outputs == expected

    @test.always
    @pytest.mark.parametrize(
        "stack,env", [
            ("vpc-peering", "prod"),
            ("vpc", "prod"),
            ("vpc", "dev"),
            ("iam", "prod"),
            ("iam", "dev"),
        ],
    )
    def test_destroy(self, stack, env):
        self.pretf(f"stacks/{stack}/{env}").destroy()
