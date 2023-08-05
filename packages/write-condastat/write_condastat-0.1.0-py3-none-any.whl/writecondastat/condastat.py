"""A module for working with conda statistics."""

import calendar
import os
from os import PathLike
from datetime import datetime, timedelta
from typing import Optional, Union, List, Dict
from enum import Enum

import dask.dataframe as dd
import pandas as pd  # type: ignore
import numpy as np


from .statdate import StatPeriod, StatDate


class CondaStatDataSource(Enum):
    """A class for storing data source types."""

    ANACONDA = "anaconda"
    CONDAFORGE = "conda-forge"
    BIOCONDA = "bioconda"


class WriteCondaStat:
    """
    A class for collecting, filtering and saving conda statistics to csv files.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(
        self, package_name: str, outdir: Optional[Union[PathLike, str]] = None
    ):
        """
        WriteCondaStat constructor.

        Args:
            package_name: Name of the target conda package.
            outdir (optional): Path of the directory where the gathered data
                will be saved into csv files.
        """

        self._package_name = package_name
        self._outdir = outdir

        self._date_period = StatPeriod.YEAR

        self._write_package_name = False
        self._merge_stored_data = True
        self._fill_no_data = True
        self._drop_percent_column = True
        self._drop_total_row = True

    @property
    def outdir(self) -> Optional[Union[PathLike, str]]:
        """
        A property for storing outdir.

        Path of the directory where the gathered data will be saved into csv files.
        """

        return self._outdir

    @outdir.setter
    def outdir(self, outdir: Optional[Union[PathLike, str]] = None) -> None:
        self._outdir = outdir

    @property
    def date_period(self) -> StatPeriod:
        """
        A property for storing date_period that is
        the time period of the statistics.
        """

        return self._date_period

    @date_period.setter
    def date_period(self, date_period: StatPeriod = StatPeriod.YEAR) -> None:
        self._date_period = StatPeriod(date_period)

    @property
    def write_package_name(self) -> bool:
        """
        A property for storing write_package_name that is
        a flag for writing the name of the package into a csv column.
        """

        return self._write_package_name

    @write_package_name.setter
    def write_package_name(self, write_package_name: bool = False):
        self._write_package_name = bool(write_package_name)

    @property
    def merge_stored_data(self) -> bool:
        """
        A property for storing merge_stored_data that is
        a flag for merging actual conda statistics with previously stored.
        """

        return self._merge_stored_data

    @merge_stored_data.setter
    def merge_stored_data(self, merge_stored_data: bool = True):
        self._merge_stored_data = bool(merge_stored_data)

    @property
    def fill_no_data(self) -> bool:
        """
        A property for storing fill_no_data that is
        a flag for creating empty lines with 0 download when data is not available.
        """

        return self._fill_no_data

    @fill_no_data.setter
    def fill_no_data(self, fill_no_data: bool = True):
        self._fill_no_data = bool(fill_no_data)

    @staticmethod
    def download_condastat(
        *data_source: Union[CondaStatDataSource, str],
        year: str,
        month: str,
        day: str,
        package: str,
    ) -> Optional[pd.DataFrame]:
        """
        A method for downloading and filtering conda statistics.

        Args:
            *data_source: Data source of the statistics.
                For example anaconda, conda-forge, bioconda.
            year: Year of the statistics.
            month: Month of the statistics.
            day: Day of the statistics.
            package: Name of the package.

        Returns:
            The filtered conda statistics.
        """

        none_stat = None
        try:
            stat_url = "s3://anaconda-package-data/conda/hourly"
            stat = dd.read_parquet(
                f"{stat_url}/{year}/{month}/{year}-{month}-{day}.parquet",
                storage_options={"anon": True},
            )
        except FileNotFoundError:
            return none_stat
        sources = [CondaStatDataSource(source).value for source in data_source]
        stat = stat.loc[
            (stat["data_source"].isin(sources)) & (stat.pkg_name == package)
        ]
        stat = stat.drop(columns=["time", "pkg_name"])
        stat = stat.groupby(
            ["data_source", "pkg_version", "pkg_platform", "pkg_python"]
        ).sum()
        stat = stat.reset_index()
        stat = stat.compute()

        stat = stat[stat["counts"] != 0]
        if stat.empty:
            return none_stat
        stat.insert(0, "package", f"{package}")
        stat.insert(0, "date", f"{year}-{month}-{day}")
        stat.rename(columns={"counts": "downloads"}, inplace=True)
        return stat

    def get_condastat(
        self,
        *data_source: Union[CondaStatDataSource, str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Returns conda statistics.

        Args:
            *data_source: Type of the data source.
                For example CondaStatDataSource.CONDAFORGE.
            start_date (optional): Start date of the statistics,
                should be in one of the following formats:
                - %Y, for example 2022 will be 2022-01-01.
                - %Y-%m, for example 2022-01 will be 2022-01-01.
                - %Y-%m-%d, for example 2022-01-01 will be 2022-01-01.
                - None will be the the date that was two months ago.
            end_date (optional): End date of the statistics,
                should be in one of the following formats:
                - %Y, for example 2022 will be 2022-12-31.
                - %Y-%m, for example 2022-12 will be 2022-12-31.
                - %Y-%m-%d, for example 2022-12-31 will be 2022-12-31.
                - None will be the actual date.

        Returns:
            The gathered conda statistics.
        """

        stat_date = StatDate(start=start_date, end=end_date)
        return self._get_condastat(*data_source, stat_date=stat_date)

    def _get_condastat(
        self, *data_source: Union[CondaStatDataSource, str], stat_date: StatDate
    ) -> Optional[pd.DataFrame]:
        stats = None
        for i in range((stat_date.end - stat_date.start).days + 1):
            date = stat_date.start + timedelta(days=i)
            year = date.strftime("%Y")
            month = date.strftime("%m")
            day = date.strftime("%d")
            new_stats = WriteCondaStat.download_condastat(
                *data_source,
                year=year,
                month=month,
                day=day,
                package=self._package_name,
            )
            if new_stats is not None:
                stats = pd.concat([stats, new_stats], ignore_index=True, sort=False)
        if stats is not None:
            if not self.write_package_name:
                stats.drop(["package"], inplace=True, axis=1, errors="ignore")
            stats.sort_values(
                self._get_columns()[:-1],
                inplace=True,
            )
            date_index = stats.pop("date")
            stats.insert(0, date_index.name, date_index)
            stats = WriteCondaStat._set_data_frame_columns(stats)
        return stats

    def _get_columns(self) -> List[str]:
        header = []
        header.append("date")
        header.append("data_source")
        if self.write_package_name:
            header.append("package")
        header.append("pkg_version")
        header.append("pkg_platform")
        header.append("pkg_python")
        header.append("downloads")
        return header

    def _get_condastat_by_none(
        self,
        *data_source: Union[CondaStatDataSource, str],
        stat_date: StatDate,
        postfix: Optional[str] = None,
    ) -> List[Dict[str, Union[str, pd.DataFrame, None]]]:
        stats = []
        stat_file = postfix if postfix is not None else "condastat"
        stat_file += ".csv"
        stat = self._get_condastat(*data_source, stat_date=stat_date)
        if self.merge_stored_data:
            stat = WriteCondaStat._concat_with_stored_condastat(
                stat,
                self._get_stored_condastat(stat_file),
                self._get_columns()[:-1],
            )
        if self.fill_no_data:
            stat = self._concat_with_no_data(stat, stat_date)
        stats.append({"stat": stat, "stat_file": stat_file})
        return stats

    def _get_condastat_by_year(
        self,
        *data_source: Union[CondaStatDataSource, str],
        start_date: datetime,
        end_date: datetime,
        postfix: Optional[str] = None,
    ) -> List[Dict[str, Union[str, pd.DataFrame, None]]]:
        stats = []
        years = []
        actual_start_date = start_date
        actual_year_end = None
        actual_end_date = None
        for i in range((end_date - start_date).days + 1):
            day = start_date + timedelta(days=i)
            stat_file = day.strftime("%Y") + "_"
            stat_file += postfix if postfix is not None else "condastat"
            stat_file += ".csv"
            if day.year not in years:
                years.append(day.year)
                actual_year_end = datetime(day.year, 12, 31)
                actual_end_date = (
                    actual_year_end if actual_year_end <= end_date else end_date
                )
                stat_date = StatDate(
                    start=actual_start_date.strftime("%Y-%m-%d"),
                    end=actual_end_date.strftime("%Y-%m-%d"),
                )
                stat = self._get_condastat(*data_source, stat_date=stat_date)
                if self.merge_stored_data:
                    stat = WriteCondaStat._concat_with_stored_condastat(
                        stat,
                        self._get_stored_condastat(stat_file),
                        self._get_columns()[:-1],
                    )
                if self.fill_no_data:
                    stat = self._concat_with_no_data(stat, stat_date)
                stats.append({"stat": stat, "stat_file": stat_file})
                actual_start_date = actual_year_end + timedelta(days=1)
        return stats

    def _get_condastat_by_month(
        self,
        *data_source: Union[CondaStatDataSource, str],
        start_date: datetime,
        end_date: datetime,
        postfix: Optional[str] = None,
    ) -> List[Dict[str, Union[str, pd.DataFrame, None]]]:
        stats = []
        months = []
        actual_start_date = start_date
        actual_month_end = None
        actual_end_date = None
        for i in range((end_date - start_date).days + 1):
            day = start_date + timedelta(days=i)
            stat_file = day.strftime("%Y-%m") + "_"
            stat_file += postfix if postfix is not None else "condastat"
            stat_file += ".csv"
            if day.month not in months:
                months.append(day.month)
                actual_month_end = datetime(
                    day.year, day.month, calendar.monthrange(day.year, day.month)[1]
                )
                actual_end_date = (
                    actual_month_end if actual_month_end <= end_date else end_date
                )
                stat_date = StatDate(
                    start=actual_start_date.strftime("%Y-%m-%d"),
                    end=actual_end_date.strftime("%Y-%m-%d"),
                )
                stat = self._get_condastat(*data_source, stat_date=stat_date)
                if self.merge_stored_data:
                    stat = WriteCondaStat._concat_with_stored_condastat(
                        stat,
                        self._get_stored_condastat(stat_file),
                        self._get_columns()[:-1],
                    )
                if self.fill_no_data:
                    stat = self._concat_with_no_data(stat, stat_date)
                stats.append(
                    {
                        "stat": stat,
                        "stat_file": stat_file,
                    }
                )
                actual_start_date = actual_month_end + timedelta(days=1)
        return stats

    def _get_condastat_by_day(
        self,
        *data_source: Union[CondaStatDataSource, str],
        start_date: datetime,
        end_date: datetime,
        postfix: Optional[str] = None,
    ) -> List[Dict]:
        stats = []
        for i in range((end_date - start_date).days + 1):
            day = start_date + timedelta(days=i)
            stat_file = day.strftime("%Y-%m-%d") + "_"
            stat_file += postfix if postfix is not None else "condastat"
            stat_file += ".csv"
            stat_date = StatDate(
                start=day.strftime("%Y-%m-%d"), end=day.strftime("%Y-%m-%d")
            )
            stat = self._get_condastat(*data_source, stat_date=stat_date)
            if self.merge_stored_data:
                stat = WriteCondaStat._concat_with_stored_condastat(
                    stat,
                    self._get_stored_condastat(stat_file),
                    self._get_columns()[:-1],
                )
            if self.fill_no_data:
                stat = self._concat_with_no_data(stat, stat_date)
            stats.append(
                {
                    "stat": stat,
                    "stat_file": stat_file,
                }
            )
        return stats

    def _get_stored_condastat(self, stat_file: str) -> Optional[pd.DataFrame]:
        stat = None
        if self.outdir:
            stat_file_path = os.path.join(self.outdir, stat_file)
            if os.path.exists(stat_file_path):
                stat = pd.read_csv(
                    stat_file_path,
                    dtype={"downloads": int, "pkg_version": str, "pkg_python": str},
                )
                stat = WriteCondaStat._set_data_frame_columns(stat)
        return stat

    @staticmethod
    def _concat_with_stored_condastat(
        stat: Optional[pd.DataFrame],
        stat_stored: Optional[pd.DataFrame],
        keys: List[str],
    ) -> Optional[pd.DataFrame]:

        if stat is None:
            return stat_stored
        if stat_stored is None:
            return stat

        stat = WriteCondaStat._merge_data_frames(stat, stat_stored, keys)

        return stat

    @staticmethod
    def _get_days(stat_date: StatDate) -> List[str]:
        days = []
        for i in range((stat_date.end - stat_date.start).days + 1):
            day = stat_date.start + timedelta(days=i)
            days.append(day.strftime("%Y-%m-%d"))
        return days

    def _concat_with_no_data(
        self, stat: Optional[pd.DataFrame], stat_date: StatDate
    ) -> pd.DataFrame:
        days = WriteCondaStat._get_days(stat_date)

        no_data = {
            "date": days,
            "package": self._package_name,
            "data_source": np.nan,
            "pkg_version": np.nan,
            "pkg_platform": np.nan,
            "pkg_python": np.nan,
            "downloads": 0,
        }

        if not self.write_package_name:
            del no_data["package"]

        if stat is not None:
            no_data_df = pd.DataFrame(data=no_data)
            no_data_df = WriteCondaStat._merge_data_frames(
                stat,
                no_data_df,
                self._get_columns()[:-1],
            )
        else:
            no_data_df = pd.DataFrame(data=no_data)
            no_data_df = WriteCondaStat._set_data_frame_columns(no_data_df)

        return no_data_df

    @staticmethod
    def _merge_data_frames(
        dataf1: pd.DataFrame, dataf2: pd.DataFrame, keys: List[str]
    ) -> pd.DataFrame:
        dataf1 = dataf1.replace("null", np.nan)
        dataf1 = dataf1.replace("nan", np.nan)
        dataf1 = WriteCondaStat._set_data_frame_columns(dataf1)
        dataf2 = dataf2.replace("null", np.nan)
        dataf2 = dataf2.replace("nan", np.nan)
        dataf2 = WriteCondaStat._set_data_frame_columns(dataf2)
        merged = pd.merge(dataf1, dataf2, how="outer", on=[*keys], suffixes=("", "_y"))
        merged.sort_values([*keys], inplace=True)
        merged.downloads.fillna(merged.downloads_y, inplace=True)
        merged.drop(["downloads_y"], inplace=True, axis=1, errors="ignore")
        return merged

    @staticmethod
    def _set_data_frame_columns(dataf: pd.DataFrame) -> pd.DataFrame:
        for col in dataf.columns:
            if col != "downloads":
                dataf[col] = dataf[col].astype(str)
            else:
                dataf[col] = dataf[col].astype(int)
        return dataf

    @staticmethod
    def _filter_data_frame_rows(stat: pd.DataFrame) -> pd.DataFrame:
        stat = WriteCondaStat._set_data_frame_columns(stat)
        stat = stat.drop_duplicates()
        df_zero = stat[stat["downloads"] == 0]
        df_no_zero = stat[stat["downloads"] != 0]
        stat = stat.drop(df_zero.index[df_zero["date"].isin(df_no_zero["date"])])
        return stat

    def write_condastat(
        self,
        *data_source: Union[CondaStatDataSource, str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        postfix: Optional[str] = None,
    ) -> None:
        """
        Writes conda statistics into csv files.

        Args:
            *data_source: Type of the data source.
                For example CondaStatDataSource.CONDAFORGE.
            start_date (optional): Start date of the statistics,
                should be in one of the following formats:
                - %Y, for example 2022 will be 2022-01-01.
                - %Y-%m, for example 2022-01 will be 2022-01-01.
                - %Y-%m-%d, for example 2022-01-01 will be 2022-01-01.
                - None will be the earliest available date.
            end_date (optional): End date of the statistics,
                should be in one of the following formats:
                - %Y, for example 2022 will be 2022-12-31.
                - %Y-%m, for example 2022-12 will be 2022-12-31.
                - %Y-%m-%d, for example 2022-12-31 will be 2022-12-31.
                - None will be the actual date.
            postfix (optional): Postfix of the csv files.
        """

        stat_date = StatDate(start=start_date, end=end_date)
        self._write_condastats(*data_source, stat_date=stat_date, postfix=postfix)

    def _write_condastats(
        self,
        *data_source: Union[CondaStatDataSource, str],
        stat_date: StatDate,
        postfix: Optional[str],
    ) -> None:
        stats = []
        if self.date_period == StatPeriod.DAY:
            stats += self._get_condastat_by_day(
                *data_source,
                start_date=stat_date.start,
                end_date=stat_date.end,
                postfix=postfix,
            )
        elif self.date_period == StatPeriod.MONTH:
            stats += self._get_condastat_by_month(
                *data_source,
                start_date=stat_date.start,
                end_date=stat_date.end,
                postfix=postfix,
            )
        elif self.date_period == StatPeriod.YEAR:
            stats += self._get_condastat_by_year(
                *data_source,
                start_date=stat_date.start,
                end_date=stat_date.end,
                postfix=postfix,
            )
        else:
            stats += self._get_condastat_by_none(
                *data_source, stat_date=stat_date, postfix=postfix
            )

        for stat in stats:
            self._write_csv(stat["stat"], stat["stat_file"])

    def _write_csv(self, stat: Optional[pd.DataFrame], stat_file: str) -> None:
        if stat is not None:
            if self.outdir:
                os.makedirs(self.outdir, exist_ok=True)
                stat = WriteCondaStat._filter_data_frame_rows(stat)
                stat.to_csv(
                    os.path.join(self.outdir, stat_file), index=False, encoding="utf-8"
                )
