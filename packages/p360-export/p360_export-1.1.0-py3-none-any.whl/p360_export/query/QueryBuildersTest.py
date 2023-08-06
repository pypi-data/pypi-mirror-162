import unittest
from p360_export.query.QueryBuilder import QueryBuilder
from pysparkbundle.test.PySparkTestCase import PySparkTestCase


CONFIG = {
    "params": {"export_columns": ["phone", "gen"], "mapping": {"EMAIL": "mapped_email"}},
    "personas": [
        {
            "definition_persona": [
                {
                    "attributes": [
                        {"op": "BETWEEN", "id": "col_1", "value": [0.0, 14.0]},
                        {"op": "LESS THAN", "id": "col_2", "value": 0.0},
                        {"op": "GREATER THAN", "id": "col_3", "value": 0.0},
                        {"op": "EQUALS", "id": "col_4", "value": 0.0},
                    ],
                    "op": "AND",
                }
            ],
        }
    ],
}
EXPECTED_CONDITIONS = "(\ncol_1 BETWEEN 0.0 AND 14.0\nAND\ncol_2 < 0.0\nAND\ncol_3 > 0.0\nAND\ncol_4 = 0.0\n);"


class QueryBuildersTest(PySparkTestCase):
    def expected_query(self, table_id):
        return f"SELECT phone, gen, mapped_email FROM {table_id} WHERE\n" + EXPECTED_CONDITIONS

    def test_query_builder(self):
        query_builder = QueryBuilder()
        query, table_id = query_builder.build(CONFIG)
        assert query == self.expected_query(table_id)


if __name__ == "__main__":
    unittest.main()
