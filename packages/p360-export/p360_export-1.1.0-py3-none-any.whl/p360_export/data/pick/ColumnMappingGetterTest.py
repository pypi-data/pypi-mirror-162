import unittest

from p360_export.data.pick.ColumnMappingGetter import ColumnMappingGetter


class ColumnMappingGetterTest:
    def test_column_mapping_getter(self):
        config = {"params": {"mapping": {"email: email_column"}}}
        assert ColumnMappingGetter().get(config) == {"email": "email_column"}


if __name__ == "__main__":
    unittest.main()
