from pretf import test


class TestJinja(test.SimpleTest):
    def test_init(self):
        self.pretf.init()

    def test_outputs(self):
        outputs = self.pretf.apply()
        assert outputs.keys() == {"byte_length", "from_jinja", "from_python", "from_terraform"}
        assert outputs["byte_length"] == 12
        assert outputs["from_jinja"].startswith("jinja-")
        assert outputs["from_python"].startswith("python-")
        assert outputs["from_terraform"].startswith("terraform-")

    @test.always
    def test_destroy(self):
        self.pretf.destroy()
