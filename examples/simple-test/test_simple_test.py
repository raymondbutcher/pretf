from pretf import test


class TestSimpleTest(test.SimpleTest):
    """
    This shows how to use SimpleTest to write your own tests.
    It runs Terraform with the different configuration files
    in the v1 and v2 directories and makes assertions about
    their outputs.

    Each "test_*" method runs in the order in which they are
    defined. If one fails then subsequent tests do not run.

    The arguments pased into self.init(), self.destroy() and
    self.apply() in these tests get used when running Terraform.
    The "v1" and "v2" passed in become the [DIR] argument which
    tells Terraform to use that directory for the configuration.
    It always uses the current directory as the working directory
    which contains the state. This allows for testing multiple
    versions of a configuration and test what Terraform will
    do as the configuration changes.

    See https://www.terraform.io/docs/commands/init.html for more.

    """

    # Use a class level variable to store values because each test
    # method runs with a different instance of this class, so you
    # can't set new attributes on "self" in one test and access
    # it from another.
    state = {}

    def test_init(self):
        """
        Prepare the working directory by initialising and then
        destroying any resources from previous fail test runs.
        It uses the v1 configuration to initialize the working
        directory and install the required provider plugins,
        but it doesn't apply the configuration yet.

        """

        self.tf.init("v1")
        self.tf.destroy("v1")

    def test_v1(self):
        """
        Apply the v1 configuration and check its outputs.

        """

        outputs = self.tf.apply("v1")

        assert "original" in outputs
        assert outputs["original"].startswith("original-")
        self.state["original"] = outputs["original"]

        assert "additional" not in outputs

    def test_v2(self):
        """
        Apply the v2 configuration and check that the original
        resource from v1 is still there, and that an additional
        resource was created.

        """

        # The second configuration has a Pretf file "additional.tf.py" which
        # is used to create "additional.tf.json". Use "self.pretf.apply()"
        # instead of "self.tf.apply()" so the Pretf workflow will run and
        # create the file before running Terraform.

        outputs = self.pretf.apply("v2")

        assert "original" in outputs
        assert outputs["original"] == self.state["original"]

        assert "additional" in outputs
        assert outputs["additional"].startswith("additional-")

    def test_v1_again(self):
        """
        Apply the v1 configuration again and check that the original
        resource is still there, and that the additional resource
        from v2 was deleted.

        """

        outputs = self.tf.apply("v1")

        assert "original" in outputs
        assert outputs["original"] == self.state["original"]

        assert "additional" not in outputs

    def test_destroy(self):
        """
        Clean up the resources.

        """

        self.tf.destroy()
