# pure-sql

[![PyPI Version][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![Code Coverage][coverage-image]][coverage-url]

> keep sql outside of Python code

This is just a stripped down version of https://github.com/nackjicholson/aiosql. Only the reading and parsing of
a sql file is being kept. No dynamic SQL query building and no execution.

Reason:
- reduction of magic and complexity
- execution of raw SQL is handled by SQLAlchemy already
- handling SQL dialect variety adds lots of complexity which is already covered by SQLAlchemy
- major benefit is just to reuse raw sql in `file.sql` and be able to execute it within and outside of Python

Installation:
```shell
pip install pure-sql
```

## Changelog
[CHANGELOG.md](https://github.com/sysid/pure-sql/blob/master/CHANGELOG.md)

<!-- Badges -->

[pypi-image]: https://badge.fury.io/py/pure-sql.svg
[pypi-url]: https://pypi.org/project/pure-sql/
[build-image]: https://github.com/sysid/pure-sql/actions/workflows/build.yml/badge.svg
[build-url]: https://github.com/sysid/pure-sql/actions/workflows/build.yml
[coverage-image]: https://codecov.io/gh/sysid/pure-sql/branch/master/graph/badge.svg
[coverage-url]: https://codecov.io/gh/sysid/pure-sql
