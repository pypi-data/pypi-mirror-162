import json
import posixpath

from persona_export.configuration.Configuration import Configuration

from persona_export.exports.FacebookExporter import FacebookExporter
from persona_export.sql.QueryBuilder import query_build


class FacebookManualExporter(FacebookExporter):

    def __init__(self, configuration: Configuration):
        super().__init__(configuration)
        self.data_save_path = posixpath.join(configuration.storage_path, 'Facebook_manual/')

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

        self.save_data(df_end, unix_time, persona)

    def save_data(self, df, unix_time, persona):
        name = persona['persona_name']
        persona_id = persona['persona_id']
        data_path = self.data_location(name, unix_time, persona_id)

        if self._is_attributes():
            df.coalesce(1).write.csv(path=data_path, mode="overwrite", header="true")
        else:
            df.coalesce(1).write.csv(path=data_path, mode="append", header="true")
        self.delete_temporary_file()