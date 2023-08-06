import json
from multiprocessing import AuthenticationError
import ssl
import copy
import re
import logging
import os
import platform
import tempfile
from pathlib import Path
from typing import Union, Dict
from collections import namedtuple
import xml.etree.ElementTree as ET
import pandas as pd
import requests
from retrying import retry
from polly.help import example, doc
from polly import constants as const
from polly import helpers
from polly.auth import Polly
from polly.constants import (
    DATA_TYPES,
    FILE_FORMAT_CONSTANTS_URL,
    REPORT_GENERATION_SUPPORTED_REPOS,
)
from polly.errors import (
    QueryFailedException,
    UnfinishedQueryException,
    InvalidParameterException,
    error_handler,
    is_unfinished_query_error,
    paramException,
    wrongParamException,
    apiErrorException,
    invalidApiResponseException,
    invalidDataException,
    BadRequestError,
    AccessDeniedError,
    ResourceNotFoundError,
    UnauthorizedException,
    UnsupportedRepositoryException,
)
from datetime import datetime
import numpy as np
import datapane as dp
import plotly.express as px
from polly.index_schema_level_conversion_const import (
    schema_levels,
    schema_table_names,
)

import polly.http_response_codes as http_codes

QUERY_API_V1 = "v1"
QUERY_API_V2 = "v2"


class OmixAtlas:
    """
    OmixAtlas class enables users to create, update an Omixatlas, get summary of an Omixatlas, get schema of \
data at dataset, sample and feature level, query metadata, download data, save file to workspace and data \
converter functions.


    ``Args:``
        |  ``token (str):`` token copy from polly.

    We can initialize a OmixAtlas class object using.


    .. code::


            from polly.omixatlas import OmixAtlas
            omixatlas = OmixAtlas(token)

    If you are authorised then you can initialize object without token to know about :ref:`authentication <auth>`.
    """

    example = classmethod(example)
    doc = classmethod(doc)

    def __init__(self, token=None, env="", default_env="polly") -> None:
        # check if COMPUTE_ENV_VARIABLE present or not
        # if COMPUTE_ENV_VARIABLE, give priority
        env = helpers.get_platform_value_from_env(
            const.COMPUTE_ENV_VARIABLE, default_env, env
        )
        self.session = Polly.get_session(token, env=env)
        self.base_url = f"https://v2.api.{self.session.env}.elucidata.io"
        self.discover_url = f"https://api.discover.{self.session.env}.elucidata.io"
        self.elastic_url = (
            f"https://api.datalake.discover.{self.session.env}.elucidata.io/elastic/v2"
        )
        self.resource_url = f"{self.base_url}/v1/omixatlases"

    def get_all_omixatlas(
        self, query_api_version="v2", count_by_source=True, count_by_data_type=True
    ):
        """
        .. _targetget:

        This function will return the summary of all the Omixatlas on Polly which the user has access to.

        ``Args:``
            |  None

        ``Returns:``
            It will return a list of objects like this.

            .. code::


                    {
                    'repo_name': 'repo',
                    'repo_id': '1646',
                    'indexes': {
                    'gct_metadata': 'repo_gct_metadata',
                        'h5ad_metadata': 'repo_h5ad_metadata',
                        'csv': 'repo_csv',
                        'files': 'repo_files',
                        'json': 'repo_json',
                        'ipynb': 'repo_ipynb',
                        'gct_data': 'repo_gct_data',
                        'h5ad_data': 'repo_h5ad_data'
                        },
                    'diseases': [],
                    'organisms': [],
                    'sources': [],
                    'datatypes': [],
                    'dataset_count': 0,
                    'disease_count': 0,
                    'tissue_count': 0,
                    'organism_count': 0,
                    'cell_line_count': 0,
                    'cell_type_count': 0,
                    'drug_count': 0,
                    'data_type_count': 0,
                    'data_source_count': 0,
                    'sample_count': 0,
                    'normal_sample_count': 0
                    }

        | To use this function import Omixatlas class and make a object.


        .. code::


                from polly.omixatlas import OmixAtlas
                omixatlas = OmixAtlas(token)
                # to use OmixAtlas class functions
                omixatlas.get_all_omixatlas()

        """

        url = self.resource_url
        if query_api_version == "v2":
            if count_by_source and count_by_data_type:
                params = {
                    "summarize": "true",
                    "v2": "true",
                    "count_by_source": "true",
                    "count_by_data_type": "true",
                }
            elif count_by_source:
                params = {"summarize": "true", "v2": "true", "count_by_source": "true"}
            elif count_by_data_type:
                params = {
                    "summarize": "true",
                    "v2": "true",
                    "count_by_data_type": "true",
                }
            else:
                params = {
                    "summarize": "true",
                    "v2": "true",
                }
        elif query_api_version == "v1":
            params = {"summarize": "true"}
        else:
            raise wrongParamException("Incorrect query param version passed")
        response = self.session.get(url, params=params)
        error_handler(response)
        return response.json()

    def omixatlas_summary(
        self,
        key: str,
        query_api_version="v2",
        count_by_source=True,
        count_by_data_type=True,
    ):
        """
        This function will return you a object that contain information about a given Omixatlas.

        ``Args:``
            |  ``key (str) :`` repo_id or repo_name.

        ``Returns:``
            It will return a object like this.

            .. code::


                    {
                    'repo_name': 'repo',
                    'repo_id': '1646',
                    'indexes': {
                        'gct_metadata': 'repo_gct_metadata',
                        'h5ad_metadata': 'repo_h5ad_metadata',
                        'csv': 'repo_csv',
                        'files': 'repo_files',
                        'json': 'repo_json',
                        'ipynb': 'repo_ipynb',
                        'gct_data': 'repo_gct_data',
                        'h5ad_data': 'repo_h5ad_data'
                        },
                    'diseases': [],
                    'organisms': [],
                    'sources': [],
                    'datatypes': [],
                    'dataset_count': 0,
                    'disease_count': 0,
                    'tissue_count': 0,
                    'organism_count': 0,
                    'cell_line_count': 0,
                    'cell_type_count': 0,
                    'drug_count': 0,
                    'data_type_count': 0,
                    'data_source_count': 0,
                    'sample_count': 0,
                    'normal_sample_count': 0
                    }

        |  To use this function see the code below.

        .. code::


                from polly.omixatlas import OmixAtlas
                omixatlas = OmixAtlas(token)
                # to use OmixAtlas class functions
                omixatlas.omixatlas_summary(key)
        """

        url = f"{self.resource_url}/{key}"
        if query_api_version == "v2":
            if count_by_source and count_by_data_type:
                params = {
                    "summarize": "true",
                    "v2": "true",
                    "count_by_source": "true",
                    "count_by_data_type": "true",
                }
            elif count_by_source:
                params = {"summarize": "true", "v2": "true", "count_by_source": "true"}
            elif count_by_data_type:
                params = {
                    "summarize": "true",
                    "v2": "true",
                    "count_by_data_type": "true",
                }
            else:
                params = {
                    "summarize": "true",
                    "v2": "true",
                }
        elif query_api_version == "v1":
            params = {"summarize": "true"}
        else:
            raise wrongParamException("Incorrect query param version passed")
        if params:
            response = self.session.get(url, params=params)
        error_handler(response)
        return response.json()

    def get_omixatlas(self, key: str):
        """
        This function will return a omixatlas repository in polly.

        ``Args:``
            |  ``key:`` repo name or repo id.

        ``Returns:``
            It will return a objects like this.

            .. code::


                    {
                    'repo_name': 'repo',
                    'repo_id': '1646',
                    'indexes': {
                    'gct_metadata': 'repo_gct_metadata',
                        'h5ad_metadata': 'repo_h5ad_metadata',
                        'csv': 'repo_csv',
                        'files': 'repo_files',
                        'json': 'repo_json',
                        'ipynb': 'repo_ipynb',
                        'gct_data': 'repo_gct_data',
                        'h5ad_data': 'repo_h5ad_data'
                        },
                    'diseases': [],
                    'organisms': [],
                    'sources': [],
                    'datatypes': [],
                    'dataset_count': 0,
                    'disease_count': 0,
                    'tissue_count': 0,
                    'organism_count': 0,
                    'cell_line_count': 0,
                    'cell_type_count': 0,
                    'drug_count': 0,
                    'data_type_count': 0,
                    'data_source_count': 0,
                    'sample_count': 0,
                    'normal_sample_count': 0
                    }

        | To use this function import Omixatlas class and make a object.


        .. code::


                from polly.omixatlas import OmixAtlas
                omixatlas = OmixAtlas(token)
                # to use OmixAtlas class functions
                omixatlas.get_omixatlas('9')

        """
        url = f"{self.resource_url}/{key}"
        response = self.session.get(url)
        error_handler(response)
        return response.json()

    def query_metadata(
        self,
        query: str,
        experimental_features=None,
        query_api_version=QUERY_API_V2,
        page_size=None,  # Note: do not increase page size more than 999
    ):
        """
        This function will return a dataframe containing the datasets or sample as per the SQL query.

        ``Args:``
            |  ``query (str) :`` sql query  on  omixatlas for example - "SELECT * FROM geo.datasets".
            |  ``experimental_features :`` :ref:`this section includes in querying metadata <target>`.
            |  ``query_api_version (str) :`` v1 or v2.
            |  ``page_size (int):`` page size for query.



        ``Returns:``
            |  It will return a dataframe that contains metadata information as defined in the schema.

        ``Errors:``
            |  ``UnfinishedQueryException:`` when query has not finised the execution.
            |  ``QueryFailedException:`` when query failed to execute.


        .. code::


                from polly.omixatlas import OmixAtlas
                omixatlas = OmixAtlas(token)
                # to use OmixAtlas class functions
                query = "SELECT * FROM geo.datasets"
                results = omixatlas.query_metadata(query, query_api_version="v2")
                print(results)

        |  To know about quering metadata :ref:`Querying metadata <targetq>`.
        """

        max_page_size = 999
        if page_size is not None and page_size > max_page_size:
            raise ValueError(
                f"The maximum permitted value for page_size is {max_page_size}"
            )
        elif page_size is None and query_api_version != QUERY_API_V2:
            page_size = 500

        queries_url = f"{self.resource_url}/queries"
        queries_payload = {
            "data": {
                "type": "queries",
                "attributes": {"query": query, "query_api_version": query_api_version},
            }
        }
        if experimental_features is not None:
            queries_payload.update({"experimental_features": experimental_features})

        response = self.session.post(queries_url, json=queries_payload)
        error_handler(response)

        query_data = response.json().get("data")
        query_id = query_data.get("id")
        return self._process_query_to_completion(query_id, query_api_version, page_size)

    @retry(
        retry_on_exception=is_unfinished_query_error,
        wait_exponential_multiplier=500,  # Exponential back-off starting 500ms
        wait_exponential_max=10000,  # After 10s, retry every 10s
        stop_max_delay=900000,  # Stop retrying after 900s (15m)
    )
    def _process_query_to_completion(
        self, query_id: str, query_api_version: str, page_size: Union[int, None]
    ):
        queries_url = f"{self.resource_url}/queries/{query_id}"
        response = self.session.get(queries_url)
        error_handler(response)

        query_data = response.json().get("data")
        query_status = query_data.get("attributes", {}).get("status")
        if query_status == "succeeded":
            return self._handle_query_success(query_data, query_api_version, page_size)
        elif query_status == "failed":
            self._handle_query_failure(query_data)
        else:
            raise UnfinishedQueryException(query_id)

    def _handle_query_failure(self, query_data: dict):
        fail_msg = query_data.get("attributes").get("failure_reason")
        raise QueryFailedException(fail_msg)

    def _handle_query_success(
        self, query_data: dict, query_api_version: str, page_size: Union[int, None]
    ) -> pd.DataFrame:
        query_id = query_data.get("id")

        details = []
        time_taken_in_ms = query_data.get("attributes").get("exec_time_ms")
        if isinstance(time_taken_in_ms, int):
            details.append("time taken: {:.2f} seconds".format(time_taken_in_ms / 1000))
        data_scanned_in_bytes = query_data.get("attributes").get("data_scanned_bytes")
        if isinstance(data_scanned_in_bytes, int):
            details.append(
                "data scanned: {:.3f} MB".format(data_scanned_in_bytes / (1024**2))
            )

        if details:
            detail_str = ", ".join(details)
            print("Query execution succeeded " f"({detail_str})")
        else:
            print("Query execution succeeded")

        if query_api_version != QUERY_API_V2 or page_size is not None:
            return self._fetch_results_as_pages(query_id, page_size)
        else:
            return self._fetch_results_as_file(query_id)

    def _fetch_results_as_pages(self, query_id, page_size):
        first_page_url = (
            f"{self.resource_url}/queries/{query_id}" f"/results?page[size]={page_size}"
        )
        response = self.session.get(first_page_url)
        error_handler(response)
        result_data = response.json()
        rows = [row_data.get("attributes") for row_data in result_data.get("data")]

        all_rows = rows

        message = "Fetched {} rows"
        print(message.format(len(all_rows)), end="\r")

        while (
            result_data.get("links") is not None
            and result_data.get("links").get("next") is not None
            and result_data.get("links").get("next") != "null"
        ):
            next_page_url = self.base_url + result_data.get("links").get("next")
            response = self.session.get(next_page_url)
            error_handler(response)
            result_data = response.json()
            if result_data.get("data"):
                rows = [
                    row_data.get("attributes") for row_data in result_data.get("data")
                ]
            else:
                rows = []
            all_rows.extend(rows)
            print(message.format(len(all_rows)), end="\r")

        # Blank line resets console line start position
        print()

        return pd.DataFrame(all_rows)

    def _fetch_results_as_file(self, query_id):
        results_file_req_url = (
            f"{self.resource_url}/queries/{query_id}/results?action=download"
        )
        response = self.session.get(results_file_req_url)
        error_handler(response)
        result_data = response.json()

        results_file_download_url = result_data.get("data", {}).get("download_url")
        if (
            results_file_download_url is None
            or results_file_download_url == "Not available"
        ):
            # The user is probably executing SHOW TABLES or DESCRIBE query
            return self._fetch_results_as_pages(query_id, 100)

        def _local_temp_file_path(filename):
            temp_dir = Path(
                "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
            ).absolute()

            temp_file_path = os.path.join(temp_dir, filename)
            if Path(temp_file_path).exists():
                os.remove(temp_file_path)

            return temp_file_path

        def _download_file_stream(download_url, _local_file_path):
            with requests.get(download_url, stream=True, headers={}) as r:
                r.raise_for_status()
                with open(_local_file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

        local_file_path = _local_temp_file_path(f"{query_id}.csv")
        _download_file_stream(results_file_download_url, local_file_path)

        columns_in_csv, conv_columns = self._get_columns_with_array_dtype(
            local_file_path
        )
        list_conv = lambda x: x.strip("[]").split(",")
        converter_dict = {}
        for column_name in columns_in_csv:
            if column_name in conv_columns:
                converter_dict[column_name] = list_conv

        data_df = pd.read_csv(local_file_path, converters=converter_dict)

        print(f"Fetched {len(data_df.index)} rows")

        return data_df

    def _get_columns_with_array_dtype(self, local_file_path: str) -> list:
        """
        Return all the columns from the csv file
        whose datatype is array
        """
        with open(local_file_path, "rb"):
            df = pd.read_csv(local_file_path)
            columns_in_csv = list(df.columns)
            conv_columns = []
            for index, row in df.iterrows():
                for col in columns_in_csv:
                    value = row[col]
                    if isinstance(value, str):
                        if re.search(r"\[(.*?)\]", value):
                            conv_columns.append(col)
                        elif value == "[]":
                            conv_columns.append(col)
                break
        return columns_in_csv, conv_columns

    def get_schema_from_api(
        self, repo_key: str, schema_type_dict: dict, source: str, data_type: str
    ) -> dict:
        """
        Gets the schema of a repo id for the given repo_key and
        schema_type definition at the top level

        ``Args:``
            |  ``repo_key (str) :`` repo id or repo name
            |  ``schema_type_dict (dictionary) :`` {schema_level:schema_type}
            |  example {'dataset': 'files', 'sample': 'gct_metadata'}

        ``Returns:``

            .. code::


                    {
                        "data": {
                            "id": "<REPO_ID>",
                            "type": "schema",
                            "attributes": {
                                "schema_type": "files | gct_metadata | h5ad_metadata",
                                "schema": {
                                    ... field definitions
                                }
                            }
                        }
                    }

        :meta private:
        """
        resp_dict = {}
        schema_base_url = f"{self.discover_url}/repositories"
        summary_query_param = "?response_format=summary"
        filter_query_params = ""
        if source:
            if data_type:
                filter_query_params = f"&source={source}&datatype={data_type}"
            else:
                filter_query_params = f"&source={source}"
        if repo_key and schema_type_dict and isinstance(schema_type_dict, Dict):
            for schema_table_key, val in schema_type_dict.items():
                schema_type = val
                if filter_query_params:
                    dataset_url = (
                        f"{schema_base_url}/{repo_key}/"
                        + f"schemas/{schema_type}"
                        + f"{summary_query_param}{filter_query_params}"
                    )
                else:
                    dataset_url = f"{schema_base_url}/{repo_key}/schemas/{schema_type}{summary_query_param}"
                resp = self.session.get(dataset_url)
                error_handler(resp)
                resp_dict[schema_table_key] = resp.json()
        else:
            raise paramException(
                title="Param Error",
                detail="repo_key and schema_type_dict are either empty or its datatype is not correct",
            )
        return resp_dict

    def _get_full_schema_payload_from_api(self, repo_key: str, schema_type_dict: str):
        """
        Get full schema payload from the API
        """
        resp_dict = {}
        schema_base_url = f"{self.discover_url}/repositories"
        if repo_key and schema_type_dict and isinstance(schema_type_dict, Dict):
            for schema_table_key, val in schema_type_dict.items():
                schema_type = val
                dataset_url = f"{schema_base_url}/{repo_key}/schemas/{schema_type}"
                resp = self.session.get(dataset_url)
                error_handler(resp)
                resp_dict[schema_table_key] = resp.json()
        else:
            raise paramException(
                title="Param Error",
                detail="repo_key and schema_type_dict are either empty or its datatype is not correct",
            )
        return resp_dict

    def _return_type_param_check(self, return_type: str):
        """
        get_schema parameters sanity check
        """
        if not isinstance(return_type, str):
            raise paramException(
                title="Param Error",
                detail="return_type should be a string",
            )

        return_type_vals = copy.deepcopy(const.GET_SCHEMA_RETURN_TYPE_VALS)

        if return_type not in return_type_vals:
            raise paramException(
                title="Param Error",
                detail=f"return_type take only two vals : {return_type_vals}",
            )

    def get_schema(
        self,
        repo_key: str,
        schema_level=[],
        source="",
        data_type="",
        return_type="dataframe",
    ) -> dict:
        """
        Using this function to extract the schema of an OmixAtlas.

        ``Args:``
            |  ``repo_key (str) :`` repo_id OR repo_name. This is a mandatory field.
            |  ``schema_level (list)(OPTIONAL) :`` The default value is all the table names for the repo. \
                Users can also a specific table name on which they want to query the schema. \
                Users can table names using `SHOW TABLES IN <repo>` query \
                Also backward compatible with previous schema_level values of ['dataset', 'sample']
            |  ``source (str)(OPTIONAL) :`` is the source from where data is ingested into the Omixatlas. \
                The default value is 'all', which will fetch the schema of all sources.
            |  ``data_type (str) (OPTIONAL):`` is the datatype for which user wants to get the schema for. \
                The default value is 'all', which will fetch the schema of all datatypes.

        ``Returns:``
            |  It will contain the schema for specific table names as dataframe.

            .. code::

                    {
                        'datasets':pd.DataFrame,
                        'samples':pd.DataFrame,
                        'features':pd.DataFrame
                    }
            |  you can access datasets, samples, features schema in following manner.

            .. code::


                    # import pandas as pd
                    # pd.set_option('expand_frame_repr', False)
                    # use above two line if your dataframe does not print in single line
                    # for repo `geo`
                    # In SHOW TABLES, there are 3 tables for geo
                    # `datasets`, `samples`, `features`
                    # tables = `omixatlas.query_metadata("SHOW TABLES IN geo")`
                    # print(tables)
                    # ['geo.datasets', 'geo.samples', 'geo.features']
                    schema = omixatlas.get_schema("geo", ['datasets', 'samples', 'features'])

                    # to fetch the dataframe with dataset level metadata
                    print(schema.datasets)

                    # to fetch the dataframe with sample level metadata
                    print(schema.samples)

                    # to fetch the dataframe with feature level metadata
                    print(schema.features)


            | ``schema.datasets`` will contain dataframe you can print them in a table form like this.

            .. csv-table::
                :header: "", Source, Datatype, "Field Name", "Field Description", "Field Type"
                :delim: |

                0  |  all |  all |   curated_organism |       Orgnism from which the samples were derived  |     text
                1  |  all |  all |            src_uri |   Unique URI derived from data file's S3 location  |     text
                2  |  all |  all |  total_num_samples |              Total number of samples in a dataset  |  integer
                3  |  all |  all |               year |           Year in which the dataset was published  |  integer
                4  |  all |  all |        description |                        Description of the dataset  |     text
                5  |  all |  all |  curated_cell_line | Cell lines from which the samples were derived...  |     text
                6  |  all | all  |   data_table_name  | Name of the data table associated with data file   |    text
                7  |  all |  all | data_table_version | Current version of the data table associated w...  |  integer

            | ``schema.sample`` will contain dataframe you can print them in a table form like this.

            .. csv-table::
                :header: "", "Source", "Datatype", "Field Name", "Field Description", "Field Type"
                :delim: |

                0  |  all  |  all  |   growth_protocol_ch1 |                                                NA |    text
                1  |  all  |  all  |               src_uri | Unique URI derived from source data file's S3 ... |    text
                2  |  all  |  all  |             sample_id |            Unique ID associated with every sample |    text
                3  |  all  |  all  | curated_gene_modified |        Gene modified through genetic modification |    text
                4  |  all  |  all  |              dose_ch1 |                                                NA |    text
                5  |  all  |  all  |   curated_cohort_name |    Name of the cohort to which the sample belongs |    text
                6  |  all  |  all  |       curated_control | Signifies whether the given sample is a contro... | integer
                7  |  all  |  all  |        src_dataset_id | Dataset ID of the file this data entity origin... |    text

        ``Errors:``
            |  ``invalidApiResponseException:`` datakey, attributes, schema_type is missing in repository schema.
            |  ``RequestException:`` Schema not found.
            |  ``paramException:`` repo_key and schema_type_dict are either empty or its datatype is not correct.


        |  Example to fetch dataset and sample level schema for all datatypes from all sources in GEO Omixatlas.


        .. code::

                # Also backward compatible with the schema level values earlier supported
                # ['dataset', 'sample']
                schema = omixatlas.get_schema("geo", ['dataset', 'sample'], "all", "all")

                # to fetch the dataframe with dataset level metadata
                print(schema.dataset)

                # to fetch the dataframe with sample level metadata
                print(schema.sample)
        """

        # get schema_type_dict
        schema_type_dict = self._get_schema_type_info(repo_key, schema_level, data_type)
        try:
            self._return_type_param_check(return_type)
        except Exception as err:
            raise err

        # schema from API calls
        if repo_key and schema_type_dict and isinstance(schema_type_dict, Dict):
            if return_type == "dict":
                schema_payload_dict = self._get_full_schema_payload_from_api(
                    repo_key, schema_type_dict
                )
                schema_payload_dict = self._remove_links_key_in_schema_payload(
                    schema_payload_dict
                )
                return self.return_schema_data(schema_payload_dict)
            else:
                schema = self.get_schema_from_api(
                    repo_key, schema_type_dict, source, data_type
                )
        if schema and isinstance(schema, Dict):
            for key, val in schema.items():
                if schema[key]["data"]["attributes"]["schema"]:
                    schema[key] = schema[key]["data"]["attributes"]["schema"]
        df_map = {}
        for key, val in schema.items():
            flatten_dict = self.flatten_nested_schema_dict(schema[key])
            df_map[key] = self.nested_dict_to_df(flatten_dict)

        return self.return_schema_data(df_map)

    def _remove_links_key_in_schema_payload(self, schema_payload_dict: dict) -> dict:
        """
        Remove links key from the schema response
        """
        for schema_level_key, schema_level_value in schema_payload_dict.items():
            if "data" in schema_level_value:
                val_data_dict = schema_level_value.get("data", {})
                if "links" in val_data_dict:
                    val_data_dict.pop("links", None)

        return schema_payload_dict

    def return_schema_data(self, df_map: dict) -> tuple:
        """
        Return schema data as named tuple

        :meta private:
        """
        Schema = namedtuple("Schema", (key for key, value in df_map.items()))
        return Schema(**df_map)

    def _get_schema_type_info(
        self, repo_key: str, schema_level: list, data_type: str
    ) -> dict:
        """
        Return schema type dict for valid schema level and table name values
        """

        # if schema level passed then return schema type accordingly
        if schema_level:
            schema_levels_const = copy.deepcopy(schema_levels)
            schema_table_name_const = copy.deepcopy(schema_table_names)

            # check if schema level parameter is a subset of schema_levels_const
            # a.issubset(b) => schema_level.issubset(schema_level_const)
            schema_levels_const_set = set(schema_levels_const)
            schema_table_name_const_set = set(schema_table_name_const)
            schema_level_set = set(schema_level)
            if schema_level_set.issubset(schema_levels_const_set):
                schema_type_dict = self.get_schema_type(schema_level, data_type)
            elif schema_level_set.issubset(schema_table_name_const_set):
                schema_type_dict = self._schema_table_name_schema_type_mapping(
                    repo_key, schema_level
                )
            else:
                raise paramException(
                    title="Param Error",
                    detail="schema_level input is incorrect. Use the query SHOW TABLES IN <repo_name>"
                    + "to fetch valid table names for schema_level input",
                )
            # else if check schema level is subset of schema table names
            # else raise errors
        else:
            # return all the schema types, in the default condition
            # default condition is no schema level or table name passed by user
            schema_type_dict = self._schema_table_name_schema_type_mapping(
                repo_key, schema_level
            )

        return schema_type_dict

    def get_schema_type(self, schema_level: list, data_type: str) -> dict:
        """
        Compute schema_type based on data_type and schema_level
        Old Schema Level Value Mapping and New Schema Level Value Mapping
        Backward compatible

        Old Schema Level Value Mapping
        |  schema_level   --------    schema_type
        |  dataset       --------     file
        |  sample    --------      gct_metadata
        |  sample and  ------       h5ad_metadata
        |  single cell

        :meta private:
        """
        if schema_level and isinstance(schema_level, list):
            if "dataset" in schema_level and "sample" in schema_level:
                if data_type != "single_cell" or data_type == "":
                    schema_type_dict = {"dataset": "files", "sample": "gct_metadata"}
                elif data_type == "single_cell":
                    schema_type_dict = {"dataset": "files", "sample": "h5ad_metadata"}
                else:
                    raise wrongParamException(
                        title="Incorrect Param Error",
                        detail="Incorrect value of param passed data_type ",
                    )
            elif "dataset" in schema_level or "sample" in schema_level:
                if "dataset" in schema_level:
                    schema_type_dict = {"dataset": "files"}
                elif "sample" in schema_level:
                    if data_type != "single_cell" or data_type == "":
                        schema_type_dict = {"sample": "gct_metadata"}
                    elif data_type == "single_cell":
                        schema_type_dict = {"sample": "h5ad_metadata"}
                    else:
                        raise wrongParamException(
                            title="Incorrect Param Error",
                            detail="Incorrect value of param passed data_type ",
                        )
            else:
                raise wrongParamException(
                    title="Incorrect Param Error",
                    detail="Incorrect value of param passed schema_level ",
                )
        else:
            raise paramException(
                title="Param Error",
                detail="schema_level is either empty or its datatype is not correct",
            )
        return schema_type_dict

    def _schema_table_name_schema_type_mapping(
        self, repo_key: str, schema_table_names: list
    ) -> dict:
        """
        New Schema Level Value mapping
        |   Table Name  Schema Type
        |   datasets ----- file
        |   samples ----- gct_metadata
        |   features ---- gct_row_metadata
        |   samples_singlecell ---- h5ad_metadata
        """
        # all the table and index name mapping present
        # for the repo is fetched
        schema_base_url = f"{self.discover_url}/repositories"
        schema_url = f"{schema_base_url}/{repo_key}/schemas"
        meta_true_query_param = "?meta=true"
        schema_mapping_url = f"{schema_url}{meta_true_query_param}"
        schema_mapping_info = self.session.get(schema_mapping_url)
        error_handler(schema_mapping_info)
        schema_mapping_info = schema_mapping_info.json()
        # schema mapping info structure
        # table name, index name mapping dict fetched from it
        # {"data":{"type":"<type>", "repository_id":"<repo_id>", "attributes":{"schemas":{<schema-mapping>}}}}
        schema_mapping = (
            schema_mapping_info.get("data").get("attributes").get("schemas")
        )

        # if user has passed table names
        # then only those are filtered
        # from the table and index name mapping dict
        # else the whole mapping dict returnedß

        if schema_table_names:
            schema_mapping_res = {
                schema_table: schema_mapping[schema_table]
                for schema_table in schema_table_names
            }
        else:
            schema_mapping_res = schema_mapping

        return schema_mapping_res

    def flatten_nested_schema_dict(self, nested_schema_dict: dict) -> dict:
        """
        Flatten the nested dict

        ``Args:``
            |  schema:{
            |         "<SOURCE>": {
            |             "<DATATYPE>": {
            |                 "<FIELD_NAME>": {
            |                 "type": "text | integer | object",
            |                 "description": "string", (Min=1, Max=100)
            |                 },
            |                 ... other fields
            |             }
            |             ... other Data types
            |         }
            |         ... other Sources
            |     }

        ``Returns:``
            |  {
            |      'Source':source_list,
            |      'Datatype': datatype_list,
            |      'Field Name':field_name_list,
            |      'Field Description':field_desc_list,
            |      'Field Type': field_type_list
            |  }


        :meta private:
        """
        reformed_dict = {}
        source_list = []
        data_type_list = []
        field_name_list = []
        field_description_list = []
        field_type_list = []
        is_curated_list = []
        is_array_list = []
        for outer_key, inner_dict_datatype in nested_schema_dict.items():
            for middle_key, inner_dict_fields in inner_dict_datatype.items():
                for inner_key, field_values in inner_dict_fields.items():
                    source_list.append(outer_key)
                    data_type_list.append(middle_key)
                    field_name_list.append(inner_key)
                    for key, value in field_values.items():
                        if key == "description":
                            field_description_list.append(field_values[key])
                        if key == "type":
                            field_type_list.append(field_values[key])
                        if key == "is_curated":
                            is_curated_list.append(field_values[key])
                        if key == "is_array":
                            is_array_list.append(field_values[key])

        reformed_dict["Source"] = source_list
        reformed_dict["Datatype"] = data_type_list
        reformed_dict["Field Name"] = field_name_list
        reformed_dict["Field Description"] = field_description_list
        reformed_dict["Field Type"] = field_type_list
        if is_curated_list:
            reformed_dict["Is Curated"] = is_curated_list
        reformed_dict["Is Array"] = is_array_list

        return reformed_dict

    def nested_dict_to_df(self, schema_dict: dict) -> pd.DataFrame:
        """
        Convert flatten dict into df and print it

        ``Args:``
            |  {
            |      'Source':source_list,
            |      'Datatype': datatype_list,
            |      'Field Name':field_name_list,
            |      'Field Description':field_desc_list,
            |      'Field Type': field_type_list
            |  }

        ``Returns:``
            DataFrame

        :meta private:
        """
        pd.options.display.max_columns = None
        pd.options.display.width = None
        multiIndex_df = pd.DataFrame.from_dict(schema_dict, orient="columns")
        # sort Field Name in an ascending order
        multiIndex_df.sort_values(by=["Field Name"], inplace=True, ignore_index=True)
        return multiIndex_df

    def format_type(self, data: dict) -> dict:
        """
        Format the dict data

        :meta private:
        """
        if data and isinstance(data, Dict):
            return json.dumps(data, indent=4)

    def insert_schema(self, repo_key: str, body: dict) -> dict:
        """
        Use insert_schema(repo_key, payload) to update the existing schema of an OmixAtlas.


        .. code::


                omixatlas.insert_schema(repo_key, payload)

        ``Args :``
            |  ``repo_key:`` (str) repo_id OR repo_name. This is a mandatory field.
            |  ``payload:`` (dict) The payload is a JSON file which should be as per the structure defined for\
 schema. Only data-admin will have the authentication to update the schema.

            .. code::


                    {
                        "data": {
                            "id": "<REPO_KEY>",
                            "type": "schema",
                            "attributes": {
                            "schema_type": "files | gct_metadata | h5ad_metadata",
                            "schema": {
                                ... field definitions
                            }
                            }
                        }
                    }
            |  ``payload`` can be loaded from the JSON file in which schema is defined in the following manner:

            .. code::


                    import json

                    # Opening JSON file
                    schema = open('schema_file.json')

                    # returns JSON object as a dictionary
                    payload = json.load(schema)

        ``Errors:``
            |  ``apiErrorException:`` Params are either empty or its datatype is not correct or see detail.
        """
        if repo_key and body and isinstance(body, dict):
            body = json.dumps(body)
            try:
                schema_base_url = f"{self.discover_url}/repositories"
                url = f"{schema_base_url}/{repo_key}/schemas"
                resp = self.session.post(url, data=body)
                error_handler(resp)
                return resp.text
            except Exception as err:
                raise apiErrorException(title="API exception err", detail=err)
        else:
            raise apiErrorException(
                title="Param Error",
                detail="Params are either empty or its datatype is not correct",
            )

    def update_schema(self, repo_key: str, body: dict) -> dict:
        """
        Use update_schema(repo_key, payload) to update the existing schema of an OmixAtlas.

        .. code::


                omixatlas.update_schema(repo_key, payload)
        ``Args :``
            |  ``repo_key (str):`` repo_id OR repo_name. This is a mandatory field.
            |  ``payload (dict):`` The payload is a JSON file which should be as per the structure defined for\
 schema. Only data-admin will have the authentication to update the schema.

            .. code::


                    {
                        "data": {
                            "id": "<REPO_KEY>",
                            "type": "schema",
                            "attributes": {
                            "schema_type": "files | gct_metadata | h5ad_metadata",
                            "schema": {
                                ... field definitions
                            }
                            }
                        }
                    }
            |  ``payload`` can be loaded from the JSON file in which schema is defined in the following manner:

            .. code::


                    import json
                    # Opening JSON file
                    schema = open('schema_file.json')
                    # returns JSON object as a dictionary
                    payload = json.load(schema)
        ``Errors:``
            |  ``apiErrorException:`` Params are either empty or its datatype is not correct or see detail.
        """
        schema_type = body["data"]["attributes"]["schema_type"]
        schema_base_url = f"{self.discover_url}/repositories"
        url = f"{schema_base_url}/{repo_key}/schemas/{schema_type}"
        if repo_key and body and isinstance(body, dict):
            body = json.dumps(body)
            try:
                resp = self.session.patch(url, data=body)
                error_handler(resp)
                return resp.text
            except Exception as err:
                raise apiErrorException(title="API exception err", detail=err)
        else:
            raise paramException(
                title="Param Error",
                detail="Params are either empty or its datatype is not correct",
            )

    def download_data(self, repo_name, _id: str):
        """
        Use update_schema(repo_key, payload) to update the existing schema of an OmixAtlas.

        .. code::


                omixatlas.update_schema(repo_key, payload)

        ``Args :``
            |  ``repo_key (str):`` repo_id OR repo_name. This is a mandatory field.
            |  ``payload (dict):`` The payload is a JSON file which should be as per the structure defined for\
 schema. Only data-admin will have the authentication to update the schema.

            .. code::


                    {
                        "data": {
                            "id": "<REPO_KEY>",
                            "type": "schema",
                            "attributes": {
                            "schema_type": "files | gct_metadata | h5ad_metadata",
                            "schema": {
                                ... field definitions
                            }
                            }
                        }
                    }
            |  ``payload`` can be loaded from the JSON file in which schema is defined in the following manner:


            .. code::


                    import json

                    # Opening JSON file
                    schema = open('schema_file.json')

                    # returns JSON object as a dictionary
                    payload = json.load(schema)

        ``Errors:``
            |  ``apiErrorException:`` Params are either empty or its datatype is not correct or see detail.
        """
        url = f"{self.resource_url}/{repo_name}/download"
        params = {"_id": _id}
        response = self.session.get(url, params=params)
        error_handler(response)
        return response.json()

    def save_to_workspace(
        self, repo_id: str, dataset_id: str, workspace_id: int, workspace_path: str
    ) -> json:
        """
        Function for saving data from omixatlas to workspaces.

        ``Args:``
            |  ``repo_id (str) :`` repo id.
            |  ``dataset_id (str) :`` dataset id.
            |  ``workspace_id (str) :`` workspace id of polly.
            |  ``workspace_path (str) :`` path in workspace where you want to save file.

        | Example to save the dataset_id ``'GSE101127_GPL1355'`` from repo_id ``1615965444377`` to a \
workspace_id ``8025`` in a folder named ``'data'``.


        .. code::


                omixatlas.save_to_workspace('1615965444377', 'GSE101127_GPL1355', 8025, 'data')
        """
        url = f"{self.resource_url}/workspace_jobs"
        params = {"action": "copy"}
        payload = {
            "data": {
                "type": "workspaces",
                "attributes": {
                    "dataset_id": dataset_id,
                    "repo_id": repo_id,
                    "workspace_id": workspace_id,
                    "workspace_path": workspace_path,
                },
            }
        }
        response = self.session.post(url, data=json.dumps(payload), params=params)
        error_handler(response)
        if response.status_code == 200:
            logging.basicConfig(level=logging.INFO)
            logging.info(f"Data Saved to workspace={workspace_id}")
        return response.json()

    def format_converter(self, repo_key: str, dataset_id: str, to: str) -> None:
        """
        Function to convert a file format.

        ``Args:``
            |  ``repo_key (str) :`` repo_id.
            |  ``dataset_id (str) :`` dataset_id.
            |  ``to(str) :`` output file format.

        |  For example:


        .. code::


                omixatlas.format_converter("cbioportal", "ACC_2019_Mutation_ACYC-FMI-19", "maf")

        ``Errors:``
            |  ``InvalidParameterException:`` invalid value of any parameter for example like - repo_id or \
repo_name etc.
            |  ``paramException:`` Incompatible or empty value of any parameter
        """
        if not (repo_key and isinstance(repo_key, str)):
            raise InvalidParameterException("repo_id/repo_name")
        if not (dataset_id and isinstance(dataset_id, str)):
            raise InvalidParameterException("dataset_id")
        if not (to and isinstance(to, str)):
            raise InvalidParameterException("convert_to")
        ssl._create_default_https_context = ssl._create_unverified_context
        response_omixatlas = self.get_omixatlas(repo_key)
        data = response_omixatlas.get("data").get("attributes")
        repo_name = data.get("repo_name")
        index_name = data.get("v2_indexes", {}).get("files")
        if index_name is None:
            raise paramException(
                title="Param Error", detail="Repo entered is not an omixatlas."
            )
        elastic_url = f"{self.elastic_url}/{index_name}/_search"
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"_index": index_name}},
                        {"term": {"dataset_id.keyword": dataset_id}},
                    ]
                }
            }
        }
        data_type = helpers.get_data_type(self, elastic_url, query)
        if data_type in DATA_TYPES:
            mapped_list = DATA_TYPES[data_type][0]
            if to in mapped_list["format"]:
                supported_repo = mapped_list["supported_repo"]
                repo_found = False
                for details in supported_repo:
                    if repo_name == details["name"]:
                        header_mapping = details["header_mapping"]
                        repo_found = True
                if not repo_found:
                    raise paramException(
                        title="Param Error",
                        detail=f"Incompatible repository error: Repository:'{repo_name}' not yet \
                                 incorporated for converter function",
                    )
                helpers.file_conversion(self, repo_name, dataset_id, to, header_mapping)
            else:
                raise paramException(
                    title="Param Error",
                    detail=f"Incompatible dataformat error: data format= {to} not yet incorporated for converter function",
                )
        else:
            raise paramException(
                title="Param Error",
                detail=f"Incompatible dataype error: data_type={data_type} not yet incorporated for converter function",
            )
        logging.basicConfig(level=logging.INFO)
        logging.info("File converted successfully!")

    def create(
        self,
        display_name: str,
        description: str,
        repo_name="",
        image_url="",
        components=[],
    ) -> pd.DataFrame:
        """
        This function is used to create a new omixatlas,

        ``Args:``
            | ``display_name (str):`` display name of the omixatlas.
            | ``description (str):`` description of the omixatlas.
            | ``repo_name (str):`` repo_name which is used to create index in db.
            | ``image_url (str):`` Url of the icon for omixatlas. Optional Parameter.
            | ``initials (str):`` Initials shown in the icon of omixatlas. Optional Parameter.
            | ``explorer_enabled (bool):`` Default True. Optional Parameter.
            | ``studio_presets (list):`` Optional Paramter.
            | ``components (list):`` Optional Parameter.

        ``Returns:``
            | Dataframe after creation of omixatlas.

        ``Errors:``
            |  ``ValueError:`` Repository creation response is in Incorrect format.

        | To use this function import Omixatlas class and make a object.


        .. code::


                from polly.omixatlas import OmixAtlas
                omixatlas = OmixAtlas(token)
                # to use OmixAtlas class functions
                omixatlas.create(display_name, description, repo_name, image_url, initials, explorer_enabled,\
studio_presets, components)

        """
        payload = self._get_repository_payload()
        frontend_info = {}
        frontend_info["description"] = description
        frontend_info["display_name"] = display_name
        frontend_info["icon_image_url"] = (
            image_url if image_url else const.IMAGE_URL_ENDPOINT
        )

        if not repo_name:
            repo_name = self._create_repo_name(display_name)
        else:
            repo_name = repo_name

        payload["data"]["attributes"]["repo_name"] = repo_name
        payload["data"]["attributes"]["frontend_info"] = frontend_info
        payload["data"]["attributes"]["components"] = components
        indexes = payload["data"]["attributes"]["indexes"]

        for key in indexes.keys():
            indexes[key] = f"{repo_name}_{key}"

        repository_url = f"{self.resource_url}"
        resp = self.session.post(repository_url, json=payload)
        error_handler(resp)

        if resp.status_code != const.CREATED:
            raise Exception(resp.text)
        else:
            if resp.json()["data"]["id"]:
                repo_id = resp.json()["data"]["id"]
                print(f" OmixAtlas {repo_id} Created  ")
                return self._repo_creation_response_df(resp.json())
            else:
                ValueError("Repository creation response is in Incorrect format")

    def update(
        self,
        repo_key: str,
        display_name="",
        description="",
        image_url="",
        components=[],
    ) -> pd.DataFrame:
        """
        This function is used to update an omixatlas

        Args:
            | repo_name(str/int): repo_name/repo_id for that Omixatlas
            | display_name(str): display name of the omixatlas. Optional Parameter
            | description(str): description of the omixatlas. Optional Parameter
            | image_url(str): Url of the icon for omixatlas. Optional Parameter
            | components(list): List of components to be added. Optional Parameter
        """

        if not (repo_key and (isinstance(repo_key, str) or isinstance(repo_key, int))):
            raise InvalidParameterException("repo_id/repo_name")

        if not display_name and not description and not image_url and not components:
            raise paramException(
                title="Param Error",
                detail="No params passed to update, please pass a param",
            )

        if isinstance(repo_key, int):
            repo_key = str(repo_key)

        repo_curr_data = self.get_omixatlas(repo_key)

        if "attributes" not in repo_curr_data["data"]:
            raise invalidDataException(
                detail="OmixAtlas is not created properly. Please contact admin"
            )

        attribute_curr_data = repo_curr_data["data"]["attributes"]
        if components:
            curr_components = attribute_curr_data.get("components", [])
            for item in components:
                curr_components.append(item)

        repo_curr_data["data"]["attributes"] = attribute_curr_data

        if "frontend_info" not in repo_curr_data["data"]["attributes"]:
            raise invalidDataException(
                detail="OmixAtlas is not created properly. Please contact admin"
            )

        frontendinfo_curr_data = repo_curr_data["data"]["attributes"]["frontend_info"]
        repo_curr_data["data"]["attributes"][
            "frontend_info"
        ] = self._update_frontendinfo_value(
            frontendinfo_curr_data, image_url, description, display_name
        )

        repository_url = f"{self.resource_url}/{repo_key}"
        resp = self.session.patch(repository_url, json=repo_curr_data)
        error_handler(resp)
        if resp.status_code != const.OK:
            raise Exception(resp.text)
        else:
            if resp.json()["data"]["id"]:
                repo_id = resp.json()["data"]["id"]
                print(f" OmixAtlas {repo_id} Updated  ")
                return self._repo_creation_response_df(resp.json())
            else:
                ValueError("Repository Updation response is in Incorrect format")

    def _get_file_format_constants(self) -> json:
        """
        Returns file format info from public assests url
        """
        response = requests.get(FILE_FORMAT_CONSTANTS_URL)
        error_handler(response)
        return json.loads(response.text)

    def _get_upload_urls(self, repo_id: str, destination_folder_path: str) -> dict:
        """
        Get the upload URLs for uploading the files to s3
        """
        # post request for upload urls
        payload = const.GETTING_UPLOAD_URLS_PAYLOAD
        payload["data"]["attributes"]["folder"] = destination_folder_path

        # post request
        repository_url = f"{self.discover_url}/repositories/{repo_id}/files"
        resp = self.session.post(repository_url, json=payload)
        error_handler(resp)
        if resp.status_code != const.OK:
            raise Exception(resp.text)
        else:
            response_data = resp.json()
            data_upload_details = (
                response_data.get("data", {})
                .get("attributes", {})
                .get("data_upload_url")
            )
            metadata_upload_details = (
                response_data.get("data", {})
                .get("attributes", {})
                .get("metadata_upload_url")
            )
            expiration_timestamp = (
                response_data.get("data", {})
                .get("attributes", {})
                .get("urls_expiration_time")
            )
        return data_upload_details, metadata_upload_details, expiration_timestamp

    def _upload_metadata_files(
        self,
        repo_id: str,
        priority: str,
        metadata_upload_details: dict,
        source_metadata_path: str,
        destination_folder_path: str,
        file_status_dict: dict,
        data_metadata_mapping: dict,
    ) -> dict:
        """
        Upload the combined metadata file to s3
        """
        # construct and fetch the combiend metadata dictionary that has to be put in file
        combined_metadata_dict = self._construct_metadata_dict_from_files(
            source_metadata_path,
            priority,
            destination_folder_path,
            data_metadata_mapping,
        )

        combined_metadata_file_path = str(
            Path(os.getcwd()) / Path(os.fsdecode(const.COMBINED_METADATA_FILE_NAME))
        )

        # opening file with `with` block closes the file at the end of with block
        # opening the file in w+ mode allows to both read and write files
        with open(combined_metadata_file_path, "w+") as combined_metadata_file:
            json.dump(combined_metadata_dict, combined_metadata_file, indent=4)

        # opening the file in bytes mode so as to upload the file using requests
        with open(combined_metadata_file_path, "rb") as metadata_file:
            combined_metadata_file_name_for_upload = const.COMBINED_METADATA_FILE_NAME
            metadata_files = {
                "file": (combined_metadata_file_name_for_upload, metadata_file)
            }
            upload_response = requests.post(
                metadata_upload_details["url"],
                data=metadata_upload_details["fields"],
                files=metadata_files,
            )

        file_status_dict[
            combined_metadata_file_name_for_upload
        ] = upload_response.status_code

        # error codes based on different conditions
        if upload_response.status_code == 400:
            error_str = upload_response.content.decode("utf-8")
            error_code = self._parse_error_code_from_error_xml(error_str)
            # In case tokens are expired after the timelimit
            # regenerate token and again start uploading files
            if error_code == "ExpiredToken":
                # will remove this print after final testing
                # print("----------Inside token expired metadata--------")
                (
                    data_upload_details,
                    metadata_upload_details,
                    expiration_timestamp,
                ) = self._get_upload_urls(repo_id, destination_folder_path)
                # metadata file not uploaded will be reuploaded again with
                # re-generated urls
                self._upload_metadata_files(
                    repo_id,
                    priority,
                    metadata_upload_details,
                    source_metadata_path,
                    destination_folder_path,
                    file_status_dict,
                )
            else:
                raise BadRequestError(detail=upload_response.content)
        elif upload_response.status_code == 403:
            raise AccessDeniedError(detail=upload_response.content)
        elif upload_response.status_code == 404:
            raise ResourceNotFoundError(detail=upload_response.content)

        return file_status_dict

    def _upload_data_files(
        self,
        repo_id: str,
        data_upload_details: dict,
        file_path: str,
        data_file_name_for_upload: str,
        destination_folder_path: str,
        single_file_status_dict: dict,
    ) -> dict:
        """
        Upload the data files to s3
        """
        # file opened in binary mode as it has to be uploaded
        # using the requests library
        with open(file_path, "rb") as file_to_upload:
            files = {"file": (data_file_name_for_upload, file_to_upload)}
            upload_response = requests.post(
                data_upload_details["url"],
                data=data_upload_details["fields"],
                files=files,
            )

        single_file_status_dict[data_file_name_for_upload] = upload_response.status_code

        if upload_response.status_code == 400:
            error_str = upload_response.content
            error_str = error_str.decode("utf-8")
            error_code = self._parse_error_code_from_error_xml(error_str)
            # In case tokens are expired after the time limit
            # regenerate token and again start uploading files
            if error_code == "ExpiredToken":
                # will remove this print after final testing
                # print("----------Inside token expired data--------")
                (data_upload, metadata_upload, expiration_time) = self._get_upload_urls(
                    repo_id, destination_folder_path
                )
                # data files not uploaded will be reuploaded again with
                # re-generated urls
                data_upload_details = data_upload
                self._upload_data_files(
                    repo_id,
                    data_upload_details,
                    file_path,
                    data_file_name_for_upload,
                    destination_folder_path,
                    single_file_status_dict,
                )
            else:
                raise BadRequestError(detail=upload_response.content)
        elif upload_response.status_code == 403:
            raise AccessDeniedError(detail=upload_response.content)
        elif upload_response.status_code == 404:
            raise ResourceNotFoundError(detail=upload_response.content)

        return single_file_status_dict, data_upload_details

    def _construct_metadata_dict_from_files(
        self,
        metadata_path: str,
        priority: str,
        destination_folder_path: str,
        data_metadata_mapping: dict,
    ) -> dict:
        """
        Construct metadata dictionary from metadata file path
        """
        # fetch ingestion level metadata
        combined_metadata_dict = self._insert_ingestion_level_dict(priority)

        # loop over files and append into a single dict
        data_directory = os.fsencode(metadata_path)

        for file in os.listdir(data_directory):
            file = file.decode("utf-8")
            # skip hidden files
            if not file.startswith("."):
                file_path = str(Path(metadata_path) / Path(os.fsdecode(file)))
                with open(file_path, "r") as file_to_upload:
                    res_dict = json.load(file_to_upload)
                    metadata_file_name_for_upload = file
                modified_metadata_dict = {}
                # format the actual metadata in which API payload is defined
                modified_metadata_dict = self._format_metadata_dict(
                    res_dict,
                    destination_folder_path,
                    metadata_file_name_for_upload,
                    data_metadata_mapping,
                )

                combined_metadata_dict["data"].append(modified_metadata_dict)

        return combined_metadata_dict

    def _data_metadata_parameter_check(self, source_folder_path: dict):
        """
        Sanity check for data and metadata path parameters
        """
        if not (source_folder_path and (isinstance(source_folder_path, dict))):
            raise paramException(
                title="Param Error",
                detail="source_folder_path should be a dict with valid data and"
                + f"metadata path values in the format {const.FILES_PATH_FORMAT} ",
            )

        if "data" not in source_folder_path:
            raise paramException(
                title="Param Error",
                detail=f"{source_folder_path} does not have `data` path"
                + f"Format the source_folder_path_dict like this  {const.FILES_PATH_FORMAT}",
            )

        if "data" in source_folder_path:
            data_directory = os.fsencode(source_folder_path["data"])
            if not os.path.exists(data_directory):
                raise paramException(
                    title="Param Error",
                    detail="`data` path passed is not found"
                    + "Please pass the correct path and call the function again",
                )

        if "metadata" not in source_folder_path:
            raise paramException(
                title="Param Error",
                detail=f"{source_folder_path} does not have `metadata` path"
                + "Format the source_folder_path_dict like this  {const.FILES_PATH_FORMAT}",
            )

        if "metadata" in source_folder_path:
            data_directory = os.fsencode(source_folder_path["metadata"])
            if not os.path.exists(data_directory):
                raise paramException(
                    title="Param Error",
                    detail="`metadata` path passed is not found. Please pass the correct path and call the function again",
                )

    def _data_metadata_file_ext_check(self, source_folder_path: dict):
        """
        Check extension for data and metadata file names
        """
        format_constants = self._get_file_format_constants()
        data_file_format_constants = format_constants.get("data")
        data_source_folder_path = source_folder_path["data"]

        data_directory = os.fsencode(data_source_folder_path)
        for file in os.listdir(data_directory):
            file = file.decode("utf-8")
            # skip hidden files
            if not file.startswith("."):
                file_ext = file.split(".")
                # ['<file_name>', '<extension>']
                file_ext = file_ext[1]
                if file_ext not in data_file_format_constants:
                    raise paramException(
                        title="Param Error",
                        detail=f"File format for file {file} is invalid."
                        + f"It can be => {data_file_format_constants}",
                    )

        metadata_file_format_constants = format_constants["metadata"]
        metadata_source_folder_path = source_folder_path["metadata"]
        metadata_directory = os.fsencode(metadata_source_folder_path)

        for file in os.listdir(metadata_directory):
            file = file.decode("utf-8")
            # skip hidden files
            if not file.startswith("."):
                file_ext = file.split(".")
                # ['<file_name>', '<extension>']
                file_ext = file_ext[1]
                if file_ext not in metadata_file_format_constants:
                    raise paramException(
                        title="Param Error",
                        detail=f"File format for file {file} is invalid."
                        + f"It can be => {metadata_file_format_constants}",
                    )

    def _check_data_metadata_file_path(self, source_folder_path: dict):
        """
        Check Metadata and Data files folders to test for empty case
        """
        data_source_folder_path = source_folder_path["data"]
        metadata_source_folder_path = source_folder_path["metadata"]

        if os.path.isdir(data_source_folder_path):
            if not os.listdir(data_source_folder_path):
                raise paramException(
                    title="Param Error",
                    detail=f"{data_source_folder_path} does not contain any datafiles. "
                    + "Please add the relevant data files and try again",
                )

        if os.path.isdir(metadata_source_folder_path):
            if not os.listdir(metadata_source_folder_path):
                raise paramException(
                    title="Param Error",
                    detail=f"{metadata_source_folder_path} does not contain any metadatafiles. "
                    + "Please add the relevant metadata files and try again",
                )

    def _parameter_check_for_add_dataset(
        self,
        repo_id: int,
        source_folder_path: dict,
        destination_folder_path: str,
        priority: str,
    ):
        """
        Sanity check for parameters in add dataset function
        """
        if not (repo_id and (isinstance(repo_id, str) or isinstance(repo_id, int))):
            raise paramException(
                title="Param Error",
                detail="repo_id should be str or int",
            )

        if isinstance(repo_id, int):
            repo_id = str(repo_id)

        try:
            self._data_metadata_parameter_check(source_folder_path)
        except Exception as err:
            raise err

        try:
            self._data_metadata_file_ext_check(source_folder_path)
        except Exception as err:
            raise err

        if not isinstance(destination_folder_path, str):
            raise paramException(
                title="Param Error",
                detail="`destination_folder_path` should be a string",
            )

        if not isinstance(priority, str):
            raise paramException(
                title="Param Error",
                detail="`priority` should be a string. Only 3 values are allowed i.e. `low`, `medium`, `high`",
            )

        if priority not in ["low", "medium", "high"]:
            raise paramException(
                title="Param Error",
                detail="`priority` varaible can have these 3 values => `low`, `medium`, `high` ",
            )

    def _upload_data(
        self,
        data_source_folder_path: str,
        file_status_dict: dict,
        data_upload_details: dict,
        repo_id: str,
        destination_folder_path: str,
    ) -> dict:
        """ """
        # Looping on metadata_path and fetching data files outside the
        # helper function as each file has to be uploaded seperately
        data_directory = os.fsencode(data_source_folder_path)
        for file in os.listdir(data_directory):
            file = file.decode("utf-8")
            # skip hidden files
            if not file.startswith("."):
                file_path = str(Path(data_source_folder_path) / Path(os.fsdecode(file)))
                data_file_name_for_upload = file
                try:
                    single_file_status_dict = {}
                    single_file_status_dict, data_upload_url = self._upload_data_files(
                        repo_id,
                        data_upload_details,
                        file_path,
                        data_file_name_for_upload,
                        destination_folder_path,
                        single_file_status_dict,
                    )
                    for key, val in single_file_status_dict.items():
                        file_status_dict[key] = val

                    data_upload_details = data_upload_url
                except ResourceNotFoundError as re:
                    raise re
                except AccessDeniedError as ae:
                    raise ae
                except Exception as err:
                    raise err

        return file_status_dict

    def _map_data_metadata_files(self, source_folder_path: dict):
        """
        Map data and metadata file names and create a dict and return
        If for a data file name, there is not metadata file raise an error
        """

        # checking if folders are empty
        try:
            self._check_data_metadata_file_path(source_folder_path)
        except Exception as err:
            raise err

        data_source_folder_path = source_folder_path["data"]
        data_directory = os.fsencode(data_source_folder_path)
        data_file_names = os.listdir(data_directory)

        data_file_names_str = []
        # convert data file names from bytes to strings
        # data file name is kept with extension here
        # whole data file name is needed in further code
        for file in data_file_names:
            file = file.decode("utf-8")
            data_file_names_str.append(file)

        metadata_source_folder_path = source_folder_path["metadata"]
        metadata_directory = os.fsencode(metadata_source_folder_path)
        metadata_file_names = os.listdir(metadata_directory)

        metadata_file_names_str = []
        # convert metadata file names from bytes to strings
        for file in metadata_file_names:
            file = file.decode("utf-8")
            file_vals = file.split(".")
            # ['<file_name>','<extentsion>']
            file_name = file_vals[0]
            metadata_file_names_str.append(file_name)

        # metadata file name -> key, data file name with extension -> value
        data_metadata_mapping_dict = {}

        unmapped_file_names = []

        for data_file in data_file_names_str:
            data_file_vals = data_file.split(".")
            # ['<file_name>','<extentsion>']
            data_file_name = data_file_vals[0]

            # check for matching data and metadata file name
            # convention for the system to know data and metadata mapping
            # also removing the metadata file from the list
            # which maps to data file
            # so as to return the unmapped metadata files at last if any
            if data_file_name in metadata_file_names_str:
                data_metadata_mapping_dict[data_file_name] = data_file
                metadata_file_names_str.remove(data_file_name)
            else:
                unmapped_file_names.append(data_file_name)

        # data and metadata file names are unmapped
        if len(unmapped_file_names) > 0 and len(metadata_file_names_str) > 0:
            raise paramException(
                title="Missing files",
                detail=f" No metadata for these data files {unmapped_file_names}"
                + f"No data for these metadata files {metadata_file_names_str}"
                + ". Please add the relevant files or remove them.",
            )
        elif len(unmapped_file_names) > 0:
            raise paramException(
                title="Missing files",
                detail=f" No metadata for these data files {unmapped_file_names}"
                + ". Please add the relevant files or remove them.",
            )
        elif len(metadata_file_names_str) > 0:
            raise paramException(
                title="Missing files",
                detail=f"No data for these metadata files {metadata_file_names_str}"
                + ". Please add the relevant files or remove them.",
            )
        else:
            return data_metadata_mapping_dict

    def _upload_metadata(
        self,
        repo_id: str,
        priority: str,
        metadata_upload_details: str,
        metadata_source_folder_path: dict,
        destination_folder_path: str,
        file_status_dict: dict,
        data_metadata_mapping: dict,
    ) -> dict:
        """
        Upload metadata function
        """
        # Looping on metadata_path and fetching metadata files inside the
        # helper function as they all are going to be combined in
        # 1 file and then uploaded
        try:
            file_status_dict = self._upload_metadata_files(
                repo_id,
                priority,
                metadata_upload_details,
                metadata_source_folder_path,
                destination_folder_path,
                file_status_dict,
                data_metadata_mapping,
            )
        except ResourceNotFoundError as re:
            raise re
        except AccessDeniedError as ae:
            raise ae
        except Exception as err:
            raise err

        return file_status_dict

    def add_datasets(
        self,
        repo_id: int,
        source_folder_path: dict,
        destination_folder_path="",
        priority="low",
    ):
        """
        This function is used to add data to an omixatlas
        Args:
            | repo_id(str/int): repo_name/repo_id for that Omixatlas
            | source_folder_path(dict): source folder path from data and metadata files are fetched.
            | destination_folder_path(str)(Optional Parameter): Destination folder structure in s3
            | priority(str)(Optional Parameter): Priority at which this data has to be inserted.

        For example :
            | Link to the notebook
            | https://github.com/ElucidataInc/polly-python/blob/main/Ingest/Data_Ingestion_CaseID_1.ipynb
        """
        # parameters check
        try:
            self._parameter_check_for_add_dataset(
                repo_id, source_folder_path, destination_folder_path, priority
            )
        except Exception as err:
            raise err
        (
            data_upload_details,
            metadata_upload_details,
            expiration_timestamp,
        ) = self._get_upload_urls(repo_id, destination_folder_path)

        # folder paths
        data_source_folder_path = source_folder_path["data"]
        metadata_source_folder_path = source_folder_path["metadata"]

        # list of list which will store all the results
        # at last assign it to a dataframe
        result_list = []
        file_status_dict = {}

        # data metadata file mapping
        try:
            data_metadata_mapping = self._map_data_metadata_files(source_folder_path)
        except Exception as err:
            raise err

        try:
            file_status_dict = self._upload_metadata(
                repo_id,
                priority,
                metadata_upload_details,
                metadata_source_folder_path,
                destination_folder_path,
                file_status_dict,
                data_metadata_mapping,
            )
        except Exception as err:
            raise err

        try:
            file_status_dict = self._upload_data(
                data_source_folder_path,
                file_status_dict,
                data_upload_details,
                repo_id,
                destination_folder_path,
            )
        except Exception as err:
            raise err

        # iterating the status dict
        # generating appropriate messages
        result_list = self._generating_response_from_status_dict(
            file_status_dict, result_list
        )

        # printing the dataframe
        data_upload_results_df = pd.DataFrame(
            result_list, columns=["File Name", "Message"]
        )

        with pd.option_context("display.max_rows", None, "display.max_columns", None):
            print(data_upload_results_df)

    def _generating_response_from_status_dict(
        self, file_status_dict: dict, result_list: list
    ) -> list:
        """
        Generating the response with File Name and Error Message
        Store the response in the list format
        Response Message Cases
        1. If the whole metadata file not uploaded => `Reupload the metadata again`
        2. If File is uploaded => `File Uploaded`
        3. If the data file is not uploaded => `Reupload the data file and its metadata also`
        """

        for key, value in file_status_dict.items():
            if key == const.COMBINED_METADATA_FILE_NAME and value in [400, 404, 409]:
                response = []
                response.append(key)
                response.append("Metadata Not uploaded, reupload the metadata again")
                result_list.append(response)
            elif value == 204:
                response = []
                response.append(key)
                response.append("File Uploaded")
                result_list.append(response)
            elif value in [400, 404, 409]:
                response = []
                response.append(key)
                response.append(
                    "File Not Uploaded, reupload the file again and also upload the corresponding metadata"
                )
                result_list.append(response)
        return result_list

    def _parse_error_code_from_error_xml(self, err) -> str:
        """
        Parse error code from then error
        """
        error_str_tree = ET.fromstring(err)
        error_code = error_str_tree.find("Code").text
        return error_code

    def _insert_ingestion_level_dict(self, priority: str) -> dict:
        """
        Ingestion level metadata appended in combined metadata dict
        """
        ingestion_level_metadata = const.INGESTION_LEVEL_METADATA
        ingestion_level_metadata["attributes"]["priority"] = priority
        # combined metadata dict structure initialized
        metadata = const.METADATA
        metadata["data"].append(ingestion_level_metadata)
        return metadata

    def _format_metadata_dict(
        self,
        metadata_dict: dict,
        destination_folder_path: str,
        filename: str,
        data_metadata_mapping: dict,
    ) -> dict:
        """
        Take metadata dict as input and insert additonal fields in each metadata
        Format the json according to JSON API spec
        """
        formatted_metadata = {"id": "", "type": "", "attributes": {}}
        # ['<filename>', '<extension>']
        file_name_vals = filename.split(".")
        # file_name = '<filename>'
        file_name = file_name_vals[0]
        # fetching data file for corresponding metadata file name
        data_file_name = data_metadata_mapping[file_name]

        if destination_folder_path:
            formatted_metadata["id"] = f"{destination_folder_path}/{data_file_name}"
        else:
            formatted_metadata["id"] = f"{data_file_name}"
        formatted_metadata["type"] = "file_metadata"
        formatted_metadata["attributes"] = metadata_dict

        return formatted_metadata

    # TODO
    # Currently works for repositories having source -> `all` & datatype -> `all`
    # In the datalake only these examples exist for now
    # In future it will be extended for other sources and datatypes
    def dataset_metadata_template(
        self, repo_key, source="all", data_type="all"
    ) -> dict:
        """
        This function is used to create a template for dataset level metadata
        Args:
            | repo_id(str/int): repo_name/repo_id for that Omixatlas
            | source(Optional Parameter) : Source/Sources present in the schema. By default `all`
            | data_type(Optional Parameter) : Datatype/Datatypes present in the schema. By default `all`
        """
        # for dataset level metadata index is files
        schema_type = "files"

        schema_base_url = f"{self.discover_url}/repositories"

        dataset_url = f"{schema_base_url}/{repo_key}/" + f"schemas/{schema_type}"

        resp = self.session.get(dataset_url)
        error_handler(resp)
        api_resp_dict = resp.json()
        if "data" in api_resp_dict:
            if "attributes" in api_resp_dict["data"]:
                if "schema" in api_resp_dict["data"]["attributes"]:
                    resp_dict = {}
                    resp_dict = api_resp_dict["data"]["attributes"]["schema"][source][
                        data_type
                    ]
                else:
                    raise invalidApiResponseException(
                        title="schema key not present",
                        detail="`schema` key not inside attributes present in the repository schema",
                    )
            else:
                raise invalidApiResponseException(
                    title="attributes key not present",
                    detail="attributes not present in the repository schema",
                )
        else:
            raise invalidApiResponseException(
                title="data key not present",
                detail="data key not present in the repository schema",
            )

        result_dict = {}
        # deleting unnecessary keys
        for field_key, val_dict in resp_dict.items():
            is_array_val = val_dict.get("is_array", None)
            type_val = val_dict.get("type", None)
            original_name_key = val_dict.get("original_name", None)
            if is_array_val is None:
                result_dict[original_name_key] = type_val
            elif is_array_val:
                result_dict[original_name_key] = []
            else:
                result_dict[original_name_key] = type_val

        # adding `__index__` key and its default values
        result_dict["__index__"] = {
            "file_metadata": True,
            "col_metadata": True,
            "row_metadata": False,
            "data_required": False,
        }

        return result_dict

    def _parameter_check_for_delete_dataset(self, repo_id: int, dataset_ids: list):
        """
        Sanity check for all the parameters
        """
        if not (repo_id and (isinstance(repo_id, str) or isinstance(repo_id, int))):
            raise paramException(
                title="Param Error",
                detail="repo_id should be str or int",
            )

        if isinstance(repo_id, int):
            repo_id = str(repo_id)

        if not (dataset_ids and isinstance(dataset_ids, list)):
            raise paramException(
                title="Param Error",
                detail="dataset_ids should be list of strings",
            )

    def _s3_key_dataset(self, repo_id: int, dataset_ids: list) -> dict:
        """
        S3 keys for dataset ids
        """
        # key -> `dataset_id`, value -> single or multiple file keys
        s3_keys_dict = {}
        schema_base_url = f"{self.discover_url}/repositories/{repo_id}/files"
        for dataset_id in dataset_ids:
            storage_details_query_param = (
                f"?storage_details=true&dataset_id={dataset_id}"
            )
            dataset_url = f"{schema_base_url}{storage_details_query_param}"
            resp = self.session.get(dataset_url)
            if resp.status_code != const.OK:
                val_dict = {}
                if resp.status_code == http_codes.FORBIDDEN:
                    raise AuthenticationError(
                        "User access is denied. Please contact admin"
                    )
                elif resp.status_code == http_codes.UNAUTHORIZED:
                    raise UnauthorizedException("User is unauthorized to access this")
                elif resp.status_code == http_codes.NOT_FOUND:
                    error_msg = self._extract_error_message(resp.text)
                    val_dict[resp.status_code] = error_msg
                else:
                    error_msg = self._extract_error_message(resp.text)
                    val_dict[resp.status_code] = error_msg
                s3_keys_dict[dataset_id] = val_dict
            else:
                response_data = resp.json()
                response_data = response_data.get("data")
                # handle cases for single and multiple key
                val_dict = {}
                # single s3 key for `dataset_id`
                if len(response_data) == 1:
                    response_data = response_data[0]
                    s3_key = response_data.get("id", "")
                    # {`status_code`:`s3_key`}
                    val_dict[resp.status_code] = s3_key
                    # {`dataset_id`:{`status_code`:`s3_key`}}
                    s3_keys_dict[dataset_id] = val_dict
                elif len(response_data) > 1:
                    # multiple s3 key for `dataset_id`
                    val_dict[resp.status_code] = []
                    for data in response_data:
                        s3_key = data.get("id", "")
                        val_dict[resp.status_code].append(s3_key)
                    s3_keys_dict[dataset_id] = val_dict
        return s3_keys_dict

    def _extract_error_message(self, error_msg) -> str:
        """
        Extract error message from the error
        """
        error_msg = json.loads(error_msg)
        error = error_msg.get("error")
        if error is None:
            error = error_msg.get("errors")[0]
        if "detail" in error:
            detail = error.get("detail")

        return detail

    def delete_datasets(self, repo_id: int, dataset_ids: list):
        """
        This function is used to delete data from an omixatlas
        Args:
            | repo_id(str/int): repo_id for that Omixatlas
            | dataset_ids(list<string>): dataset_ids that users want to delete
            | file_key(list<string>)(Optional Parameter): File key for the files to delete
        """
        try:
            self._parameter_check_for_delete_dataset(repo_id, dataset_ids)
        except Exception as err:
            raise err

        # extract s3 keys for dataset_ids
        dataset_s3_keys_dict = self._s3_key_dataset(repo_id, dataset_ids)

        # convert the dict to df at last
        result_dict = {}

        # delete the datasets using file keys
        for datasetid_key, val_dict in dataset_s3_keys_dict.items():
            for status_code, value in val_dict.items():
                if status_code in [
                    http_codes.BAD_REQUEST,
                    http_codes.NOT_FOUND,
                    http_codes.CONFLICT,
                    http_codes.FORBIDDEN,
                ]:
                    result_dict[datasetid_key] = value
                elif status_code in [http_codes.OK]:
                    if isinstance(value, str):
                        delete_url = (
                            f"{self.discover_url}/repositories/{repo_id}/files/{value}"
                        )
                        resp = self.session.delete(delete_url)
                        if resp.status_code == http_codes.ACCEPTED:
                            result_dict[
                                datasetid_key
                            ] = "Request Accepted. Dataset Will be deleted in the next version of OmixAtlas"
                        else:
                            result_dict[
                                datasetid_key
                            ] = f"Request of Deletion not accepted because {resp.text}"
                    elif isinstance(value, list):
                        result_dict[
                            datasetid_key
                        ] = "Operation Failed. Please contact admin for deletion"
        data_delete_df = pd.DataFrame(
            result_dict.items(), columns=["Dataset Id", "Message"]
        )

        with pd.option_context(
            "display.max_rows",
            500,
            "display.max_columns",
            500,
            "display.max_colwidth",
            100,
        ):
            print(data_delete_df)

    def _update_frontendinfo_value(
        self,
        frontendinfo_curr_data: dict,
        image_url: str,
        description: str,
        display_name: str,
    ) -> dict:
        if image_url:
            frontendinfo_curr_data["icon_image_url"] = image_url
        if description:
            frontendinfo_curr_data["description"] = description
        if display_name:
            frontendinfo_curr_data["display_name"] = display_name
        return frontendinfo_curr_data

    def _repo_creation_response_df(self, original_response) -> pd.DataFrame:
        """
        This function is used to create dataframe from json reponse of
        creation api

        Args:
            | original response(dict): creation api response
        Returns:
            | DataFrame consisting of 4 columns ["Repository Id", "Repository Name", "Display Name", "Description"]

        """
        response_df_dict = {}
        if original_response["data"]:
            if original_response["data"]["attributes"]:
                attribute_data = original_response["data"]["attributes"]
                response_df_dict["Repository Id"] = attribute_data.get("repo_id", "")
                response_df_dict["Repository Name"] = attribute_data.get(
                    "repo_name", ""
                )
                if attribute_data["frontend_info"]:
                    front_info_dict = attribute_data["frontend_info"]
                    response_df_dict["Display Name"] = front_info_dict.get(
                        "display_name", ""
                    )
                    response_df_dict["Description"] = front_info_dict.get(
                        "description", ""
                    )
        rep_creation_df = pd.DataFrame([response_df_dict])
        return rep_creation_df

    def _create_repo_name(self, display_name) -> str:
        """
        This function is used to repo_name from display_name
        Args:
            | display_name(str): display name of the omixatlas
        Returns:
            | Constructed repo name
        """
        repo_name = display_name.lower().replace(" ", "_")
        return repo_name

    def _get_repository_payload(self):
        """ """
        return {
            "data": {
                "type": "repositories",
                "attributes": {
                    "frontend_info": {
                        "description": "<DESCRIPTION>",
                        "display_name": "<REPO_DISPLAY_NAME>",
                        "explorer_enabled": True,
                        "initials": "<INITIALS>",
                    },
                    "indexes": {
                        "csv": "<REPO_NAME>_csv",
                        "files": "<REPO_NAME>_files",
                        "gct_data": "<REPO_NAME>_gct_data",
                        "gct_metadata": "<REPO_NAME>_gct_metadata",
                        "h5ad_data": "<REPO_NAME>_h5ad_data",
                        "h5ad_metadata": "<REPO_NAME>_h5ad_metadata",
                        "ipynb": "<REPO_NAME>_ipynb",
                        "json": "<REPO_NAME>_json",
                    },
                    "repo_name": "<REPO_NAME>",
                },
            }
        }

    def generate_report(
        self, repo_key: str, dataset_id: str, workspace_id: int, workspace_path=""
    ) -> None:
        """
        This function is used to generate a report for a dataset_id belonging to the geo repository.
        Args:
            | repo_key(str): repo_name/repo_id for which the report is to be generated
            | dataset_id(str): dataset_id for which the report is to be generated
            | workspace_id(int): workspace_id to where the report is to be uploaded
            | workspace_path(str)(Optional Parameter): workspace_path to upload the report to

        .. code::


                from polly.omixatlas import OmixAtlas
                omixatlas = OmixAtlas(token)
                # to use OmixAtlas class functions
                omixatlas.generate_report(dataset_id, workspace_id, workspace_path=None)
        """
        if not (repo_key and isinstance(repo_key, str)):
            raise InvalidParameterException("repo_key")
        if not (workspace_id and isinstance(workspace_id, int)):
            raise InvalidParameterException("workspace_id")
        if not (dataset_id and isinstance(dataset_id, str)):
            raise InvalidParameterException("dataset_id")
        response_omixatlas = self.omixatlas_summary(repo_key)
        data = response_omixatlas.get("data")
        repo_name = data.get("repo_name").lower()
        if repo_name not in REPORT_GENERATION_SUPPORTED_REPOS:
            raise UnsupportedRepositoryException
        download_dict = self.download_data(repo_name, dataset_id)
        if download_dict:
            pass
        query = f"SELECT * FROM {repo_name}.datasets WHERE dataset_id = '{dataset_id}'"
        sel_dataset_info = self.query_metadata(query)
        query = (
            f"SELECT * FROM {repo_name}.samples WHERE src_dataset_id ='{dataset_id}'"
        )
        result_sample = self.query_metadata(query)
        result_sample.fillna("none", inplace=True)
        all_fields = helpers.get_cohort_fields()
        sample_kw_fields = all_fields.get("sample_kw_fields")
        sample_fields = all_fields.get("sample_fields")
        dataset_fields = all_fields.get("dataset_fields")
        extra_fields = all_fields.get("extra_fields")
        total_sample_fields = []
        total_sample_fields = sample_kw_fields + sample_fields
        for col in result_sample.columns:
            if col in extra_fields:
                total_sample_fields.append(col)
        total_sample_fields = list({*total_sample_fields})
        result_sample_sel = result_sample[total_sample_fields]
        deleted_dict, result_sample_sel = self._preprocessing_data(result_sample_sel)
        pie_charts, sunburst = self._get_plots(result_sample_sel)
        sel_dataset_info.reset_index(inplace=True)
        sel_dataset_info = sel_dataset_info[dataset_fields]
        sel_dataset_info.fillna("None", inplace=True)
        sel_dataset_info = sel_dataset_info.astype("str")
        sel_dataset_info = sel_dataset_info.applymap(lambda x: x.strip("[]"))
        sel_dataset_info = sel_dataset_info.applymap(lambda x: x.replace("'", ""))
        sel_dataset_info = sel_dataset_info.applymap(lambda x: x.replace("[", ""))
        drop_data_cols = sel_dataset_info.columns[(sel_dataset_info == "None").any()]
        sel_dataset_info.drop(drop_data_cols, axis=1, inplace=True)
        replace_cols = {
            "total_num_samples": "number_of_samples",
            "description": "title",
            "overall_design": "experimental_design",
        }
        sel_dataset_info.rename(columns=replace_cols, inplace=True)
        sel_dataset_info["platform"] = dataset_id.split("_")[1]
        string_data = []
        for col in sel_dataset_info.columns:
            string_data.append(
                f"**{col.replace('_', ' ').title()} :** {sel_dataset_info[col][0]}"
            )
        deleted_data = []
        for key, val in deleted_dict.items():
            deleted_data.append(f"**{key.replace('_', ' ').title()} :** {val}")
        md_blocks = [dp.Text(st) for st in string_data]
        new_md_blocks = [dp.Text(st) for st in deleted_data]
        self._save_report(
            dataset_id,
            workspace_id,
            workspace_path,
            md_blocks,
            new_md_blocks,
            pie_charts,
            sunburst,
        )

    def _preprocessing_data(self, result_sample_sel: pd.DataFrame):
        """
        Dropping the columns which have same values
        """
        deleted_dict = {}
        for col in result_sample_sel.columns:
            if result_sample_sel[col].explode().nunique() == 1:
                value = list(np.unique(np.array(list(result_sample_sel[col]))))
                if value[0] != "none":
                    deleted_dict[col] = value[0]
                result_sample_sel = result_sample_sel.drop(col, axis=1)
        return deleted_dict, result_sample_sel

    def _get_plots(self, result_sample_sel: pd.DataFrame) -> tuple:
        """
        Function to return plots( pie-chart and sunburst plot)
        """
        if result_sample_sel.shape[1] != 0:
            result_sample_sel = result_sample_sel[
                result_sample_sel.columns[
                    ~(result_sample_sel.applymap(helpers.check_empty) == 0).any()
                ]
            ]
            explode_col = result_sample_sel.columns[
                result_sample_sel.applymap(
                    lambda x: True if type(x) == list else False
                ).any()
            ]
            for col in explode_col:
                result_sample_sel = result_sample_sel.explode(col)
            for col in result_sample_sel.columns:
                for val in result_sample_sel[col].unique():
                    if val.find(":") > 1:
                        result_sample_sel.rename(
                            columns={col: val[: val.find(":")].strip(" ")}, inplace=True
                        )
            sunburst = px.sunburst(
                result_sample_sel,
                path=list(
                    zip(
                        *sorted(
                            {
                                col: result_sample_sel[col].nunique()
                                for col in result_sample_sel.columns
                            }.items(),
                            key=lambda x: x[1],
                        )
                    )
                )[0],
                width=600,
                height=600,
                title="Sample level Metadata",
            )
            pie_charts = []
            for col in result_sample_sel.columns:
                pie_ch = px.pie(
                    result_sample_sel,
                    col,
                    width=600,
                    height=600,
                    title=col.replace("_", " ").title(),
                    hole=0.3,
                )
                pie_ch.update_traces(marker=dict(line=dict(color="white", width=1.5)))
                pie_ch.update_layout(
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        font=dict(size=10),
                        xanchor="right",
                        x=1,
                    )
                )
                pie_charts.append(dp.Plot(pie_ch))

        else:
            pie_charts, sunburst = None, None
        return pie_charts, sunburst

    def _save_report(
        self,
        dataset_id: str,
        workspace_id: int,
        workspace_path: str,
        md_blocks: list,
        new_md_blocks: list,
        pie_charts: list,
        sunburst,
    ) -> None:
        """
        Function to make a report and save it in local and upload to given workspace
        """
        if pie_charts is not None:
            my_pie = dp.Group(blocks=pie_charts, columns=2, label="Pie Charts")
            sunburst_pl = dp.Plot(sunburst, label="Sun Burst")
            report = dp.Report(
                f"### {dataset_id}",
                dp.Group(blocks=md_blocks, columns=1),
                dp.Select(blocks=[my_pie, sunburst_pl]),
            )
        else:
            report = dp.Report(
                f"### {dataset_id}",
                dp.Group(blocks=md_blocks, columns=1),
                dp.Group(blocks=new_md_blocks, columns=1),
            )
        report_name = f"{dataset_id}_report.html"
        report.save(
            path=report_name, formatting=dp.ReportFormatting(width=dp.ReportWidth.FULL)
        )
        local_path = f"{os.getcwd()}/{report_name}"
        """if workspace_path is not empty and contains anything except whitespaces, then make a valid path, \
        else assign predefined name as the path"""
        if workspace_path and not workspace_path.isspace():
            workspace_path = helpers.make_path(workspace_path, report_name)
        else:
            workspace_path = report_name
        helpers.edit_html(local_path)
        from polly.workspaces import Workspaces

        w = Workspaces()
        w.upload_to_workspaces(workspace_id, workspace_path, local_path)

    def link_report(
        self,
        repo_key: str,
        dataset_id: str,
        workspace_id: int,
        workspace_path: str,
        access_key: str,
    ) -> None:
        """
        This function is used to link a file present in a workspace with the specified dataset in OmixAtlas.
        Args:
            | repo_key(str): repo_name/repo_id of the repository to be linked.
            | dataset_id(str): dataset_id of the dataset to be linked.
            | workspace_id(int): workspace_id for the file which is to be linked.
            | workspace_path(str): workspace_path for the file which is to be linked.
            | access_key(str): access_key(private or public) depending upon the link access type to be generated.

        .. code::


                from polly.omixatlas import OmixAtlas
                omixatlas = OmixAtlas(token)
                # to use OmixAtlas class functions
                omixatlas.link_report(repo_key, dataset_id, workspace_id, workspace_path, access_key)
        """
        if not (repo_key and isinstance(repo_key, str)):
            raise InvalidParameterException("repo_key")
        if not (dataset_id and isinstance(dataset_id, str)):
            raise InvalidParameterException("dataset_id")
        if not (workspace_id and isinstance(workspace_id, int)):
            raise InvalidParameterException("workspace_id")
        if not (workspace_id and isinstance(workspace_path, str)):
            raise InvalidParameterException("workspace_path")
        if not (
            access_key
            and isinstance(access_key, str)
            and access_key.lower() in ["private", "public"]
        ):
            raise InvalidParameterException("access_key")
        sts_url = f"{self.base_url}/projects/{workspace_id}/credentials/files"
        access_url = f"https://{self.session.env}.elucidata.io/manage"
        helpers.verify_workspace_details(self, workspace_id, workspace_path, sts_url)
        response_omixatlas = self.omixatlas_summary(repo_key)
        data = response_omixatlas.get("data")
        repo_id = data.get("repo_id")
        absolute_path = helpers.make_path(workspace_id, workspace_path)
        url = f"{self.base_url}/v1/omixatlases/{repo_id}/reports"
        payload = {
            "data": {
                "type": "dataset-reports",
                "attributes": {
                    "dataset_id": f"{dataset_id}",
                    "absolute_path": f"{absolute_path}",
                },
            }
        }
        response = self.session.post(url, data=json.dumps(payload))
        error_handler(response)
        shared_id = self._get_shared_id(workspace_id, workspace_path)
        if shared_id is None:
            existing_access = "private"
        else:
            existing_access = "public"
        if access_key == existing_access == "private":
            file_link = helpers.make_private_link(
                workspace_id, workspace_path, access_url
            )
        elif access_key == existing_access == "public":
            file_link = f"{access_url}/shared/file/?id={shared_id}"
        else:
            file_link = helpers.change_file_access(
                self, access_key, workspace_id, workspace_path, access_url
            )
        print(
            f"File Successfully linked to dataset id = {dataset_id}. The URL for the {access_key} access is '{file_link}'"
        )

    def fetch_linked_reports(self, repo_key: str, dataset_id: str) -> pd.DataFrame:
        """
        This function fetch workspaces from Polly.

        ``Args:``
            | repo_key(str): repo_name/repo_id of the repository for which to fetch the reports.
            | dataset_id(str): dataset_id of the dataset which to fetch the reports.

        ``Returns:``
            |  A Dataframe with the details of the linked reports.


        .. code::


                # create a obj
                omixatlas = OmixAtlas()
                # to use OmixAtlas class functions
                omixatlas.fetch_linked_report(repo_key, dataset_id)
        """
        if not (repo_key and isinstance(repo_key, str)):
            raise InvalidParameterException("repo_key")
        if not (dataset_id and isinstance(dataset_id, str)):
            raise InvalidParameterException("dataset_id")
        response_omixatlas = self.omixatlas_summary(repo_key)
        data = response_omixatlas.get("data")
        repo_id = data.get("repo_id")
        params = {"dataset_id": f"{dataset_id}"}
        url = f"{self.base_url}/v1/omixatlases/{repo_id}/reports"
        response = self.session.get(url, params=params)
        error_handler(response)
        report_list = response.json().get("data").get("attributes").get("reports")
        access_url = f"https://{self.session.env}.elucidata.io/manage"
        if len(report_list) == 0:
            print("No Reports found to be linked with the given details.")
        else:
            columns = ["Added_by", "Added_time", "URL"]
            all_details = []
            for items in report_list:
                details_list = []
                added_by = items.get("added_by")
                # convertime time fetched in miliseconds to datetime
                added_on = items.get("added_on") / 1000.0
                added_time = datetime.fromtimestamp(added_on).strftime(
                    "%d/%m/%Y %H:%M:%S"
                )
                absolute_path = items.get("absolute_path")
                workspace_id, workspace_path = helpers.split_workspace_path(
                    absolute_path
                )
                try:
                    sts_url = (
                        f"{self.base_url}/projects/{workspace_id}/credentials/files"
                    )
                    status = helpers.check_is_file(
                        self, sts_url, workspace_id, workspace_path
                    )
                except Exception:
                    print(
                        f"Not enough permissions for the workspace_id : {workspace_id}. Please contact Polly Support."
                    )
                    continue
                if not status:
                    # the file does not exist in the workspace, hence skipping this file path
                    print(
                        f"The workspace path '{workspace_path}' does not represent a valid path. Please contact Polly Support."
                    )
                    continue
                shared_id = self._get_shared_id(workspace_id, workspace_path)
                if shared_id is None:
                    file_url = helpers.make_private_link(
                        workspace_id, workspace_path, access_url
                    )
                else:
                    file_url = f"{access_url}/shared/file/?id={shared_id}"
                details_list.append(added_by)
                details_list.append(added_time)
                details_list.append(file_url)
                all_details.append(details_list)
            if len(all_details) == 0:
                print("No Reports to be displayed.")
            else:
                df = pd.DataFrame(all_details, columns=columns)
                return df

    def _get_shared_id(self, workspace_id, workspace_path):
        """
        Returns the shared_id of the file in workspace in case of global access to file, None in case of private access
        """
        url = f"https://v2.api.{self.session.env}.elucidata.io/projects/{workspace_id}/files/{workspace_path}"
        params = {"action": "file_download"}
        response = self.session.get(url, params=params)
        error_handler(response)
        shared_id = response.json().get("data").get("shared_id")
        return shared_id


if __name__ == "__main__":
    client = OmixAtlas()
