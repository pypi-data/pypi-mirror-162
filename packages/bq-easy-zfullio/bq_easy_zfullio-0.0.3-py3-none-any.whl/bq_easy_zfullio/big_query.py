from datetime import datetime
from enum import Enum

from google.cloud import bigquery
from google.oauth2 import service_account


class DateForm(Enum):
    """Форматы дат используемые в проекте"""
    Y_M_D = "%Y-%m-%d"
    Y_M_D_H_M_S = "%Y-%m-%d %H:%M:%S"
    D_M_Y_H_M = "%d.%m.%y %H:%M"


class Client:

    def __init__(self, token_path: str, project_id: str):
        credentials = service_account.Credentials.from_service_account_file(token_path)
        self.client = bigquery.Client(project_id, credentials=credentials)

    def upload_table(self, df, table_id: str, schema):
        job_config = bigquery.LoadJobConfig()
        job_config.schema = schema
        job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()
        assert job.errors is None, f"Ошибка при отправке данных: {job.errors}"

    def delete_row(self, table: str, date_column: str, start_date: str | datetime, finish_date: str | datetime):
        start_date: str = self.__normalize_date(start_date)
        finish_date: str = self.__normalize_date(finish_date)
        query = f"DELETE FROM {table} where {date_column} >= '{start_date}' AND  {date_column} <= '{finish_date}'"
        job = self.client.query(query)
        job.result()
        assert job.errors is None, f"Ошибка при удалении данных: {job.errors}"

    @staticmethod
    def __normalize_date(date: str | datetime) -> str:
        return date.strftime(DateForm.Y_M_D.value) if type(date) == datetime else date
