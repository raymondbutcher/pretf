from unittest.mock import ANY

from pretf import test


class TestAWS(test.SimpleTest):
    def test_init(self):
        self.pretf.init()

    def test_outputs(self):

        outputs = self.pretf.apply()

        assert outputs == {
            "private_sg_id": ANY,
            "public_sg_id": ANY,
            "total_bytes": 63,
            "total_files": 5,
            "user_pretf_iam_user_1": "pretf-iam-user-1",
            "user_pretf_iam_user_2": "pretf-iam-user-2",
        }

    def test_destroy(self):
        self.pretf.destroy()
