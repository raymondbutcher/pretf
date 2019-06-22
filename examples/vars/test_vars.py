from pretf import test


class TestVars(test.SimpleTest):
    def test_create(self):
        self.pretf.init()

    def test_outputs(self):
        outputs = self.pretf.apply()
        assert outputs == {
            "five": 5,
            "four": 4,
            "one": 1,
            "seven": ["7a", "7b"],
            "six": ["six1", "six2"],
            "three": 3,
            "two_attr": 2,
            "two_dict": 2,
        }

    @test.always
    def test_destroy(self):
        self.pretf.destroy()
