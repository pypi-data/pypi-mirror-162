import json

import names
import numpy as np
import pandas as pd
from randomtimestamp import randomtimestamp

from teaching_tools.ab_test.params import cohort_params


def load_json(filepath: str) -> dict:
    """Loads JSON file.

    Parameters
    ----------
    filepath : str
        Location of JSON file

    Returns
    -------
    dict

    """
    with open(filepath, "r") as f:
        return json.load(f)


def load_cohort_params(c) -> dict:
    """Helper function for loading cohort parameters.

    Parameters
    ----------
    c : Union[str, dict]
        If ``str``, treated as a filepath. If ``dict``, returns same.

    Returns
    -------
    dict

    """
    if isinstance(c, str):
        return load_json(c)
    elif isinstance(c, dict):
        return c
    else:
        return cohort_params


class StudentGenerator:
    def __init__(
        self,
        cohort_params=None,
        days=1,
        start=None,
        n=None,
        is_experiment=False,
    ):
        self.cohort_params = load_cohort_params(cohort_params)
        self.is_experiment = is_experiment
        self.days = days

        if n is None:
            self.n = self.calculate_n_students()
        else:
            self.n = n

        if start is None:
            self.start = pd.Timestamp.now()
        elif isinstance(start, str):
            self.start = pd.to_datetime(start, format="%Y-%m-%d")
        else:
            self.start = start

    def calculate_n_students(self) -> int:
        mu = self.cohort_params["daily_traffic"]["mu"]
        sigma = self.cohort_params["daily_traffic"]["sigma"]
        n = sum(np.random.normal(mu, sigma, self.days).astype(int))
        return n

    def generate_bday(self, years):
        days_offset = np.random.randint(low=0, high=350)
        birthdate = pd.Timestamp.now() - pd.DateOffset(
            years=int(years), days=days_offset
        )
        return birthdate.replace(hour=0, minute=0, second=0, microsecond=0)

    def generate_categorical(self, labels, probabilities, size=1):
        labels = np.array(labels)
        probabilities = np.array(probabilities)
        data = np.random.choice(
            a=labels,
            size=size,
            p=probabilities,
        )
        return data

    def generate_email(self, first: str, last: str) -> str:
        domains = [
            "@yahow.com",
            "@gmall.com",
            "@microsift.com",
            "@hotmeal.com",
        ]
        email = (
            first.lower()
            + "."
            + last.lower()
            + str(np.random.randint(1, 100))
            + np.random.choice(domains, 1)[0]
        )
        return email

    def generate_students(self):
        df = pd.DataFrame()

        # Add columns from demographic params
        for k, v in self.cohort_params["demographics"].items():
            df[k] = self.generate_categorical(
                labels=list(v.keys()),
                probabilities=list(v.values()),
                size=self.n,
            )

        # Create birthday from age
        df["birthday"] = df["age"].apply(self.generate_bday)
        df.drop(columns=["age"], inplace=True)

        # Create name
        df["firstName"] = df["gender"].apply(
            lambda x: names.get_first_name(gender=x)
        )
        df["lastName"] = [names.get_last_name() for x in range(self.n)]

        # Create email
        df["email"] = df[["firstName", "lastName"]].apply(
            lambda x: self.generate_email(*x), axis=1
        )

        # Create timestamp
        stop = self.start + pd.DateOffset(days=self.days)
        df["createdAt"] = [
            randomtimestamp(start=self.start, end=stop) for x in range(self.n)
        ]

        # Reorder columns
        cols = [
            "createdAt",
            "firstName",
            "lastName",
            "email",
            "birthday",
            "gender",
            "highestDegreeEarned",
            "countryISO2",
            "admissionsQuiz",
        ]
        df = df[cols]

        if self.is_experiment:
            df["inExperiment"] = False
            df["group"] = np.nan
            # Get parameters
            response_var = self.cohort_params["experiment"]["response_var"]
            contingency_table = self.cohort_params["experiment"][
                "contingency_table"
            ]

            # Mask to those who haven't taken the quiz
            mask = df["admissionsQuiz"] == "incomplete"
            mask_idx = mask[mask].index.to_list()
            # Create experiment data
            data = []
            for group, response in contingency_table.items():
                for k, v in response.items():
                    count = round(mask.sum() * v)
                    data += [(group, k)] * count

            # Sometimes the lengths of data and mask_idx don't match
            diff = len(data) - len(mask_idx)
            if diff > 0:
                data = data[:-diff]
            if diff < 0:
                mask_idx = mask_idx[:diff]

            # Add to df
            df.loc[mask_idx, ("group", response_var)] = data
            df.loc[mask_idx, "inExperiment"] = True

        return df


class Cohort:
    def __init__(self, **kwargs):
        self._students = None
        self.generator = StudentGenerator(**kwargs)

    def enroll_students(self, confirm_msg=True):
        self._students = self.generator.generate_students()
        if confirm_msg:
            print(f"Added {len(self._students)} students to cohort.")

    def yield_students(self):
        if self._students is None:
            self.enroll_students(confirm_msg=False)
        for s in self._students.itertuples(index=False, name="Student"):
            # Remove fields for subjects not in experiment
            s_dict = s._asdict()
            try:
                if s_dict["inExperiment"] is False:
                    del s_dict["group"]
            except KeyError:
                pass
            yield s_dict

    def get_students(self) -> pd.DataFrame:
        """Getter function"""
        if self._students is None:
            raise AttributeError(
                "You have not enrolled any students in this cohort. Use `enroll_students` first."
            )
        else:
            return self._students
