from typing import Optional, Union

import pandas as pd
import pymongo

from teaching_tools.ab_test.data_model import Cohort
from teaching_tools.ab_test.params import (
    cohort_params,
    cohort_params_assignment,
)
from teaching_tools.ab_test.repository import (
    AbstractRepository,
    MongoRepository,
)


class Experiment:
    """Class to generate experimental student data and insert into repository."""

    def __init__(
        self,
        repo: AbstractRepository,
        db="wqu-abtest",
        collection="ds-applicants",
    ) -> None:
        self.attach_repository(repo, db=db)
        self.collection = collection
        self.db = db

    def attach_repository(
        self,
        repository: Union[AbstractRepository, pymongo.MongoClient],
        db: str,
    ) -> None:
        """Attach new repository to experiment.

        Parameters
        ----------
        repository : AbstractRepository

        repo_name : str, optional
            If ``repository`` is ``pymongo.MongoClient``, name of database, by default "wqu-abtest".

        Raises
        ------
        Exception
            Failed to attach repository.
        """
        if isinstance(repository, pymongo.MongoClient):
            self.repo = MongoRepository(repository, db)
        # Pass in Class we build in 7.4
        elif type(repository).__name__ == "MongoRepository":
            client = repository.client
            db = repository.collection._Collection__database._Database__name
            self.repo = MongoRepository(client, db)
        elif isinstance(repository, AbstractRepository):
            self.repo = repository
        elif isinstance(repository, pymongo.collection.Collection):
            db = repository._Collection__database._Database__name
            client = repository._Collection__database._Database__client
            self.repo = MongoRepository(client, db)
        else:
            raise Exception("Cannot attach repository.")

    def add_cohort_to_repository(self, overwrite=False) -> dict:
        """Add cohort of students to repository.

        Parameters
        ----------
        collection : str, optional
            Name of collection to which cohort will be added, by default "ds_applicants"
        overwrite : bool, optional
            Whether to overwrite collection if already exists, by default False
        """
        self.repo.create_collection(
            collection=self.collection, overwrite=overwrite
        )
        r = self.repo.insert(
            self.collection,
            records=self.cohort.yield_students(),
            return_result=True,
        )
        return r

    def run_experiment(self, days: int, start: Optional[str] = None, assignment=False) -> dict:
        """Add experimental student data to repository.

        Parameters
        ----------
        days : int
            Number of days to run the experiment. More days means more students.
        """
        if start is None:
            start = pd.Timestamp.now()
        if assignment:
            self.cohort = Cohort(days=days, start=start, is_experiment=True, cohort_params=cohort_params_assignment)
        else:
            self.cohort = Cohort(days=days, start=start, is_experiment=True, cohort_params=cohort_params)
        r = self.add_cohort_to_repository()
        return r

    def reset_experiment(self) -> dict:
        """Remove experimental student data from repository.

        Parameters
        ----------
        confirm_msg : bool, optional
            Whether to print confirmation message, by default True
        """
        results = self.repo.drop(
            collection=self.collection,
            query={"inExperiment": {"$exists": True}},
            return_result=True,
        )
        return results
