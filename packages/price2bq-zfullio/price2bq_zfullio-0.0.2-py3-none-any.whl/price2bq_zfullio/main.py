from datetime import datetime

import pandas as pd
from bq_easy_zfullio import Client
from google.cloud.bigquery import SchemaField


def push_realty(path_file: str, bq_path_token: str, bq_project_id: str, bq_table: str) -> (datetime, datetime):
    df = pd.read_excel(path_file, sheet_name="Calls")
    df = df.rename(columns={"Дата/время": "datetime", "Объект": "object", "Входящий номер": "incoming_number",
                            "Внутренний номер": "internal_number", "Длительность ожидания": "waiting_time",
                            "Длительность разговора": "call_duration", "Рассчитанная стоимость звонка": "price",
                            "Тип объекта": "type"})
    start_date: datetime = df["datetime"].min()
    finish_date: datetime = df["datetime"].max()
    schema = [SchemaField("datetime", "DATETIME"), SchemaField("object", "STRING"),
              SchemaField("incoming_number", "STRING"), SchemaField("internal_number", "STRING"),
              SchemaField("waiting_time", "STRING"), SchemaField("call_duration", "STRING"),
              SchemaField("price", "INT64"), SchemaField("type", "STRING"), SchemaField("date_upload", "DATETIME")]
    df = df.astype({"datetime": "datetime64[ns]", "object": str, "incoming_number": str, "internal_number": str,
                    "waiting_time": str, "call_duration": str, "price": int, "type": str})
    df["date_upload"] = datetime.now()
    bq = Client(bq_path_token, bq_project_id)
    bq.upload_table(df, bq_table, schema)
    return start_date, finish_date


def push_cian(path_file: str, bq_path_token: str, bq_project_id: str, bq_table: str) -> (datetime, datetime):
    df = pd.read_excel(path_file, sheet_name="Статистика звонков")
    df = df.rename(columns={"Id": "id", "Дата": "call_datetime", "Входящий номер": "incoming_number",
                            "Подменный номер клиента": "substitute_client_number",
                            "Подменный номер застройщика": "replacement_builder_number",
                            "Исходящий номер": "outgoing_number", "Название ЖК": "object", "Статус": "status",
                            "Разговор": "call_duration", "Тариф": "tariff", "Аукцион": "auction",
                            "Cписано в баллах": "written_in_points", "Тип": "type_of_call", "Тип лида": "type_of_lead",
                            "Сумма": "final_cost"})
    df["tariff"] = df["tariff"].replace({"\xa0": ""}, regex=True).astype(int)
    df["auction"] = df["auction"].replace({"\xa0": ""}, regex=True).astype(int)
    df["final_cost"] = df["final_cost"].replace({"\xa0": ""}, regex=True).astype(int)
    df["written_in_points"] = df["auction"].replace({"\xa0": ""}, regex=True).astype(int)
    start_date: datetime = df["call_datetime"].min()
    finish_date: datetime = df["call_datetime"].max()
    schema = [SchemaField("id", "INT64"), SchemaField("call_datetime", "datetime"),
              SchemaField("incoming_number", "STRING"), SchemaField("substitute_client_number", "STRING"),
              SchemaField("replacement_builder_number", "STRING"), SchemaField("outgoing_number", "STRING"),
              SchemaField("object", "STRING"), SchemaField("status", "STRING"), SchemaField("call_duration", "STRING"),
              SchemaField("tariff", "INT64"), SchemaField("auction", "INT64"),
              SchemaField("written_in_points", "INT64"), SchemaField("type_of_call", "STRING"),
              SchemaField("type_of_lead", "STRING"), SchemaField("final_cost", "INT64"),
              SchemaField("date_upload", "DATETIME")]
    df = df.astype(
        {"call_datetime": "datetime64[ns]", "tariff": int, "auction": int, "object": str, "call_duration": str})
    df["date_upload"] = datetime.now()
    bq = Client(bq_path_token, bq_project_id)
    bq.upload_table(df, bq_table, schema)
    return start_date, finish_date
