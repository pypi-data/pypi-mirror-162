# squad-report
Create human-friendly reports from software quality data.

[squad](https://github.com/Linaro/squad) is a software quality dashboard.
The service provides storage and a public API.

[squad-client](https://github.com/Linaro/squad-client) is a client library.
The library fetches data from a `squad` service API.

[squad-report](https://gitlab.com/Linaro/lkft/reports/squad-report) is
a command-line program that uses `squad-client` to create human-friendly
reports using software quality data from a `squad` service.

## Install
Use [pip](https://pip.pypa.io/en/stable/) to install from `pypi`.
```
pip install squad-report
```

## Config
The user-specific config file is located at `~/.config/squad_report/config.yaml`.

NOTE: All config values will override command-line options.

### Example config
```
config: &config
    sig_name: "Anders Roxell"
    sig_url: "https://lkft.linaro.org"
    email_from: "LKFT <lkft@linaro.org>"
    email_to: "LKFT <lkft@linaro.org>"
    email_subject: "LKFT Test Report"
    reported_tested_by: "Anders Roxell <anders.roxell@linaro.org>"

report:
  - name: report
    << : *config
    email_subject: "testing Stable RC reports"
    template: report
    output: report.txt
```

### Example config usage
```
$ squad-report \
        --config-report-type=report \
        --group=lkft --project=linux-next-master --build=next-20210223
Report created in report.txt

$ cat report.txt
From: LKFT <lkft@linaro.org>
To: LKFT <lkft@linaro.org>
Cc:
Subject: [REGRESSION] testing Stable RC reports

## Build
* kernel: 5.11.0
* git: ['https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git', 'https://gitlab.com/Linaro/lkft/mirrors/next/linux-next']
* git branch: master
* git commit: 8431fb50e1a7ffe7fcc4da2f798d3100315cee7b
* git describe: next-20210223
* test details: https://qa-reports.linaro.org/lkft/linux-next-master/build/next-20210223

...

Reported-by: Anders Roxell <anders.roxell@linaro.org>

...

--
Anders Roxell
https://lkft.linaro.org
```

## Templates
The user-specific template directory is located at `~/.config/squad_report/templates`.

If you want to add your own templates, you need to copy them to the above directory with a name of `<template>.txt.jinja`.

## Email
You can specify email headers to be included in the report so you can send it out later.

The email subject can be templated. For example:
```
build: {{ build.metadata.kernel_version }}/{{ build.version }}
```

NOTE: Email headers will only be present if you specify the email subject.

### Example email usage
```
$ squad-report \
        --email-from="lkft@linaro.org" \
        --email-to="lkft@linaro.org"   \
        --email-subject="report for linux-next" \
        --group=lkft --project=linux-next-master --build=next-20210223 \
        --template=report --output=report.txt
Report created in report.txt

$ head -n 15 report.txt
From: lkft@linaro.org
To: lkft@linaro.org
Cc: None
Subject: [REGRESSION] report for linux-next

## Build
* kernel: 5.11.0
* git: ['https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git', 'https://gitlab.com/Linaro/lkft/mirrors/next/linux-next']
* git branch: master
* git commit: 8431fb50e1a7ffe7fcc4da2f798d3100315cee7b
* git describe: next-20210223
* test details: https://qa-reports.linaro.org/lkft/linux-next-master/build/next-20210223

...

```

## Examples
Create a report from a `squad` project
```
squad-report --group=lkft --project=linux-next-master --build=next-20210223 --template=report-full
```

Create a report that shows build results for all environments
```
squad-report --group=lkft --project=linux-next-master --build=next-20210223 --suites=build --template=report-full
```

Create a report that shows build results for the `arm64` environment
```
squad-report --group=lkft --project=linux-next-master --build=next-20210223 --suites=build --environments=arm64 --template=report-full
```

Create a report that shows `kselftest` results
```
squad-report --group=lkft --project=linux-next-master --build=next-20210223 --suite-prefixes=kselftest --template=report-full
```

Create a performance report for sysbenchcpu data using mmtests
```
squad-report --group=~anders.roxell --project=linux-stable-linux-5.10.y --build=v5.10.93
      --base-build=v5.10.90 --environments=x86 --suites=mmtests-sysbenchcpu-tests
      --template=perf-report --perf-report-hook=mmtests --perf-report-hook-args=/path/to/mmtests
```

## Usage
```
usage: squad-report [-h] [--cache CACHE] [--token TOKEN] [--url URL]
       [--group GROUP] [--project PROJECT] [--build BUILD] [--base-build BASE_BUILD]
       [--environments ENVIRONMENTS | --environment-prefixes ENVIRONMENT_PREFIXES]
       [--suites SUITES | --suite-prefixes SUITE_PREFIXES]
       [--email-cc EMAIL_CC] [--email-from EMAIL_FROM] [--email-subject EMAIL_SUBJECT] [--email-to EMAIL_TO]
       [--output OUTPUT] [--send-on SEND_ON] [--template TEMPLATE]
       [--config CONFIG] [--config-report-type CONFIG_REPORT_TYPE]
       [--perf-report-hook SCRIPT] [--perf-report-hook-args ARGS] [--unfinished] [--version]

Create a report using data from SQUAD

optional arguments:
  -h, --help            show this help message and exit
  --cache CACHE         Cache squad-client requests with a timeout
  --token TOKEN         Authenticate to SQUAD using this token
  --url URL             URL of the SQUAD service
  --group GROUP         SQUAD group
  --project PROJECT     SQUAD project
  --build BUILD         SQUAD build
  --base-build BASE_BUILD
                        SQUAD build to compare to
  --environments ENVIRONMENTS
                        List of SQUAD environments to include
  --environment-prefixes ENVIRONMENT_PREFIXES
                        List of prefixes of SQUAD environments to include
  --suites SUITES       List of SQUAD suites to include
  --suite-prefixes SUITE_PREFIXES
                        List of prefixes of SQUAD suites to include
  --email-cc EMAIL_CC   Create the report with email cc
  --email-from EMAIL_FROM
                        Create the report with email from
  --email-subject EMAIL_SUBJECT
                        Create the report with this email subject
  --email-to EMAIL_TO   Create the report with email to
  --output OUTPUT       Write the report to this file
  --send-on SEND_ON     Send on failures, regressions or always.
                        example: FAIL:REG, REG default: ALL
  --template TEMPLATE   Create the report with this template
  --config CONFIG       Create the report using this configuration
  --config-report-type CONFIG_REPORT_TYPE
                        Set the report type to use in the local config file
  --perf-report-hook SCRIPT
                        Set the performance script
  --perf-report-hook-args ARGS
                        Set arguments for the performance script
  --unfinished          Create a report even if a build is not finished
  --version             Print out the version
```

## Logging
To enable logging output, set `LOG_LEVEL` in your environment.

The most common levels to use are `INFO` and `DEBUG`.

See [Logging Levels](https://docs.python.org/3/library/logging.html#levels) for more options.

## Contributing
[CONTRIBUTING.md](https://gitlab.com/Linaro/lkft/reports/squad-report/-/blob/master/CONTRIBUTING.md)

## License
[MIT](https://gitlab.com/Linaro/lkft/reports/squad-report/-/blob/master/LICENSE)
