# Mettle #

Bitsmiths-Mettle is the supporting code generators and python libraries for the Mettle project.

See our <a href="https://bitbucket.org/bitsmiths_za/mettle.git">repo</a> and main *README* for more details!


## Requirements ##

Python 3.10+


## Installation ##

```console
$ pip install bitsmiths-mettle

---> 100%
```

## Change History ##

### 2.2.2 ###

| Type   | Description |
| ------ | ----------- |
| Fix | Fixed an import issue with the Braze TCP overload in python. |

### 2.2.1 ###

| Type   | Description |
| ------ | ----------- |
| Fix | Applied `couplet` identifier improvement to braze couplets on python. |

### 2.2.0 ###

| Type   | Description |
| ------ | ----------- |
| New    | Added a `database_name()` method to all db connections. |
| New    | Select one statements that fail, will now raise the new `DBNotFound` error code. |
| New    | Added `psycopg3` database extension for `python3`. |
| New    | Added `psycopg3 async` database extension for `python3`. |
| New    | Python generation for `__slots__` added, requires python 3.10 and up. |
| New    | Added a `must_exist` optional parameter to the python generated `fetch()` methods which will raise an error if the fetch fails. |
| Breaking | In the python generated `fetch_all()` methods, renamed `clearList` to `clear_list`. |
| Breaking | Improved the genartion of `couplet` identifier names. This may cause some couplets to be generated with differnt names. |
| Bug    | Foreign key, and unique key violations now proplerly thrown for all the python db drivers. |

### 2.1.14 ###

| Type   | Description |
| ------ | ----------- |
| New    | Added a new python generator option `fetch.method`. Options are `c++` which is the legacy option and `python` which adds a fetch iterator method and creates a new object for each fetch instead of reusing the existing `orec`. |
| New    | Removed the `__del__` dunder from the python DAO code generation as it is not needed. |

### 2.1.13 ###

| Type   | Description |
| ------ | ----------- |
| New    | Angular makefile generators can now be dynamically extended with a different CC, and TARGS as well as have optional overwrite commands. |
| Bug    | Fixed configuration bug from the 2.1.12 where a null dataclass would cause a generation error. |

### 2.1.12 ###

| Type   | Description |
| ------ | ----------- |
| New    | Python database and braze models can now be generated with (pydantic, or dataclass, or attrs) as an option. |
| New    | Python database and braze models can now toggle (pk, serializer, dav, clear) features an and off. |

### 2.1.11 ###

| Type   | Description |
| ----   | ----------- |
| Bug    | Fixed a refactor of `errCode` to `err_code` that was not rippled through some of the base library code/ |


### 2.1.10 ###

| Type   | Description |
| ----   | ----------- |
| Change | General typing improvements, and minor bug fixes. |



## License ##

This project is licensed under the terms of the MIT license.
