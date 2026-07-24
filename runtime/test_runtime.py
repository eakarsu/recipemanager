import unittest
from runtime.runtime_server import password_digest, sql_text


class RuntimeUnitTests(unittest.TestCase):
    def test_password_digest_is_deterministic_and_salted(self):
        self.assertEqual(password_digest("test-password", b"a" * 16), password_digest("test-password", b"a" * 16))
        self.assertNotEqual(password_digest("test-password", b"a" * 16), password_digest("test-password", b"b" * 16))

    def test_sql_text_encodes_untrusted_text(self):
        expression = sql_text("value' OR TRUE --")
        self.assertNotIn("OR TRUE", expression)
        self.assertTrue(expression.startswith("convert_from(decode('"))


if __name__ == "__main__":
    unittest.main()
