import unittest
from datetime import time

import pandas as pd
from service.clean_data import CleanData


class TestCleanData(unittest.TestCase):
    def setUp(self):
        # Create sample dataframes for testing
        self.df_ihm = pd.DataFrame(
            {
                "maquina_id": [1, 2, 3],
                "data_registro": ["2022-01-01", "2022-01-02", "2022-01-03"],
                "hora_registro": ["10:00:00", "11:00:00", "12:00:00"],
                "linha": [1, 2, 3],
            }
        )

        self.df_info = pd.DataFrame(
            {
                "maquina_id": [1, 2, 3],
                "data_registro": ["2022-01-01", "2022-01-02", "2022-01-03"],
                "hora_registro": ["10:00:00", "11:00:00", "12:00:00"],
                "turno": ["MAT", "VES", "NOT"],
                "status": ["true", "false", "true"],
            }
        )

        self.df_info_production = pd.DataFrame(
            {
                "maquina_id": [1, 2, 3],
                "data_registro": ["2022-01-01", "2022-01-02", "2022-01-03"],
                "hora_registro": ["10:00:00", "11:00:00", "12:00:00"],
                "turno": ["MAT", "VES", "NOT"],
                "linha": [1, 2, 3],
            }
        )

        self.clean_data = CleanData(self.df_ihm, self.df_info, self.df_info_production)

    def test_clean_basics(self):
        cleaned_df = self.clean_data._CleanData__clean_basics(self.df_ihm)
        self.assertEqual(len(cleaned_df), 3)  # No duplicate values
        self.assertTrue(all(cleaned_df["maquina_id"].notnull()))  # No missing values
        self.assertTrue(
            all(cleaned_df["data_registro"].dtypes == "datetime64[ns]")
        )  # Correct data type
        self.assertTrue(all(cleaned_df["hora_registro"].dtypes == "object"))  # Correct data type
        self.assertTrue(all(cleaned_df["linha"].notnull()))  # No missing values
        self.assertTrue(all(cleaned_df["linha"].dtypes == "int64"))  # Correct data type
        self.assertFalse("recno" in cleaned_df.columns)  # "recno" column removed
        self.assertFalse(any(cleaned_df["linha"] == 0))  # No rows where "linha" is 0

    def test_clean_info(self):
        cleaned_df = self.clean_data._CleanData__clean_info(self.df_info)
        self.assertTrue(all(cleaned_df["maquina_id"].notnull()))  # No missing values
        self.assertTrue(
            all(cleaned_df["turno"] != "VES" or cleaned_df["maquina_id"].duplicated())
        )  # No rows where "turno" is "VES" and "maquina_id" changes
        mask = (
            (cleaned_df["turno"] == "VES")
            & (cleaned_df["hora_registro"] >= time(0, 0, 0))
            & (cleaned_df["hora_registro"] <= time(0, 5, 0))
        )
        self.assertTrue(
            all(
                cleaned_df.loc[mask, "data_registro"]
                == pd.to_datetime(cleaned_df.loc[mask, "data_registro"]) - pd.Timedelta(days=1)
            )
        )
        self.assertTrue(all(cleaned_df.loc[mask, "hora_registro"] == time(23, 59, 59)))
        self.assertTrue(all(cleaned_df["linha"].notnull()))  # No missing values
        self.assertTrue(all(cleaned_df["linha"].dtypes == "int64"))  # Correct data type
        self.assertTrue(
            all(cleaned_df["linha"].duplicated())
        )  # Rows sorted by "linha", "data_registro", and "hora_registro"
        self.assertTrue(all(cleaned_df.index == range(len(cleaned_df))))  # Index reset

    def test_clean_production(self):
        cleaned_df = self.clean_data._CleanData__clean_production(self.df_info_production)
        self.assertTrue(all(cleaned_df["turno_order"].notnull()))  # No missing values
        self.assertTrue(all(cleaned_df["turno_order"].dtypes == "int64"))  # Correct data type
        self.assertTrue(all(cleaned_df["linha"].notnull()))  # No missing values
        self.assertTrue(
            all(cleaned_df["linha"].duplicated())
        )  # Rows sorted by "linha", "data_registro", and "turno_order"
        self.assertFalse("turno_order" in cleaned_df.columns)  # "turno_order" column removed
        self.assertTrue(all(cleaned_df.index == range(len(cleaned_df))))  # Index reset

    def test_clean_data(self):
        cleaned_ihm, cleaned_info, cleaned_info_production = self.clean_data.clean_data()
        self.assertEqual(len(cleaned_ihm), 3)  # No duplicate values
        self.assertTrue(all(cleaned_ihm["maquina_id"].notnull()))  # No missing values
        self.assertTrue(
            all(cleaned_ihm["data_registro"].dtypes == "datetime64[ns]")
        )  # Correct data type
        self.assertTrue(all(cleaned_ihm["hora_registro"].dtypes == "object"))  # Correct data type
        self.assertTrue(all(cleaned_ihm["linha"].notnull()))  # No missing values
        self.assertTrue(all(cleaned_ihm["linha"].dtypes == "int64"))  # Correct data type
        self.assertFalse("recno" in cleaned_ihm.columns)  # "recno" column removed
        self.assertFalse(any(cleaned_ihm["linha"] == 0))  # No rows where "linha" is 0

        self.assertTrue(all(cleaned_info["maquina_id"].notnull()))  # No missing values
        self.assertTrue(
            all(cleaned_info["turno"] != "VES" or cleaned_info["maquina_id"].duplicated())
        )  # No rows where "turno" is "VES" and "maquina_id" changes
        mask = (
            (cleaned_info["turno"] == "VES")
            & (cleaned_info["hora_registro"] >= time(0, 0, 0))
            & (cleaned_info["hora_registro"] <= time(0, 5, 0))
        )
        self.assertTrue(
            all(
                cleaned_info.loc[mask, "data_registro"]
                == pd.to_datetime(cleaned_info.loc[mask, "data_registro"]) - pd.Timedelta(days=1)
            )
        )
        self.assertTrue(all(cleaned_info.loc[mask, "hora_registro"] == time(23, 59, 59)))
        self.assertTrue(all(cleaned_info["linha"].notnull()))  # No missing values
        self.assertTrue(all(cleaned_info["linha"].dtypes == "int64"))  # Correct data type
        self.assertTrue(
            all(cleaned_info["linha"].duplicated())
        )  # Rows sorted by "linha", "data_registro", and "hora_registro"
        self.assertTrue(all(cleaned_info.index == range(len(cleaned_info))))  # Index reset

        self.assertTrue(all(cleaned_info_production["turno_order"].notnull()))  # No missing values
        self.assertTrue(
            all(cleaned_info_production["turno_order"].dtypes == "int64")
        )  # Correct data type
        self.assertTrue(all(cleaned_info_production["linha"].notnull()))  # No missing values
        self.assertTrue(
            all(cleaned_info_production["linha"].duplicated())
        )  # Rows sorted by "linha", "data_registro", and "turno_order"
        self.assertFalse(
            "turno_order" in cleaned_info_production.columns
        )  # "turno_order" column removed
        self.assertTrue(
            all(cleaned_info_production.index == range(len(cleaned_info_production)))
        )  # Index reset


if __name__ == "__main__":
    unittest.main()
