import json
import posixpath

from persona_export.configuration import Configuration
from persona_export.exports.BaseExport import BaseExport
import pyspark.sql.functions as F

from persona_export.sql.QueryBuilder import query_build


class FacebookExporter(BaseExport):
    mapping = {
        "customer_phone": "phone",  # 00420 az tri sloupce
        "customer_email": "email",  # az tri sloupce
        "customer_permanent_city": "ct",
        "customer_permanent_postal_code": "zip",
        "customer_permanent_country": "country",
        "customer_contact_city": "ct",
        "customer_contact_postal_code": "zip",
        "customer_contact_country": "country",
        "customer_date_of_birth": "dob",  # replace (. za nic)
        "customer_first_name": "fn",  # i s diakritikou
        "customer_surname": "ls",
        "customer_sex": "gen",
        "gender": "gen",
        "phoneNumber": "phone"
    }

    def __init__(
            self,
            configuration: Configuration
    ):
        self.data_save_path = posixpath.join(configuration.storage_path, 'Facebook')
        super().__init__(configuration)

        print(f"init of {__name__}")

    def get_existing_columns(self):
        """It takes desired columns and compare it with existing columns. Returns only unique existing columns"""
        if isinstance(self.configuration.get('params')['export_columns'], str):
            desired_columns = set(
                word.lower() for word in (eval(self.configuration.get('params')['export_columns'])) + ['client_id'])
        else:
            desired_columns = set(
                word.lower() for word in (self.configuration.get('params')['export_columns'] + ['client_id']))

        mapping_columns = self.mapping_from_config().values()
        columns = {*desired_columns, *mapping_columns}
        dataframe_columns = set(word.lower() for word in self.join_data_sources().columns)
        return list(dataframe_columns.intersection(columns))

    def rename_columns_from_config(self, df):
        for after, before in self.mapping_from_config().items():
            df = df.withColumnRenamed(before, after)
        return df

    def mapping_columns(self, df):
        return df.select([F.col(c).alias(self.mapping.get(c, c)) for c in df.columns])

    def mapping_from_config(self):
        mapping = self.configuration.get('params')['mapping']
        if isinstance(mapping, dict):
            return mapping
        else:
            return json.loads(mapping)

    def delete_surplus_columns(self, df):
        facebook_columns = ["client_id", "email", "phone", "gen", "doby", "dobm", "dobd",
                            "ln", "fn", "fi", "st", "ct", "zip", "country", "madid"]
        columns_to_drop = []
        for x in df.columns:
            if x not in facebook_columns:
                columns_to_drop.append(x)
        return df.drop(*columns_to_drop)

    def hash_data(self, x):
        return F.sha2(F.col(x).cast('string'), 256)

    def save_data(self, df, unix_time, persona):
        persona = self.configuration.get('personas')
        if persona:
            name = persona['persona_name']
            persona_id = persona['persona_id']
            csv_location = self.data_location(name, unix_time, persona_id)
        else:
            csv_location = self.data_location(self.configuration.get('id'), unix_time, None)

        df.coalesce(1).write.option("maxRecordsPerFile", 9995).csv(path=csv_location, mode="append", header="true")

    def save_persona(self, persona, unix_time):
        if self.configuration.get('personas'):
            persona_query = json.dumps(persona['definition_persona'])
            base_query = json.dumps(persona['definition_base'])

            definition_persona = query_build(json.loads(persona_query))
            definition_base = query_build(json.loads(base_query))

            df = self.define_select(definition_persona, definition_base)
        else:
            df = self.join_data_sources().select(self.get_existing_columns())

        df_renamed = self.mapping_columns(self.rename_columns_from_config(df))
        df_end = self.delete_surplus_columns(df_renamed)
        df_last = df_end.select(
            *[self.hash_data(column).name(column) if column != 'client_id' else column for column in df_end.columns])

        self.save_data(df_last, unix_time, persona)

    def save_table(self):
        unix_time = self.configuration.get('created_at')
        if self.configuration.get('personas'):
            for persona in self.configuration.get('personas'):
                self.save_persona(persona, unix_time)
        else:
            self.save_persona(None, unix_time)
