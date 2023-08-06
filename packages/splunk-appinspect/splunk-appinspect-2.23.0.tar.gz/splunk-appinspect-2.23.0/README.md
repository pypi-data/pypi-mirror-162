# Splunk AppInspect

This repo is hosted [here on Gitlab](https://cd.splunkdev.com/appinspect/appinspect-cli)
and configured to mirror (push to) the [repo on Github](https://github.com/splunk/appinspect)
to make use of the Github Windows runner for testing on Windows.

All commits should be made to the repo on Gitlab.

If you are here to make code changes, see [Things every developer should know about this code](#Things every developer should know about this code). It will save you a lot of pain...

## Build Status

![Pipeline Status](https://cd.splunkdev.com/appinspect/appinspect-cli/badges/main/pipeline.svg)

## Overview

AppInspect is a tool for assessing a Splunk App's compliance with Splunk recommended development practices, by using static analysis. AppInspect is open for extension, allowing other teams to compose checks that meet their domain specific needs for semi- or fully-automated analysis and validation of Splunk Apps.

## Documentation

You can find the documentation for Splunk AppInspect at http://dev.splunk.com/goto/appinspectdocs.

## Local Development

Use the following steps to setup AppInspect for local development.
### Install from source
* Checkout the source code
* Create and activate a [virtual env](http://docs.python-guide.org/en/latest/dev/virtualenvs)
* Build and install from source
	- install libmagic (`brew install libmagic` on macOS)
	- `make install`, if you see any error like `ValueError: bad marshal data`, try run `find ./ -name '*.pyc' -delete` first.
	**Caution**: Do not delete the pyc file below which is used for tests.
	 `test/unit/packages/has_disallowed_file_extensions/has_pyc_file/configuration_parser.pyc`
	- That's it. The `splunk-appinspect` tool is installed into your virtualenv. You can verify this by running the following commands:
   		- `splunk-appinspect`
    	- `splunk-appinspect list version`

### Run CLI directly from codebase
* Install all dependencies, `pip install -r (windows|darwin|linux).txt`, it depends on your system platform
* Add current folder into PYTHONPATH, `export PYTHONPATH=$PYTHONPATH:.`
* Run the CLI, `scripts/splunk-appinspect list version`

### Build the distribution package
* Create a distribution of AppInspect
    - `make build` 
    - after running the above command, an installation package with name like `splunk-appinspect-<version>.tar.gz` is created under the `dist` folder
* Install the distro previously created
    - `pip install dist/splunk-appinspect-<version>.tar.gz`

### Run all code beautifiers (isort, black)
```
pip install -r requirements-dev.txt
make pretty
```

### Run tests
Once you have the `splunk-appinspect` tool installed, you can run tests by following the steps below.

* Install the Unit & Integration Test Requirements
    - `pip install -r test/(windows|darwin|linux).txt`, it depends on your system platform
* Ensure the Unit tests pass
    - `pytest -v test/unit/`

### Things every developer should know about this code

* the unit tests are defined in a set of CSV files. They are located at `test/unit/test_scenarios`
* to inject test files into the mock-app your check will be applied against, create a folder in directory `test/unit/packages`. The test plumbling will automagically inject whatever you put in that directory into the app object that gets used in that test run. 
* there are a gazillion tests and you probably don't want to run all of them when writing a new check. The `-k {FILTER}` pytest option will allow you to only run tests with names that contain the `{FILTER}` text. 
  * for example, if you only want to run unit tests with the name `check_for_languages` in the name, the command `pytest -v -k check_for_languages test/unit/` will do the trick. 
* if you want to see log output from your check and pytest is not showing it to you, the option `-o log_cli=true` should do the trick. 
* the file `VERSION.txt` sets the version for the app. If your new check has a metadata tag wherein the version is `<` what's in the version file, the app will act as if that check doesn't exist. Moreover, tests will fail because - as far as the app is concerned - the check doesn't exist.
* There is a known bug with the testing suite. If you are not running the tests in a Python 3.8 context some stuff is going to fail. The bug is tracked [here](https://jira.splunk.com/browse/A3-188). The CI/CD pipeline will run the tests on every commit. The link to CI/CD jobs is [here](https://cd.splunkdev.com/appinspect/appinspect-cli/-/jobs)
* **The consequence of having two pipelines is that YOU NEED TO MAKE SURE ALL TESTS PASS IN *BOTH* PIPELINES BEFORE YOUR PR CAN BE APPROVED.**

