[![PyPI version](https://badge.fury.io/py/write-condastat.svg)](https://badge.fury.io/py/write-condastat)
[![CI-CD](https://github.com/veghdev/write-condastat/actions/workflows/cicd.yml/badge.svg?branch=main)](https://github.com/veghdev/write-condastat/actions/workflows/cicd.yml)


# About The Project

write-condastat makes it easy to collect, filter and save conda statistics to csv files.

# Installation

write-condastat requires `pandas`, `dask`, `pyarrow` and `s3fs` packages.

```sh
pip install write-condastat
```

# Usage

```python
from writecondastat import WriteCondaStat, CondaStatDataSource

target_package = "pandas"
csv_dir = "stats/pandas"
write_condastat = WriteCondaStat(package_name=target_package, outdir=csv_dir)

write_condastat.write_condastat(
    CondaStatDataSource.CONDAFORGE,
    start_date="2021",
    end_date="2022-03",
)

write_condastat.date_period = "month"
write_condastat.write_condastat(
    CondaStatDataSource.ANACONDA,
    CondaStatDataSource.CONDAFORGE,
    CondaStatDataSource.BIOCONDA,
    start_date="2022-01",
    end_date="2022-04-15",
)
```

Visit our [documentation](https://veghdev.github.io/write-condastat/) site for code reference or 
our [wiki](https://github.com/veghdev/write-condastat/wiki/) site for a step-by-step tutorial into write-condastat.

# Contributing

We welcome contributions to the project, visit our [contributing](https://github.com/veghdev/write-condastat/blob/main/CONTRIBUTING.md) guide for further info.

# Contact

Join our [discussions](https://github.com/veghdev/write-condastat/discussions) page if you have any questions or comments.

# License

Copyright © 2022.

Released under the [Apache 2.0 License](https://github.com/veghdev/write-condastat/blob/main/LICENSE).
