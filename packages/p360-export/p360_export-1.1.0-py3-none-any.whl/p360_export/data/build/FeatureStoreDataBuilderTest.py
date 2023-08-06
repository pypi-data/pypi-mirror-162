import unittest
from unittest.mock import patch
from pysparkbundle.test.PySparkTestCase import PySparkTestCase

from p360_export.data.build.FeatureStoreDataBuilder import FeatureStoreDataBuilder

CONFIG = {
    "params": {"export_columns": ["phone", "id"], "mapping": {"email": "mapped_email"}},
    "personas": [
        {
            "definition_persona": [
                {
                    "attributes": [
                        {"op": "BETWEEN", "id": "col_1", "value": [0.0, 14.0]},
                        {"op": "LESS THAN", "id": "col_2", "value": 0.0},
                    ],
                    "op": "AND",
                }
            ],
        }
    ],
}


class FeatureStoreDataBuilderTest(PySparkTestCase):
    @patch("featurestorebundle.feature.FeatureStore.FeatureStore")
    @patch("p360_export.data.build.FeatureStoreDataBuilder.get_entity")
    def test_data_getter_gets_correct_data(self, _, mock_fs):
        def get_latest_attributes_(_, attributes):
            df_complete = self.spark.createDataFrame(
                [
                    ["123", 1, "a@b.c", 1, 1, 1],
                    ["456", 2, "b@c.d", 2, 2, 2],
                    ["789", 1, "c@d.e", 5, 3, 4],
                ],
                ["phone", "id", "mapped_email", "foo", "col_1", "col_2"]
            )

            return df_complete.select(attributes)

        mock_fs.get_latest_attributes.side_effect = get_latest_attributes_

        df_expected = self.spark.createDataFrame(
            [
                ["123", 1, "a@b.c", 1, 1],
                ["456", 2, "b@c.d", 2, 2],
                ["789", 1, "c@d.e", 3, 4],
            ],
            ["phone", "id", "mapped_email", "col_1", "col_2"]
        )

        feature_store_data_builder = FeatureStoreDataBuilder(mock_fs)

        self.compare_dataframes(df_expected, feature_store_data_builder.build(config=CONFIG), sort_keys=["id"])


if __name__ == "__main__":
    unittest.main()
