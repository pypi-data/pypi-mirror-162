# ALMAFE-Lib package
Contains reusable tools which are required by other ALMAFE packages.

## ALMAFE.basic.ParseTimeStamp module

### class ParseTimeStamp:
Helper object for parsing time stamps in a variety of formats.
Caches last matching time stamp format string to speed subsequent calls.

### function makeTimeStamp(timeStamp = None):
initialized a timestamp from provided, or now() if None provided
:param timeStamp: string or datetime or None

## ALMAFE.basic.StripQuotes:
Utility to strip quotes from a string, if present.

## ALMAFE.common.GitVersion:

### function gitVersion():
Return the current Git tag (if any) and revision as a string

### function gitBranch():
Return the current Git branch name as a string

## ALMAFE.database.DriverMySQL:

### class DriverMySQL():
Driver wrapper for mysql-connector-python
Provides a uniform interface to SQL user code

### class DriverSQLite():
Driver wrapper for sqlite3
Provides a uniform interface to SQL user code
