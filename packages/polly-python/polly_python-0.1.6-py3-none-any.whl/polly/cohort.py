from polly import helpers
from polly.errors import (
    InvalidCohortOperationException,
    InvalidParameterException,
    InvalidRepoException,
    CohortEditException,
    EmptyCohortException,
    InvalidCohortAddition,
    InvalidCohortMergeOperation,
)
import pandas as pd
from deprecated import deprecated
from polly.bridge_cohort import CohortRepoClass
from polly.core_cohort import CohortFileStandard
from polly import constants as const
from polly.help import example, doc


class Cohort:
    """
    The Cohort class contains functions which can be used to create cohorts, add or remove samples,\
merge metadata and data-matrix of samples/datasets in a cohort and edit or delete a cohort.

    ``Args:``
        |  ``token (str):`` token copy from polly.

    .. code::


            from polly.cohort import Cohort
            # To use this class initialize a object like this if you are not authorised on polly
            cohort = Cohort(token)

    If you are authorised then you can initialize object without token to know about :ref:`authentication <auth>`.
    """

    _cohort_info = None
    example = classmethod(example)
    doc = classmethod(doc)

    def __init__(self, token=None, env="", default_env="polly") -> None:
        # check if COMPUTE_ENV_VARIABLE present or not
        # if COMPUTE_ENV_VARIABLE, give priority
        env = helpers.get_platform_value_from_env(
            const.COMPUTE_ENV_VARIABLE, default_env, env
        )
        if self._cohort_info is None:
            self._cohort_info = helpers.get_cohort_constants()
        self._cohort_path = None
        self._cohort_details = None
        self.bridge_obj = CohortRepoClass(token, env)
        self.core_obj = CohortFileStandard()

    def create_cohort(
        self,
        local_path: str,
        cohort_name: str,
        description: str,
        repo_key=None,
        dataset_id=None,
        sample_id=None,
    ) -> None:
        """
            This function is used to create a cohort.

            ``Args:``
                |  ``local_path(str):`` local path to instantiate the cohort.
                |  ``cohort_name(str):`` identifier name for the cohort.
                |  ``description(str):`` description about the cohort.
                |  ``repo_key(str):`` Optional argument: repo_key(repo_name/repo_id) for the omixatlas from where \
datasets or samples is to be added.
                |  ``entity_id(list):`` Optional argument: list of dataset_id or sample_id to be added to the \
cohort.

            ``Returns:``
                |  A confirmation message on creation of cohort.

            ``Errors:``
                |  ``InvalidParameterException:`` Empty or Invalid Parameters
                |  ``InvalidCohortNameException:`` The cohort_name does not represent a valid cohort name.
                |  ``InvalidPathException:`` Provided path does not represent a file or a directory.

            | After making Cohort Object you can create cohort.
            | Example-
            | 1. while passing argument of repo and dataset.

            .. code::


                cohort.create_cohort("/import/tcga_cohort","cohort_name","cohort_description",\
"repo_id",list_of_datasets)

            | 2. without passing argument of repo and dataset.

            .. code::


                    cohort2.create_cohort("/path","cohort_name","cohort_description")


        """
        self._cohort_path = self.bridge_obj.create_cohort(
            local_path, cohort_name, description
        )
        self._cohort_details = self.bridge_obj._cohort_details
        if repo_key:
            self.add_to_cohort(
                repo_key=repo_key,
                dataset_id=dataset_id,
                sample_id=sample_id,
            )

    def add_to_cohort(self, repo_key: str, dataset_id=None, sample_id=None) -> None:
        """
        This function is used to add datasets or samples to a cohort.

        ``Args:``
            |  ``repo_key(str):`` repo_key(repo_name OR repo_id) for the omixatlas where datasets or samples belong.
            |  ``entity_id(list):`` list of dataset ID or sample ID to be added to the cohort.

        ``Returns:``
            |  A confirmation message for number of datasets or samples which are added to the cohort.

        ``Errors:``
            |  ``InvalidParameterException:`` Empty or Invalid Parameters.
            |  ``InvalidCohortOperationException:`` This operation is not valid as no cohort has been \
instantiated.

        | After creating cohort we can add datasets or samples to cohort.
        | Example-
        .. code::


                cohort.add_to_cohort("repo_id",list_of_dataset_ids)

        """
        self.bridge_obj._cohort_details = self._cohort_details
        if self._cohort_details is None:
            raise InvalidCohortOperationException
        if not ((repo_key and dataset_id and sample_id) or (repo_key and dataset_id)):
            raise InvalidParameterException("repo_key dataset_id sample_id")
        repo_name = self.bridge_obj._return_omixatlas_name(repo_key)
        if repo_name not in self._cohort_info:
            raise InvalidRepoException(repo_name)
        for repo, dict in self._cohort_info.items():
            if repo_name == repo:
                if dict["file_structure"] == "single":
                    entity_type = "dataset"
                else:
                    entity_type = "sample"
        cohort_entity_type = entity_type
        if "entity_type" in self._cohort_details:
            existing_entity_type = self._cohort_details.get("entity_type")
            if existing_entity_type != cohort_entity_type:
                raise InvalidCohortAddition
        self.bridge_obj._cohort_details = self._cohort_details
        if cohort_entity_type == "dataset":
            self.bridge_obj.add_to_cohort_single(
                self._cohort_path,
                repo_name=repo_name,
                entity_id=dataset_id,
                entity_type=cohort_entity_type,
            )
        else:
            self.bridge_obj.add_to_cohort_multiple(
                self._cohort_path,
                repo_name=repo_name,
                dataset_id=dataset_id,
                sample_id=sample_id,
                entity_type=cohort_entity_type,
            )
        self._cohort_details = self.bridge_obj._cohort_details

    def remove_from_cohort(self, dataset_id=None, sample_id=[]) -> None:
        """
        This function is used for removing datasets or samples from a cohort.

        ``Args:``
            |  ``entity_id(list):`` list of dataset IDs or sample IDs which is to be removed from the cohort.

        ``Returns:``
            |  A confirmation message on removal of datasets or samples from cohort.

        ``Errors:``
            |  ``InvalidParameterException:`` Empty or Invalid Parameters
            |  ``InvalidCohortOperationException:`` This operation is not valid as no cohort has been \
instantiated.

        |  Example-
        .. code::


                cohort.remove_from_cohort(list_of_datasets)
        """
        self.core_obj._cohort_details = self._cohort_details
        if self._cohort_details is None:
            raise InvalidCohortOperationException
        if "entity_type" not in self._cohort_details:
            raise EmptyCohortException
        entity_type = self._cohort_details.get("entity_type")
        if entity_type == "dataset":
            self.core_obj.remove_single_from_cohort(self._cohort_path, dataset_id)
        else:
            self.core_obj.remove_multiple_from_cohort(
                self._cohort_path, dataset_id, sample_id
            )
        self._cohort_details = self.core_obj._cohort_details

    def merge_data(self, data_level: str):
        """
        Function to merge metadata (dataset, sample and feature level metadata) or data-matrix of all the samples\
or datasets in the cohort.

        Args:
            | data_level(str): identifier to specify the data to be merged - "dataset", "sample", "feature" or \
"data_matrix"
        Returns:
            | A pandas dataframe containing the merged data which is ready for analysis
        """
        self.core_obj._cohort_details = self._cohort_details
        if self._cohort_details is None:
            raise InvalidCohortOperationException
        if not (data_level and isinstance(data_level, str)):
            raise InvalidParameterException("data_level")
        if "entity_type" not in self._cohort_details:
            raise EmptyCohortException
        if not (data_level and isinstance(data_level, str)):
            raise InvalidParameterException("data_level")
        if data_level == "sample":
            sample_df = self.merge_sample_metadata()
            return sample_df
        if data_level == "dataset":
            dataset_df = self.merge_dataset_metadata()
            return dataset_df
        if data_level == "data_matrix":
            datamatrix_df = self.merge_data_matrix()
            return datamatrix_df
        if data_level == "feature":
            feature_df = self.merge_feature_metadata()
            return feature_df
        raise InvalidCohortMergeOperation

    @deprecated(reason="use function merge_data")
    def merge_sample_metadata(self) -> pd.DataFrame:
        """
        Function to merge the sample level metadata from all the gct files in a cohort.
        Returns:
            | A pandas dataframe containing the merged metadata for analysis.

        :meta private:
        """
        self.core_obj._cohort_details = self._cohort_details
        if self._cohort_details is None:
            raise InvalidCohortOperationException
        if "entity_type" not in self._cohort_details:
            raise EmptyCohortException
        entity_type = self._cohort_details.get("entity_type")
        if entity_type == "sample":
            return self.core_obj.merge_multiple_sample_metadata(self._cohort_path)
        else:
            return self.core_obj.merge_single_sample_metadata(self._cohort_path)

    def is_valid(self) -> bool:
        """
        This function is used to check the validity of a cohort.

        ``Returns:``
            |  A boolean result based on the validity of the cohort.

        ``Errors:``
            |  ``InvalidPathException:`` Cohort path does not represent a file or a directory.
            |  ``InvalidCohortOperationException:`` This operation is not valid as no cohort has been \
instantiated.

        .. code::


                cohort2.is_valid()
        """
        self.core_obj._cohort_details = self._cohort_details
        if self._cohort_details is None:
            raise InvalidCohortOperationException
        return self.core_obj.is_valid(self._cohort_path)

    @deprecated(reason="use function merge_data")
    def merge_feature_metadata(self) -> pd.DataFrame:
        """
        Function to merge the feature level metadata from all the gct files in a cohort.
        Returns:
            | A pandas dataframe containing the merged metadata for analysis.

        :meta private:
        """
        self.core_obj._cohort_details = self._cohort_details
        if self._cohort_details is None:
            raise InvalidCohortOperationException
        if "entity_type" not in self._cohort_details:
            raise EmptyCohortException
        return self.core_obj.merge_feature_metadata(self._cohort_path)

    @deprecated(reason="use function merge_data")
    def merge_dataset_metadata(self) -> pd.DataFrame:
        """
        Function to merge the dataset level metadata from all the gct files in a cohort.
        Returns:
            | A pandas dataframe containing the merged metadata for analysis.

        :meta private:
        """
        self.core_obj._cohort_details = self._cohort_details
        if self._cohort_details is None:
            raise InvalidCohortOperationException
        if "entity_type" not in self._cohort_details:
            raise EmptyCohortException
        return self.core_obj.merge_dataset_metadata(self._cohort_path)

    @deprecated(reason="use function merge_data")
    def merge_data_matrix(self) -> pd.DataFrame:
        """
        Function to merge the data matrix metadata from all the gct files in a cohort.
        Returns:
            | A pandas dataframe containing the merged metadata for analysis.

        :meta private:
        """
        self.core_obj._cohort_details = self._cohort_details
        if self._cohort_details is None:
            raise InvalidCohortOperationException
        if "entity_type" not in self._cohort_details:
            raise EmptyCohortException
        entity_type = self._cohort_details.get("entity_type")
        if entity_type == "sample":
            return self.core_obj.merge_multiple_data_matrix(self._cohort_path)
        else:
            return self.core_obj.merge_single_data_matrix(self._cohort_path)

    def load_cohort(self, local_path: str):
        """
        Function to load an existing cohort into an object. Once loaded, the functions described in the \
documentation can be used for the object where the cohort is loaded.

        ``Args:``
            |  ``local_path(str):`` local path of the cohort.

        ``Returns:``
            |  A confirmation message on instantiation of the cohort.

        ``Errors:``
            |  ``InvalidPathException:`` This path does not represent a file or a directory.
            |  ``InvalidCohortPathException:`` This path does not represent a Cohort.

        |  Example-
        .. code::

                cohort.load_cohort("/path/cohort_name.pco")

        """
        self.core_obj.load_cohort(local_path)
        self._cohort_path = local_path
        self._cohort_details = self.core_obj._cohort_details

    def edit_cohort(self, new_cohort_name=None, new_description=None):
        """
          This function is used to edit the cohort level metadata such as cohort name and description.

        ``Args:``
            |  ``new_cohort_name(str):`` Optional Argument: new identifier name for the cohort.
            |  ``new_description(str):`` Optional Argument: new description about the cohort.

        ``Returns:``
            |  A confirmation message on updation of cohort.

        ``Errors:``
            |  ``InvalidCohortOperationException:`` This operation is not valid as no cohort has been \
instantiated.
            |  ``CohortEditException:`` No parameter specified for editing in cohort

        |  Example-
        .. code::


                cohort.edit_cohort("edited-cohort-name","edited-cohort-description")

        """
        self.core_obj._cohort_details = self._cohort_details
        if self._cohort_details is None:
            raise InvalidCohortOperationException
        if new_cohort_name is None and new_description is None:
            raise CohortEditException
        new_path = self.core_obj.edit_cohort(
            new_cohort_name, new_description, self._cohort_path
        )
        if new_path:
            self._cohort_path = new_path
        self._cohort_details = self.core_obj._cohort_details

    def summarize_cohort(self):
        """
        Function to return cohort level metadata and dataframe with datasets or samples added in the cohort.

        ``Returns:``
            |  A tuple with the first value as cohort metadata information (name, description and number of \
dataset(s) or sample(s) in the cohort) and the second value as dataframe containing the source, \
dataset_id or sample_id and data type available in the cohort.

        ``Errors:``
            |  ``InvalidCohortOperationException:`` This operation is not valid as no cohort has been \
instantiated.

        | Example-

        .. code::


                metadata, cohort_details = cohort.summarize_cohort()
        | metadata will contain a object like this.

        .. code::


                {
                'cohort_name': 'cohort_name',
                'number_of_samples': 6,
                'description': 'cohort_description'
                }
        | cohort detail will contain a table like that
        .. csv-table::
            :header: "", "source_omixatlas",  "datatype", "dataset_id"
            :delim: |

            0 |	tcga |	Mutation |	BRCA_Mutation_TCGA-A8-A09Q-01A-11W-A019-09
            1 |	tcga |	Mutation |	BRCA_Mutation_TCGA-AN-A0FL-01A-11W-A050-09
            2 |	tcga |	Mutation |	BRCA_Mutation_TCGA-AR-A254-01A-21D-A167-09
            3 |	tcga |	Mutation |	BRCA_Mutation_TCGA-D8-A1XO-01A-11D-A14K-09
            4 |	tcga |	Mutation |	BRCA_Mutation_TCGA-EW-A1J2-01A-21D-A13L-09
            5 |	tcga |	Mutation |	BRCA_Mutation_TCGA-LL-A50Y-01A-11D-A25Q-09
        """
        self.core_obj._cohort_details = self._cohort_details
        if self._cohort_details is None:
            raise InvalidCohortOperationException
        return self.core_obj.summarize_cohort(self._cohort_path)

    def delete_cohort(self) -> None:
        """
        This function is used to delete a cohort.
        Returns:
            | A confirmation message on deletion of cohort
        """
        self.core_obj._cohort_details = self._cohort_details
        if self._cohort_details is None:
            raise InvalidCohortOperationException
        self.core_obj.delete_cohort(self._cohort_path)
        self.bridge_obj._cohort_details = self.core_obj._cohort_details
        self._cohort_details = self.core_obj._cohort_details
        self._cohort_path = None
