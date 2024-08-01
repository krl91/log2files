import unittest
import os
import json
from utils import Config

class TestConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a sample configuration file for testing."""
        cls.config_path = "test_config.json"
        cls.config_data = {
            "markup_element_conf": "Element",
            "markup_date_conf": "Date"
        }
        with open(cls.config_path, 'w') as f:
            json.dump(cls.config_data, f)

    @classmethod
    def tearDownClass(cls):
        """Clean up the test config file after all tests."""
        os.remove(cls.config_path)

    def test_load_config(self):
        """Test that the configuration file is loaded correctly."""
        config = Config(self.config_path)
        self.assertEqual(config.XML_PATTERN.pattern, rf'<{self.config_data["markup_element_conf"]}>.*?</{self.config_data["markup_element_conf"]}>')
        self.assertEqual(config.ELEMENT_REF_XPATH, f'.//{self.config_data["markup_date_conf"]}')

    def test_invalid_config_path(self):
        """Test that an invalid configuration path raises a FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            Config("invalid_config.json")

    def test_invalid_config_format(self):
        """Test that an invalid JSON format in the configuration raises a JSONDecodeError."""
        invalid_config_path = "invalid_config.json"
        with open(invalid_config_path, 'w') as f:
            f.write("Invalid JSON")
        with self.assertRaises(json.JSONDecodeError):
            Config(invalid_config_path)
        os.remove(invalid_config_path)

if __name__ == "__main__":
    unittest.main()

