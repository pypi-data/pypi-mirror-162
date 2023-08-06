# -*- coding: utf-8 -*-

"""
Created on Mon Dec 27 16:13:22 2021

@author: Dominik Fischer
"""

from typing import List, Optional, Union

import numpy as np
import pandas as pd
from numpy.typing import NDArray  # type: ignore
from scipy import optimize
from scipy.special import erf

from tssm.value_storage import ValueStorage


class AverageScalingCalculation:
    """class to save the start and end index"""

    __slots__ = "start", "end", "values", "date", "period", "simultaneity_factor", "new_simultaneity_factor"

    def __init__(self, values: ValueStorage, period: int, simultaneity_factor: NDArray[np.float64]):
        self.start: NDArray[np.uint32] = np.zeros(0, np.uint32)
        self.end: NDArray[np.uint32] = np.zeros(0, np.uint32)
        self.values: ValueStorage = values
        self.date: NDArray[np.float64] = values.date
        self.period: int = period
        self.simultaneity_factor: NDArray[np.float64] = simultaneity_factor
        self.new_simultaneity_factor: NDArray[np.float64] = np.zeros(len(self.values.original))

    def calculate(self, number_of_buildings: int, *, scaling_factor: Optional[Union[pd.Series, NDArray[np.float64], List[float]]] = None) -> ValueStorage:
        """
        calculate_average_scaling load using the scaling or average profile
        :param number_of_buildings: number of buildings
        :param scaling_factor: scaling factor if simultaneity factor should not be considered
        :return: ValueStorage including the results
        """
        self.calculate_average_and_indexes()
        self.calculate_average_load()
        if scaling_factor is None:
            if len(self.values.scaling) < 1:
                self.calculate_simultaneity_factor()
            else:
                self.determine_scaling_profile_simultaneity_factor()
        else:
            self.new_simultaneity_factor = (
                np.array(scaling_factor, dtype=np.float64)
                if isinstance(scaling_factor, list)
                else scaling_factor.to_numpy(dtype=np.float64)
                if isinstance(scaling_factor, pd.Series)
                else scaling_factor
            )
        self.calculate_new_values(number_of_buildings)
        return self.values

    def calculate_average_and_indexes(self) -> None:
        """Calculate average load and indexes of:\n
            1: day; 2: week; 3: month; 4: year
        :return:
        """

        if self.period not in [1, 2, 3, 4]:
            raise ValueError("The period should be: 1,2,3,4")

        self._calculate_indexes(self.period, self.date)

    def _calculate_indexes(self, period: int, date: NDArray[np.float64]) -> None:
        """
        calculate_average_scaling the indexes for the selected period
        :param period: period to calculate_average_scaling mean for 1: day; 2: week; 3: month; 4: year
        :param date: date of original values
        :return: None
        """
        # period = day: getting index lists
        if period == 1:
            day_range = range(365)
            index_start = 0
            index = 0
            self.start = np.zeros(365, np.uint32)
            self.end = np.zeros(365, np.uint32)
            days = date.astype("datetime64[D]").astype(np.uint32)
            for i, date_i in enumerate(days - days[0]):
                if day_range[index] != date_i:
                    self.start[index] = index_start
                    self.end[index] = i
                    index += 1
                    index_start = i

            self.start[index] = index_start
            self.end[index] = len(date)

        # period = week: getting index lists
        elif period == 2:
            week_range = range(53)
            index_start = 0
            index = 0
            self.start = np.zeros(53, np.uint32)
            self.end = np.zeros(53, np.uint32)
            week = pd.to_datetime(date).strftime("%W").astype("int")
            for i, date_i in enumerate(week - week[0]):
                if week_range[index] != date_i:
                    self.start[index] = index_start
                    self.end[index] = i
                    index += 1
                    index_start = i

            self.start[index] = index_start
            self.end[index] = len(date)

        # period = month: getting index lists
        elif period == 3:
            month_range = range(12)
            index_start = 0
            index = 0
            self.start = np.zeros(12, np.uint32)
            self.end = np.zeros(12, np.uint32)
            for i, date_i in enumerate(date.astype("datetime64[M]").astype(np.uint32) % 12):
                if month_range[index] != date_i:
                    self.start[index] = index_start
                    self.end[index] = i
                    index += 1
                    index_start = i

            self.start[index] = index_start
            self.end[index] = len(date)

        # period = year: getting index lists
        else:
            self.start = np.array([0], np.uint32)
            self.end = np.array([len(date)], np.uint32)

    def calculate_average_load(self) -> None:
        """
        calculating the average loads\n
        """
        # calculating the average loads
        self.values.average = self.values.original if len(self.values.scaling) < 1 else self.values.scaling
        value_list: List[NDArray[np.float64]] = [self.values.average[start:end] for start, end in zip(self.start, self.end)]
        self.values.average = np.array([sum(entries) / len(entries) for entries in value_list])

    def calculate_simultaneity_factor(self) -> None:
        """
        Calculates the new simultaneity factor.
        :return:
        """
        # transform gzf to list with period times elements
        if len(self.simultaneity_factor) == 1:
            self.simultaneity_factor = np.multiply(np.ones(len(self.start)), self.simultaneity_factor)
        # getting max of period
        maximum_in_period: NDArray[np.float64] = np.array([max(self.values.original[start:end]) for start, end in zip(self.start, self.end)])

        # calculating the min simultaneity factor
        dividend: NDArray[np.float64] = self.simultaneity_factor * maximum_in_period - self.values.average
        divisor: NDArray[np.float64] = maximum_in_period - self.values.average
        self.new_simultaneity_factor = np.divide(dividend, divisor, out=np.zeros_like(dividend), where=divisor != 0)
        control_list = [avg / maxi if maxi > 1 else 0 for avg, maxi in zip(self.values.average, maximum_in_period)]
        # control if min simultaneity factor is smaller than calculated simultaneity factor raise value error if not smaller
        if (self.simultaneity_factor < control_list).any():
            raise ValueError(f"The simultaneity factor ({max(self.simultaneity_factor):.2f}) should not be smaller " f"than {max(control_list):.2f}")

    def calculate_with_scaling_profile(self, new_simultaneity_factor: NDArray[np.float64], start_idx: int, end_idx: int):
        """
        calculate error in the maximal value for the start until end index and the given simultaneity factor\n
        :param new_simultaneity_factor: new guessed simultaneity factor to calculate error for
        :param start_idx: start index
        :param end_idx: end index
        :return: absolute error of the maximal values
        """
        # getting max of period
        maximum_in_period: float = max(self.values.original[start_idx:end_idx])
        self.values.new = (
            new_simultaneity_factor[0] * self.values.original[start_idx:end_idx] + (1 - new_simultaneity_factor[0]) * self.values.scaling[start_idx:end_idx]
        )
        maximum_in_period_new: float = max(self.values.new)
        return abs(maximum_in_period_new - maximum_in_period * self.simultaneity_factor)

    def determine_scaling_profile_simultaneity_factor(self) -> None:
        """
        determine the simultaneity factors for the scaling profile approach using scipy minimize\n
        """
        start_value = np.ones(1) * self.simultaneity_factor
        self.new_simultaneity_factor = np.zeros_like(self.start, dtype=np.float64)
        # determine normal distribution variance which leads to the desired simultaneity factor using scipy minimize
        for idx, (start, end) in enumerate(zip(self.start, self.end)):
            res = optimize.minimize(
                self.calculate_with_scaling_profile,
                start_value,
                args=(start, end),
                method="Nelder-Mead",
                bounds=((-1, 2),),
                tol=1e-6,
            )
            self.new_simultaneity_factor[idx] = res.x[0]
            # print(idx, res.x[0], res.fun, (start, end))
            start_value = res.x[0] * np.ones(1)

    def calculate_new_values(self, number_of_buildings: int) -> None:
        """
        Calculates the new value for each timestamp.
        :return:
        """
        # calculating new values for timestamps scaled to average of

        if len(self.values.scaling) < 1:
            average: NDArray[np.float64] = np.zeros(len(self.values.original), dtype=np.float64)
            for start, end, avg in zip(self.start, self.end, self.values.average):
                average[start:end] = avg
        else:
            average = self.values.scaling
        simultaneity_factor: NDArray[np.float64] = np.zeros(len(self.values.original), dtype=np.float64)
        for start, end, d_f in zip(self.start, self.end, self.new_simultaneity_factor):
            simultaneity_factor[start:end] = d_f
        self.values.new = (simultaneity_factor * self.values.original + (1 - simultaneity_factor) * average) * float(number_of_buildings)


class NormalDistributionCalculation:
    """
    class to calculate_average_scaling scaled profile using the normal distribution approach\n
    """

    __slots__ = ("original_values", "new_values", "maximum", "maximum_index", "len_yr", "idx", "simultaneity_factor", "number_of_buildings")

    # set maximal variance, and its corresponding indexes
    max_sigma: int = 90
    # predetermine sqrt of 2 * pi to save calculation time
    sqrt_2 = 2**0.5

    def __init__(self, values: ValueStorage, simultaneity_factor: float, number_of_buildings: int):
        """
        init of NormalDistributionCalculation class\n
        :param values: ValueStorage to get original values from
        :param simultaneity_factor: simultaneity factor to be up-scaled
        :param number_of_buildings: number of buildings
        """
        # get original values
        self.original_values: NDArray[np.float64] = values.original
        # determine maximum in the original values and its index as well as the length of original values
        self.maximum: float = max(self.original_values)
        self.maximum_index: int = self.original_values.argmax(0)
        self.len_yr = len(self.original_values)
        # create index for the length of the year so that the indexes > len_yr start at the beginning and indexes < 0 at the end
        self.idx: NDArray[np.uint64] = np.append(np.arange(self.len_yr), np.arange(self.len_yr))
        # store simultaneity factor and number of buildings for later
        self.simultaneity_factor = simultaneity_factor
        self.number_of_buildings = number_of_buildings

    def calculate(self, complete_year: bool = False, sigma: Optional[float] = None) -> NDArray[np.float64]:
        """
        calculate_average_scaling up-scaled profile using the normal distribution method\n
        :param complete_year: should the complete year be considered during variance finding
        :param sigma: variance of normal distribution. If None it is calculated depending on the simultaneity factor
        :return: up-scaled values
        """
        if sigma is None:
            # determine normal distribution variance which leads to the desired simultaneity factor using scipy minimize
            res = optimize.minimize(
                self.calculate_error,
                np.ones(1) * 1,
                args=(complete_year,),
                method="Nelder-Mead",
                bounds=((0.1, self.max_sigma),),
                tol=1e-6,
            )
            # get variance from minimization results
            sigma = res.x[0]
        # raise an error if the variance is at the limits
        if np.isclose(sigma, 0.1) or np.isclose(sigma, self.max_sigma):
            raise ValueError(f"For the selected simultaneity factor ({self.simultaneity_factor}) no normal distribution can be calculated (sigma: {sigma})!")
        # calculate_average_scaling normal distribution
        values: NDArray[np.float64] = self.calculate_normal_distributed_values(range(self.len_yr), sigma)
        # check if the maximal value has changed to a different time step so that the optimization has to be performed for the complete year
        if not np.isclose(self.maximum * self.simultaneity_factor, max(values)):
            # check if the maximal value index has changed
            if values.argmax(0) != self.original_values.argmax(0) and not complete_year:
                # check if it has already changed and then calculate_average_scaling the complete year
                if self.original_values.argmax(0) != self.maximum_index:
                    return self.calculate(True)
                # otherwise change the maximal value index and calculate_average_scaling again
                self.maximum_index = values.argmax(0)
                return self.calculate(False)
        # return the new values up-scaled by the number of buildings
        return values * self.number_of_buildings

    def calculate_normal_distributed_values(self, ran_yr: range, sigma: float) -> NDArray[np.float64]:
        """
        calculate_average_scaling normal distributed values\n
        :param ran_yr: range of the year for which the new values should be calculated
        :param sigma: variance of normal distribution
        :return: NDArray[np.float64] of new values
        """
        # initialize results value array
        values = np.zeros(self.len_yr)
        # cut sigma into int
        sigma_int = int(sigma + 0.5)
        # create maximal sigma range
        maximal_range: NDArray[np.int64] = np.arange(-4 * sigma_int - 2, 4 * sigma_int + 2)
        # determine the idx range for the negative values
        idx_sigma: int = sigma_int * 4 + 2
        # pre calculate_average_scaling value to increase calculation speed
        erf_values = (erf((maximal_range + 0.5) / (sigma * self.sqrt_2)) - erf((maximal_range - 0.5) / (sigma * self.sqrt_2))) / 2
        # loop over the complete year
        for i in ran_yr:
            # just loop over the relevant elements before and after the current element i in the year
            for j in range(i - 4 * sigma_int - 1, i + 4 * sigma_int + 2):
                # determine the new values using the precalculated exponential values
                values[self.idx[j]] += self.original_values[self.idx[i]] * erf_values[idx_sigma + (j - i)]
        return values

    def calculate_error(self, sigma: NDArray[np.float64], complete_year: bool) -> float:
        """
        calculate_average_scaling normal distribution error for the input sigma\n
        :param sigma: Variance of normal distribution as array because scipy minimize is working with arrays
        :param complete_year: should the complete year be considered during variance finding
        :return: absolute difference of maximal values with simultaneity factor consideration
        """
        # get variance from array
        sigma_val = sigma[0]
        # create either a complete year or an around the maximal value range
        ran: range = (
            range(self.maximum_index - 4 * int(sigma_val + 0.5) - 1, self.maximum_index + 4 * int(sigma_val + 0.5) + 2)
            if not complete_year
            else range(self.len_yr)
        )
        # determine normal distributed values
        values: NDArray[np.float64] = self.calculate_normal_distributed_values(ran, sigma_val)
        # return absolute difference between maximum of original values considering the simultaneity factor and tha maximum of new values
        return float(abs(self.maximum * self.simultaneity_factor - max(values)))


class TimeSeriesScalingModule:
    """
    class to calculate_average_scaling an up-scaling profile
    """

    __slots__ = ("values", "number_of_buildings", "simultaneity_factor", "new_simultaneity_factor")

    def __init__(self, number_of_buildings: int, simultaneity_factor: Union[List[float], float]) -> None:
        """
        :param number_of_buildings: number of houses
        :param simultaneity_factor: the simultaneity factor for calculation
        """
        self.number_of_buildings: int = number_of_buildings
        self.simultaneity_factor: NDArray[np.float64] = np.array(
            simultaneity_factor if isinstance(simultaneity_factor, list) else [simultaneity_factor],
            dtype=np.float64,
        )
        self.new_simultaneity_factor: NDArray[np.float64] = np.zeros(0)
        self.values: ValueStorage = ValueStorage()

    def calculate_average_scaling(
        self, period: int, *, scaling_factor: Optional[Union[pd.Series, NDArray[np.float64], List[float]]] = None
    ) -> NDArray[np.float64]:
        """
        calculate new time series by using the scaling approach\n
        :param period: period of time(1: day; 2:week; 3: month; 4:year) for which average is going to be calculated
        calculate_average_scaling load using the scaling profile
        :param scaling_factor: scaling factor if simultaneity factor should not be considered
        :return: new time series as numpy array
        """
        idx = AverageScalingCalculation(self.values, period, self.simultaneity_factor)
        self.values = idx.calculate(self.number_of_buildings, scaling_factor=scaling_factor)
        return self.values.new

    def calculate_linear(self, period: int, *, scaling_factor: Optional[Union[pd.Series, NDArray[np.float64], List[float]]] = None) -> NDArray[np.float64]:
        """
        calculate new time series by using the linear approach\n
        :param period: period of time(1: day; 2:week; 3: month; 4:year) for which average is going to be calculated
        calculate_average_scaling load using the scaling profile
        :param scaling_factor: scaling factor if simultaneity factor should not be considered
        :return: new time series as numpy array
        """
        asc = AverageScalingCalculation(self.values, period, self.simultaneity_factor)
        self.values = asc.calculate(self.number_of_buildings, scaling_factor=scaling_factor)
        return self.values.new

    def calculate_normal_distribution(self, sigma: Optional[float] = None) -> NDArray[np.float64]:
        """
        calculate_average_scaling new profile using the normal distribution approach
        :param sigma: variance if it should not be calculated
        :return: new time series as numpy array
        """
        cnd = NormalDistributionCalculation(self.values, self.simultaneity_factor[0], self.number_of_buildings)
        self.values.new = cnd.calculate(sigma is not None, sigma)
        return self.values.new

    def save_2_csv(self, data_name: Optional[str] = None) -> str:
        """
        exports result Dataframe to csv.\n
        :param data_name: name of file with results
        :return: data name string
        """

        result_array: NDArray[np.float64] = np.column_stack(
            [
                self.values.original,
                self.values.original * self.number_of_buildings,
                self.values.new,
            ]
        )

        result_df: pd.DataFrame = pd.DataFrame(
            result_array,
            columns=[
                "original values",
                "house factorised",
                "simultaneity factorised",
            ],
        )
        result_df["Date"] = pd.Series(self.values.date)
        result_df.set_index("Date")
        data_name = "./scaled_time_series.csv" if data_name is None else data_name
        result_df.to_csv(data_name, index=True)
        return data_name
