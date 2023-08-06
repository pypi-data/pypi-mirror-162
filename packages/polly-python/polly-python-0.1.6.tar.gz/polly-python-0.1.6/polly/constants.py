DATA_TYPES = {
    "Mutation": [
        {
            "format": ["maf"],
            "supported_repo": [
                {
                    "name": "cbioportal",
                    "header_mapping": {
                        "gene": "Hugo_Symbol",
                        "chr": "Chromosome",
                        "startPosition": "Start_Position",
                        "endPosition": "End_Position",
                        "referenceAllele": "Reference_Allele",
                        "variantAllele": "Tumor_Seq_Allele2",
                        "mutationType": "Variant_Classification",
                        "variantType": "Variant_Type",
                        "uniqueSampleKey": "Tumor_Sample_Barcode",
                    },
                },
                {"name": "tcga", "header_mapping": {}},
            ],
        }
    ]
}

# endpoints
CONSTANTS_ENDPOINT = "/constants"
REPOSITORIES_ENDPOINT = "/repositories"
REPOSITORY_PACKAGE_ENDPOINT = REPOSITORIES_ENDPOINT + "/{}/packages"
IMAGE_URL_ENDPOINT = (
    "https://elucidatainc.github.io/PublicAssets/discover-fe-assets/omixatlas_hex.svg"
)

# statuscodes
OK = 200
CREATED = 201
COMPUTE_ENV_VARIABLE = "POLLY_TYPE"
UPLOAD_URL_CREATED = 204

# cohort constants
COHORT_VERSION = "0.2"
COHORT_CONSTANTS_URL = (
    "https://elucidatainc.github.io/PublicAssets/cohort_constants.txt"
)
REPORT_FIELDS_URL = "https://elucidatainc.github.io/PublicAssets/report_fields.txt"
OBSOLETE_METADATA_FIELDS = [
    "package",
    "region",
    "bucket",
    "key",
    "file_type",
    "file_location",
    "src_uri",
    "timestamp_",
]
dot = "."

GETTING_UPLOAD_URLS_PAYLOAD = {"data": {"type": "files", "attributes": {"folder": ""}}}

INGESTION_LEVEL_METADATA = {
    "id": "metadata/ingestion",
    "type": "ingestion_metadata",
    "attributes": {
        "ignore": "false",
        "urgent": "true",
        "v1_infra": False,
        "priority": "low",
    },
}

METADATA = {"data": []}

GET_SCHEMA_RETURN_TYPE_VALS = ["dataframe", "dict"]

COMBINED_METADATA_FILE_NAME = "combined_metadata.json"

FILES_PATH_FORMAT = {"metadata": "<metadata_path>", "data": "<data_path>"}

FORMATTED_METADATA = {"id": "", "type": "", "attributes": {}}

FILE_FORMAT_CONSTANTS_URL = (
    "https://elucidatainc.github.io/PublicAssets/file_format_constants.txt"
)

BASE_TEST_FORMAT_CONSTANTS_URL = "https://github.com/ElucidataInc/PublicAssets/blob/master/internal-user/add_dataset_test_file"

ELUCIDATA_LOGO_URL = (
    "https://elucidatainc.github.io/PublicAssets/dashboardFrontend/elucidata-logo.svg"
)

REPORT_GENERATION_SUPPORTED_REPOS = ["geo"]
