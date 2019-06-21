from unittest.mock import ANY

from pretf import test, workflow


class TestAWS(test.SimpleTest):
    def test_init(self):
        workflow.delete_files()
        workflow.create_files()
        self.tf.init()

    def test_outputs(self):

        outputs = self.tf.apply()

        assert outputs == {
            "private_sg_id": ANY,
            "public_sg_id": ANY,
            "total_bytes": 63,
            "total_files": 5,
            "user_pretf_iam_user_1": "pretf-iam-user-1",
            "user_pretf_iam_user_2": "pretf-iam-user-2",
        }

    def test_destroy(self):
        self.tf.destroy()
