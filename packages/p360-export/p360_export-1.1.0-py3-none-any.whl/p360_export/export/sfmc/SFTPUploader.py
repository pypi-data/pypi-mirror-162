import os
from pyspark.sql import DataFrame
from p360_export.export.sfmc.SFMCData import SFMCData

from p360_export.export.sfmc.SFTPClientGetter import SFTPClientGetter


class SFTPUploader:
    def __init__(self, sftp_client_getter: SFTPClientGetter):
        self.__sftp_client_getter = sftp_client_getter

    def __get_csv_path(self, audience_name: str) -> str:
        return f"/dbfs/tmp/{audience_name}.csv"

    def upload(self, df: DataFrame, sfmc_data: SFMCData):
        sftp_client = self.__sftp_client_getter.get(sfmc_data=sfmc_data)

        csv_path = self.__get_csv_path(sfmc_data.audience_name)

        df.toPandas().to_csv(csv_path)  # pyre-ignore[16]

        sftp_client.put(csv_path, f"/Import/{sfmc_data.audience_name}.csv")
        sftp_client.close()

        os.remove(csv_path)
