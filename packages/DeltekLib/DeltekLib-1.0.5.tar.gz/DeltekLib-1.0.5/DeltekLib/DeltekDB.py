# Deltek Database Library
# Copyright 2022

import os
import json

from robot.api import logger
from DatabaseLibrary import ConnectionManager, Query, Assertion


class DeltekDB(ConnectionManager, Query, Assertion):
    """
    Deltek Database Test Library

    ==Dependencies==
    | robotframework | http://robotframework.org |
    | robotframework-databaselibrary | https://pypi.org/project/robotframework-databaselibrary/ |
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    PARAM_SEPARATOR = "="
    FILE_ENCODING = "utf-8"
    TEMP_SQL_FILE = "tmp.sql"

    def __init__(self):
        super().__init__()

    def execute_sql_script_with_replacements(
            self,
            sql_file: str,
            *replacements
    ) -> str:
        """
        Runs a sql file against the database replacing strings on the contents with the supplied parameters

        :param sql_file: sql file to process
        :param replacements: strings to replace on the sql file
        :return: sql file execution output

        *Example:*
        | Execute Sql Script With Replacements  |  file.sql  |  :name=John |  :lastname=Doe  |  :middle=A |
        """
        logger.info(f'Processing sql file {os.path.abspath(sql_file)}')
        logger.info(f'Replacements are {replacements}')
        file = open(sql_file, "r")

        # Read whole SQL file to a string
        contents = file.read()
        temp_contents = contents
        for replacement in replacements:
            replace = replacement.split(self.PARAM_SEPARATOR)
            temp_contents = temp_contents.replace(replace[0], replace[1])
        logger.info(f'Saving processed sql to file {os.path.abspath(self.TEMP_SQL_FILE)}')
        with open(self.TEMP_SQL_FILE, 'w', encoding=self.FILE_ENCODING) as f:
            f.write(temp_contents)
        result = self.execute_sql_script(sqlScriptFileName=self.TEMP_SQL_FILE)
        # Close SQL file
        file.close()
        logger.info(f'Deleting temporary SQL file {os.path.abspath(self.TEMP_SQL_FILE)}')
        if os.path.exists(self.TEMP_SQL_FILE):
            os.remove(self.TEMP_SQL_FILE)
        return result

    def execute_sql_script_with_json(
        self,
        sql_file: str,
        json_file: str
    ) -> str:
        """
        Runs a sql file against the database replacing strings on the contents with values from a json file

        :param sql_file: sql file to process
        :param json_file: json file that contains the string to be replaced
        :return: sql file execution output

        *Example:*
        | Execute Sql Script With Json  |  file.sql  |  file.json |

        *Example JSON format:*
        {
            ":name": "John",
            ":lastname1": "Doe"
        }
        """
        logger.info(f'Reading from JSON file {os.path.abspath(json_file)}')
        with open(json_file) as json_file:
            data = json.load(json_file)
        parameters = []
        for key, value in data.items():
            parameters.append(f"{key}{self.PARAM_SEPARATOR}{value}")
        logger.info(f"Replacing parameters {parameters}")
        return self.execute_sql_script_with_replacements(sql_file, *parameters)
