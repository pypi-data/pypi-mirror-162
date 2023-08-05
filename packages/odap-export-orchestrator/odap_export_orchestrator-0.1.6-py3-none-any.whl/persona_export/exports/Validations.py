"""
1) cesty existuji
2) najdu vsechny sloupecky - pokud je to v definici -> skoncit, jinak vratit vse, co jsem schopna dohledat
3) je persona ve spravnem formatu - ma 4 povinne parametry a jsou tam nejake persony?
4) ? je tam mapping, ale zadny export column
5) query mi nevrati zadny data -> neukoncit, ale nekam zalogovat
"""
import logging
import os


class Validations:

    # 1
    def is_path_valid(self, data_path):
        if os.path.exists(data_path):
            return True

        logging.warning("Path to data doesn't exist")
        raise NameError("Path doesn't exist")

    # 2a
    def select_existing_export_columns(self, cols, dataframe):
        present_columns = []
        for col in cols:
            if col in dataframe.columns:
                present_columns.append(col)
        return present_columns

    # 2b
    def is_definition_columns_valid(self, col, dataframe):
        if col in dataframe.columns:
            return True

        logging.warning('Columns are not found in dataframe.')
        raise ValueError('Columns in definitions are not found in database.')

    # 3
    def is_persona_valid(self, persona):
        required_keys = ["persona_name", "persona_id", "definition_persona", "definition_base"]
        if all([key in persona for key in required_keys]):
            return True

        logging.warning("Personas doesn't have all necessary parameters")
        raise AttributeError("Persona doesn't have all necessary parameters")

    # 5
    def empty_select(self, df):
        if not df.take(1).isEmpty:
            return True

        logging.warning("Query doesn't return any row")
        raise ValueError("Selected parameters returned empty result.")
