from unittest.mock import ANY

import pytest

from pretf import test


class TestWorkspaces(test.SimpleTest):
    @pytest.mark.parametrize("stack", [
        "iam",
        "vpc",
        "vpc-peering",
    ])
    def test_init(self, stack):
        with self.pretf(f"stacks/{stack}") as tf:
            tf.init()

    @pytest.mark.parametrize("stack,workspace,expected", [
        ("iam", "default", {"user_name": "pretf-workspaces-dev"}),
        ("iam", "prod", {"user_name": "pretf-workspaces-prod"}),
        ("vpc", "default", {"vpc_id": ANY}),
        ("vpc", "prod", {"vpc_id": ANY}),
        ("vpc-peering", "default", {"status": "active"}),
    ])
    def test_apply(self, stack, workspace, expected):
        with self.pretf(f"stacks/{stack}") as tf:
            tf.execute("workspace", "select", workspace)
            outputs = tf.apply()
            assert outputs == expected

    @test.always
    @pytest.mark.parametrize("stack,workspace", [
        ("vpc-peering", "default"),
        ("vpc", "prod"),
        ("vpc", "default"),
        ("iam", "prod"),
        ("iam", "default"),
    ])
    def test_destroy(self, stack, workspace):
        with self.pretf(f"stacks/{stack}") as tf:
            tf.execute("workspace", "select", workspace)
            tf.destroy()
