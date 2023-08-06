import os
import unittest
from pyfonycore.bootstrap import bootstrapped_container


class LocalFileConfigGetterTest(unittest.TestCase):
    def test_file_content_matches(self):
        container = bootstrapped_container.init("test")
        config_getter = container.get("p360_export.config.config_getter")

        with open("./test_config_id.json", "w", encoding="utf8") as file_handler:
            file_handler.write('{"test": "content"}')

        config = config_getter.get(config_id="test_config_id")

        self.assertEqual(config, {"test": "content"})

        os.remove("./test_config_id.json")


if __name__ == "__main__":
    unittest.main()
