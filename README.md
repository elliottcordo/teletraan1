# Teletraan1

![robopager](https://github.com/elliottcordo/teletran1/blob/master/docs/teletran.png)

_(Super Computer from Original Transformers Series)_

This project will provide very simple, dependable dashboarding of critical process such as day end and intraday processes.. 


## Overview

Teletraan supports having multiple dashboards/views hosted within the same app.  The way that this works is as follows:

* you create a yaml in the cfg folder with the tests that you want to appear on a given dashboard. For example if you want an intraday dashboard you would create an Intraday.yaml
* when you point your browser you put the yaml name in the path and wallah, your dashboard will render the test results.  In this example http://127.0.0.1:5000/Intraday/jobs
* You can have as many yaml's as you want

## Anatomy of the Yaml
```
Intraday Contracts:
  type: intraday
  label: Intraday Contracts
  sql: "dbo.DW_DQ_Infa_Teletran_Watch 'wf_contracts'"
  latency_min: 20
Intraday EDW:
  type: intraday
  label: Intraday EDW
  sql: "dbo.DW_DQ_Infa_Teletran_Watch 'wf_dw_load_intraday'"
  latency_min: 20
```
Right now we only have one type: intraday, but we will quickly expand to daily, and general data quality alerts (which can be mixed and matched in the same dashboard)

* You specificy the label you want to see in the dashboard
* specify the sql statement which represents the intraday test.  The SQL statement can be a stored proc or a query.  The results must conform to the data model illustrated in the next section.
* specify the latency threshold we would start raising alerts, note that this is the threshold for critical failure, we will raise a warning at 80% of this threshold


### Test Data Model
As stated any SQL can be run, but it must return the following fields:

* name (string): name of job
* last_start_time (datetime): last time the job started
* last_end_time (datetime): last time the job ended
* status (integer): 1 for failure, 0 for OK
* status_message (string): any messages you want to show in the dashboard in addition to success or failure


