"""
python script for the value storage dataclass and its functions
"""


from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from numpy.typing import NDArray  # type: ignore
from pandas import read_csv as pd_read_csv


@dataclass
class ValueStorage:
    """class to store the original, new, average, scaling and date values"""

    average: NDArray[np.float64] = field(default_factory=lambda: np.zeros(0))
    original: NDArray[np.float64] = field(default_factory=lambda: np.zeros(0))
    scaling: NDArray[np.float64] = field(default_factory=lambda: np.zeros(0))
    new: NDArray[np.float64] = field(default_factory=lambda: np.zeros(0))
    date: NDArray[np.float64] = field(default_factory=lambda: np.zeros(0))

    def read_profile_from_csv_with_date(
        self,
        path: str,
        column_of_load: str,
        column_of_date: str,
        *,
        separator: str = ",",
        decimal: str = ".",
        date_format: str = "%Y-%m-%d %H:%M:%S",
    ) -> None:
        """
        read profile to be scaled from csv file and also the date of profile\n
        :param path: path of csv file from which the dataframe should be read
        :param column_of_load: column name of load profile in csv
        :param column_of_date: column name of date in csv
        :param separator: seperator sign between csv columns (default is ,)
        :param decimal: decimal sign in csv file (default is .)
        :param date_format: date time format if necessary (default YYYY-MM-DD hh:mm:ss)
        Link for date format https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        """
        data_frame = self._read_dataframe_from_csv(path, separator, decimal)
        self._get_profile_from_dataframe(data_frame, column_of_load)
        date = self._get_date_from_dataframe(data_frame, column_of_date)
        self._reformat_date(date, date_format=date_format)

    def read_profile_from_csv(
        self,
        path: str,
        column_of_load: str,
        *,
        separator: str = ",",
        decimal: str = ".",
    ) -> None:
        """
        read profile to be scaled from csv file\n
        :param path: path of csv file from which the dataframe should be read
        :param column_of_load: column name of load profile in csv
        :param separator: seperator sign between csv columns (default is ,)
        :param decimal: decimal sign in csv file (default is .)
        """
        data_frame = self._read_dataframe_from_csv(path, separator, decimal)
        self._get_profile_from_dataframe(data_frame, column_of_load)

    def read_profile_from_dataframe(self, data_frame: pd.DataFrame, column_of_load: str) -> None:
        """
        read profile to be scaled from pandas dataframe\n
        :param data_frame: pandas dataframe to read profile from
        :param column_of_load: column name of load profile in pandas dataframe
        """
        self._get_profile_from_dataframe(data_frame, column_of_load)

    def read_profile_from_dataframe_with_date(
        self, data_frame: pd.DataFrame, column_of_load: str, column_of_date: str, *, date_format: str = "%Y-%m-%d %H:%M:%S"
    ) -> None:
        """
        read profile to be scaled from pandas dataframe including the date\n
        :param data_frame: pandas dataframe to read profile from
        :param column_of_load: column name of load profile in pandas dataframe
        :param column_of_date: column name of date in pandas dataframe
        :param date_format: date time format if necessary (default YYYY-MM-DD hh:mm:ss)
        Link for date format https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        """
        self._get_profile_from_dataframe(data_frame, column_of_load)
        date = self._get_date_from_dataframe(data_frame, column_of_date)
        self._reformat_date(date, date_format=date_format)

    def set_profile_from_series_with_date(self, load_profile: pd.Series, date: pd.Series) -> None:
        """
        set load profile and date from pandas Series
        :param load_profile: load profile as pandas Series
        :param date: Date as pandas Series
        """
        self.original = load_profile.to_numpy(dtype=np.float64)
        self.date = date.to_numpy(dtype="datetime64[s]")

    def set_profile_from_series(self, load_profile: pd.Series) -> None:
        """
        set load profile from pandas Series
        :param load_profile: load profile as pandas Series
        """
        self.original = load_profile.to_numpy(dtype=np.float64)

    def set_profile_from_numpy_array(self, load_profile: NDArray[np.float64]) -> None:
        """
        set load profile from numpy array
        :param load_profile: load profile as numpy array
        """
        self.original = load_profile

    @staticmethod
    def _read_dataframe_from_csv(path: str, separator: str = ",", decimal: str = ".") -> pd.DataFrame:
        """
        read dataframe from csv file\n
        :param path: path of csv file from which the dataframe should be read
        :param separator: seperator sign between csv columns (default is ,)
        :param decimal: decimal sign in csv file (default is .)
        """
        # try to read csv file if not found raise an exception
        try:
            data_frame: pd.DataFrame = pd_read_csv(path, sep=separator, decimal=decimal)
        except FileNotFoundError as exception:
            raise FileNotFoundError(f"pandas Dataframe not found: {path}") from exception
        return data_frame

    @staticmethod
    def _get_date_from_dataframe(data_frame: pd.DataFrame, column_of_date: str) -> pd.Series:
        """
        get date from pandas Dataframe and check if column exists\n
        :param data_frame: pandas DataFrame to read the date from
        :param column_of_date: column name of date in Dataframe
        :return: pandas series of date
        """
        # try to get date from column otherwise raise column not found error
        try:
            date = data_frame[column_of_date]
        except KeyError as exception:
            raise KeyError("no such Date column in pandas Dataframe") from exception
        return date

    def _get_profile_from_dataframe(self, data_frame: pd.DataFrame, column_of_load: str) -> None:
        """
        get profile from pandas Dataframe and check if column exists\n
        :param data_frame: pandas DataFrame to read the profile from
        :param column_of_load: column name of profile in Dataframe
        :return: pandas series of profile
        """
        # try to get load profile from column otherwise raise column not found error
        try:
            self.original = data_frame[column_of_load].to_numpy(dtype=np.float64)
        except KeyError as exception:
            raise KeyError("no such column in pandas Dataframe to read values from") from exception

    def _reformat_date(self, date: pd.Series, *, date_format: str = "%Y-%m-%d %H:%M:%S") -> None:
        """
        reformat date input as pandas Dataframe to a numpy array\n
        :param date: pandas series including the date
        :param date_format: date time format if necessary (default YYYY-MM-DD hh:mm:ss)
        Link for date format https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        """
        date = pd.to_datetime(date, format=date_format)
        self.date = date.to_numpy(dtype="datetime64[s]")

    def scale_scaling_profile_2_same_sum(self) -> None:
        """
        scales the scaling profile to the same sum of the original load
        """
        self.scaling = self.scaling / self.scaling.sum() * self.original.sum()

    def set_scaling_profile_from_numpy_array(self, load_profile: NDArray[np.float64], *, same_sum: bool = False) -> None:
        """
        set scaling profile from numpy array
        :param load_profile: load profile as numpy array
        :param same_sum: size scaling profile to the same sum as the original profile (default=False)
        """
        # set scaling profile
        self.scaling = load_profile
        # calculate same sum if wanted
        if same_sum:
            self.scale_scaling_profile_2_same_sum()

    def set_scaling_profile_from_pandas_series(self, load_profile: pd.Series, *, same_sum: bool = False) -> None:
        """
        set scaling profile from pandas series
        :param load_profile: load profile as pandas series
        :param same_sum: size scaling profile to the same sum as the original profile (default=False)
        """
        # set scaling profile
        self.scaling = load_profile.to_numpy(dtype=np.float64)
        # calculate same sum if wanted
        if same_sum:
            self.scale_scaling_profile_2_same_sum()

    def read_scaling_profile_from_dataframe(self, data_frame: pd.DataFrame, column_of_scaled_profile: str, *, same_sum: bool = False) -> None:
        """
        read scaling profile from pandas dataframe
        :param data_frame: pandas dataframe to read profile from
        :param column_of_scaled_profile: column name of scaling profile in pandas dataframe
        :param same_sum: size scaling profile to the same sum as the original profile (default=False)
        """
        # set scaling profile
        self.scaling = data_frame[column_of_scaled_profile].to_numpy(dtype=np.float64)
        # calculate same sum if wanted
        if same_sum:
            self.scale_scaling_profile_2_same_sum()

    def read_scaling_profile_from_csv(
        self, path: str, column_of_scaled_profile: str, *, separator: str = ",", decimal: str = ".", same_sum: bool = False
    ) -> None:
        """
        read profile to be scaled from csv file\n
        :param path: path of csv file from which the dataframe should be read
        :param column_of_scaled_profile: column name of scaling profile in csv
        :param separator: seperator sign between csv columns (default is ,)
        :param decimal: decimal sign in csv file (default is .)
        :param same_sum: size scaling profile to the same sum as the original profile (default=False)
        """
        # get pandas dataframe from csv file
        data_frame = self._read_dataframe_from_csv(path, separator, decimal)
        # set scaling profile
        self.scaling = data_frame[column_of_scaled_profile].to_numpy(dtype=np.float64)
        # calculate same sum if wanted
        if same_sum:
            self.scale_scaling_profile_2_same_sum()
