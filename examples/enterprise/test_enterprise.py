from unittest.mock import ANY

import pytest

from pretf import test


class TestFlatten(test.SimpleTest):
    @pytest.mark.parametrize(
        "stack,env,expected", [
            ("vpc", "dev", {"internet_gateway_id": ANY, "vpc_cidr_block": "10.1.0.0/16", "vpc_id": ANY}),
            ("vpc", "prod", {"internet_gateway_id": ANY, "vpc_cidr_block": "10.2.0.0/16", "vpc_id": ANY}),
        ],
    )
    def test_create_vpc(self, stack, env, expected):
        self.pretf(f"stacks/{stack}/{env}").init()
        outputs = self.pretf(f"stacks/{stack}/{env}").apply()
        assert outputs == expected

    @pytest.mark.parametrize(
        "stack,env,expected", [
            ("security", "dev", {"security_group_id": ANY}),
            ("security", "prod", {"security_group_id": ANY}),
        ],
    )
    def test_create_security(self, stack, env, expected):
        self.pretf(f"stacks/{stack}/{env}").init()
        outputs = self.pretf(f"stacks/{stack}/{env}").apply()
        assert outputs == expected

    @test.always
    @pytest.mark.parametrize(
        "stack,env", [
            ("security", "dev"),
            ("security", "prod"),
            ("vpc", "dev"),
            ("vpc", "prod"),
        ],
    )
    def test_destroy_all(self, stack, env):
        self.pretf(f"stacks/{stack}/{env}").destroy()
