import csv
import json
from os import makedirs, path
from shutil import move
from typing import Generator, List

from .dbt_schema import get_all_sources

class PreProcess:
    """
    A class to make pre-processing raw files easier. When instantiated it
    contains functions to easily read and write the file in question, and is
    passed to any pre-processing functions defined by users in their own Data
    Engineering repositories and pre-processing functions.
    """
    def __init__(self, data_provider: str, table: str, file_name: str,
                 development_dbt_root: str = None):
        """
        Initialise the object with the file details

        Parameters
        ----------
        data_provider : str
            The data provider that provided the file, which is part of the raw
            file path
        table : str
            The table that the file is related to, which is also part of the raw
            file path
        file_name : str
            The name of the file we want to pre-process. When developing 
            locally this is the path to the file, not just the file name
        development_dbt_root : str, optional
            When developing locally this is the path to the dbt folder that can
            be used to validate schemas. By default None when running this code
            on the platform and the dbt folder is in its expected path

        Raises
        ------
        Exception
            When the file does not exist at the given location
        """
        self.data_provider = data_provider
        self.table = table
        self.file_name = file_name

        # In case the column names vary by case, this aligns with the schema
        self.column_name_map = {}

        if development_dbt_root:
            self.project_root = development_dbt_root

            # Will move to a folder in the same location the file is in now
            self.write_folder = "/".join(self.file_name.split("/")[:-1]) or "."
            self.archive_folder = self.write_folder + "/before_pre_process"

            self.file_name = self.file_name.split("/")[-1]

        else:
            mnt_path = "/dbfs/mnt/"

            self.project_root = mnt_path + "dbt"

            # Move to the correct container location
            self.write_folder = \
                mnt_path + f"archive/{self.data_provider}/{self.table}"
            self.archive_folder = self.write_folder + "/before_pre_process"

        all_sources = get_all_sources(self.project_root)
        self.table_details = all_sources[data_provider]["tables"][table]

        # https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.sql.DataFrameReader.csv.html
        # https://docs.python.org/3/library/csv.html#csv-fmt-params
        spark_to_csv = {
            "sep": "delimiter",
            "escape": "escapechar",
            "lineSep": "lineterminator",
            "quote": "quotechar"
        }
        self.csv_fmt_params = {
            spark_to_csv[name]: val
            for name, val in self.table_details.get("file_details", {}).items()
            if name in spark_to_csv
        }

        if not path.exists(self.archive_folder):
            makedirs(self.archive_folder)
        
        if not path.exists(self.get_write_path()) \
                and not path.exists(self.get_raw_path()):
            raise Exception(
                f"Unable to find file at {self.get_write_path()} "
                f"or {self.get_raw_path()} to process!"
            )

        if not path.exists(self.get_raw_path()):
            move(self.get_write_path(), self.get_raw_path())
        
    def get_raw_path(self) -> str:
        """
        Get the path of the raw file to read

        Returns
        -------
        str
            The path of the file to read
        """
        return self.archive_folder + "/" + self.file_name

    def get_write_path(self, new_file_name: str=None) -> str:
        """
        Get the path to write the pre-processed file

        Parameters
        ----------
        new_file_name : str, optional
            Specify the new file name, by default None where we will re-use the
            original file name but in a new folder location

        Returns
        -------
        str
            The path of the file to write
        """
        if new_file_name:
            return self.write_folder + "/" + new_file_name
        else:
            return self.write_folder + "/" + self.file_name

    def get_filename_no_extension(self) -> str:
        """
        Get the name of the file without an extenstion (e.g. no '.csv')

        Returns
        -------
        str
            The file name without an extension            
        """
        return ".".join(self.file_name.split(".")[:-1])

    def get_raw_file(self) -> str:
        """
        Get the raw file contents as a string

        Returns
        -------
        str
            The file contents
        """
        with open(self.get_raw_path(), "r") as raw_file:
            return raw_file.read()

    def get_raw_file_by_line(self) -> Generator[str, None, None]:
        # Generator which returns the raw file, line by line
        """
        Return each line of the raw file, one at a time

        Yields
        -------
        Generator[str, None, None]
            Each line of the raw file as a string
        """
        with open(self.get_raw_path(), "r") as raw_file:
            for line in raw_file.readlines():
                yield line

    def get_file_as_json(self) -> dict:
        """
        Read the file and return a dictionary of the contents

        Returns
        -------
        dict
            The contents of the .json file

        Raises
        ------
        decode_error
            If we have trouble reading the .json file and the issue isn't the
            'UTF-8 BOM' issue, then throw the error
            
        """
        try:
            with open(self.get_raw_path(), "r") as jsonfile:
                return json.load(jsonfile)
        except json.decoder.JSONDecodeError as decode_error:
            if "Unexpected UTF-8 BOM" in decode_error.msg:
                with open(self.get_raw_path(), "rb") as jsonfile:
                    return json.loads(
                        jsonfile.read().decode("utf-8-sig").strip())
            else:
                raise decode_error

    def read_csv_as_json(self) -> Generator[dict, None, None]:
        """
        Read a .csv file with headers, returning a generator where each entry
        is a dictionary representing each row, where the keys are the column
        name and the values are the row values

        Yields
        -------
        Generator[dict, None, None]
            Each entry corresponds to a line of the .csv file
        """
        with open(self.get_raw_path(), "r") as raw_file:
            for row in csv.DictReader(raw_file, **self.csv_fmt_params):
                yield row

    def get_expected_table_fields(self) -> List[str]:
        """
        From reading the dbt schema, return a list of the expected column names
        in the processed file. This strips any ` characters added to the schema
        to make it compatible with Databricks

        Returns
        -------
        List[str]
            The column names in the dbt schema file
        """
        return [c["name"].strip("`") 
                for c in self.table_details["columns"]]

    def get_json_list_fields(self, json_list: List[dict]) -> set:
        """
        Given a list of dictionaries representing each line of data, find all
        of the columns in the full list

        Parameters
        ----------
        json_list : List[dict]
            The list of dictionaries to investigate

        Returns
        -------
        set
            All the unique key names in the whole list
        """
        known_columns = set()
        for ind_json in json_list:
            known_columns.update(ind_json.keys())
        return known_columns

    def check_table_fields(self, file_fields: List[str], 
                           expected_fields: List[str]=None) -> None:
        """
        Check that all of the proposed columns are in the dbt schema

        Parameters
        ----------
        file_fields : List[str]
            The list of columns in the file
        expected_fields : List[str], optional
            The list of fields in the schema, by default None where the fields
            are drawn from the schema file itself

        Raises
        ------
        Exception
            If there are fields in the file that the schema doesn't know about
        """
        expected_fields = expected_fields or self.get_expected_table_fields()
        schema_column_map = {
            c.lower(): c for c in expected_fields
        }
        missing_columns = [
            f for f in file_fields 
            if f not in expected_fields and f.lower() not in schema_column_map
        ]
        if missing_columns:
            raise Exception(
                f"Columns in file not in schema! {missing_columns}. "
                f"Schema columns: {expected_fields}, "
                f"file columns: {file_fields}")

        self.column_name_map = {
            f: schema_column_map[f.lower()]
            for f in file_fields 
            if f != schema_column_map[f.lower()]
        }

    def write_json_to_csv(self, json_to_write: List[dict],
                          new_file_name: str=None, write_header: bool=True,
                          **kwargs) -> None:
        """
        From the data as a list of dictionaries, write them to a .csv file at
        the appropriate location

        Parameters
        ----------
        json_to_write : List[dict]
            The data to write
        new_file_name : str, optional
            The new file name, by default None where we re-use the current file
            name. We won't overwrite the file but write to a different folder
        write_header : bool, optional
            Whether headers should be written to the file, by default True
        """
        field_names = self.get_expected_table_fields()
        self.check_table_fields(
            self.get_json_list_fields(json_to_write), field_names)
        with open(self.get_write_path(new_file_name), "w") as result:

            writer = csv.DictWriter(result, fieldnames=field_names, 
                                    **self.csv_fmt_params, **kwargs)

            if write_header:
                writer.writeheader()

            for entry in json_to_write:
                writer.writerow({
                    self.column_name_map.get(k, k): v
                    for k, v in entry.items()
                })
  
    def write_json(self, json_to_write: List[dict], 
                   new_file_name: str=None, **kwargs) -> None:
        """
        From the data as a list of dictionaries, write them to a .json file at
        the appropriate location

        Parameters
        ----------
        json_to_write : List[dict]
            The data to write
        new_file_name : str, optional
            The new file name, by default None where we re-use the current file
            name. We won't overwrite the file but write to a different folder
        """
        with open(self.get_write_path(new_file_name), "w") as result:
            for ind_json in json_to_write:
                json.dump(ind_json, result, **kwargs)
                result.write("\n")
