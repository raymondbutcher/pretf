import pytest

from pretf import test


class TestVersionedRootModules(test.SimpleTest):
    @pytest.mark.parametrize(
        "env", [
            "dev",
            "prod",
        ],
    )
    def test_init(self, env):
        self.pretf(env).init()

    @pytest.mark.parametrize(
        "env,expected", [
            ("dev", {"first": "dev", "second": "dev", "third": "dev"}),
            ("prod", {"first": "prod", "second": "prod"}),
        ],
    )
    def test_apply(self, env, expected):
        outputs = self.pretf(env).apply()
        assert outputs == expected

    @test.always
    @pytest.mark.parametrize(
        "env", [
            "dev",
            "prod",
        ],
    )
    def test_destroy(self, env):
        self.pretf(env).destroy()
