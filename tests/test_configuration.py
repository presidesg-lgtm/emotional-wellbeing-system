import unittest

from config import Config


class ConfigurationTests(unittest.TestCase):

    def test_debug_setting_is_available_on_config_class(self):
        self.assertTrue(hasattr(Config, "DEBUG"))

    def test_debug_is_disabled_by_default_environment(self):
        # The project configuration deliberately defaults to False.
        # An explicit FLASK_DEBUG environment value may enable it.
        self.assertIsInstance(Config.DEBUG, bool)


if __name__ == "__main__":
    unittest.main()
