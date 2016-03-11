from ConfigParser import ConfigParser as Conf
import os
import sys
import logging
import traceback
import argparse
from  datetime import datetime
import yaml
import pymssql
from flask import Flask, render_template, flash, redirect


#define err messages
# ------------------------------------------------------------------------
err_config = 'The Config File: \'{0}\' is not recognized by python.\n\n'\
             'Please verify the file name and path.  All config files need to reside in the /cfg directory'

# ------------------------------------------------------------------------
#declare application
app = Flask(__name__, static_url_path = "/static", static_folder = "static")
app.debug = True

# ------------------------------------------------------------------------
@app.route('/index')        #http://localhost:5000/index
def index():
     return 'Teletraan 1.0'


# test_data = ({'job_name':'test1', 'last_start_time':datetime.now(), 'last_end_time':datetime.now(),
#               'status':'failure', 'status_message':'your job failed bro!', 'alert_level':'FAILURE'},
#              {'job_name':'test2', 'last_start_time':datetime.now(), 'last_end_time':datetime.now(),
#               'status':'warning', 'status_message':'maybe we will be ok', 'alert_level':'WARNING'},
#              {'job_name':'test3', 'last_start_time':datetime.now(), 'last_end_time':datetime.now(),
#               'status':'success', 'status_message':'smooth sailing yo!', 'alert_level':'SUCCESS'})

#config = 'intraday'
logo_url = '/static/images/equinox.png'

#get status of jobs -- http://localhost:5000/Theorem/jobs
@app.route('/<string:config>/jobs', endpoint='jobs')
def get_jobs(config):
    try:
        config_path = "{0}/cfg/{1}.yaml".format(sys.path[0], config)
        #First verify config file exists
        if os.path.isfile(config_path):
            jobs = GetTestResult().run_tests()
        else:
            err_msg = err_config.format(config_path)
            return err_msg

    except Exception, err:
        err_msg = traceback.format_exc().splitlines()
        return render_template("general_error.html",
               title=config,
               logo = logo_url,
               status_path = '/{0}/jobs'.format(config),
               err_msg = err_msg)

    return render_template("jobs.html",
                           title= config + ': Job Status',
                           logo = logo_url,
                           status_path = '/{0}/jobs'.format(config),
                           jobs=jobs)

def parse_checklist():
    """
    reads yaml file into python object
    :return: checklist
    """
    config_path = "{0}/cfg/{1}.yaml".format(sys.path[0], 'intraday')
    with open(config_path, 'r') as checklist_yaml:
        check_list = yaml.load(checklist_yaml)
    return check_list


class GetTestResult:
    def __init__(self):
        c = Conf()
        c.read('teletraan1.cfg')
        self.server = c.get('life', 'server')
        self.database = c.get('life', 'database')
        self.user = c.get('life', 'user')
        self.pwd = c.get('life', 'pwd')
        self.set_db_connection()
    def set_db_connection(self):
        self.TestDBConn = pymssql.connect(self.server, self.user, self.pwd, self.database)
    def exec_tests(self):
        result = []
        checklist = parse_checklist()
        cursor = self.TestDBConn.cursor(as_dict=True)
        for f in checklist:
            check = checklist[f]
            type = check['type']
            cursor.execute(check['sql'])
            row = cursor.fetchone()
            if type == 'intraday':
                test = calc_intraday_tests(row, check)
            else:
                print 'invalid test yo!'
                continue
            result.append(test)
        return result
    def close_connection(self):
        self.TestDBConn.close()
    def run_tests(self):
        result = self.exec_tests()
        self.close_connection()
        return result


def calc_intraday_tests(result, check):
    max_latency = check['latency_min']
    latency =  (datetime.now() - result['last_end_time']).seconds/60
    result['latency'] = latency
    result['label'] = check['label']
    status = result['status']
    if latency >= max_latency:
        result['alert_level'] = 'FAILURE'
        result['status_message'] = 'latency issue'
    elif status == 1:
        result['alert_level'] = 'FAILURE'
    elif latency >= max_latency*.8:
        result['alert_level'] = 'WARNING'
    else:
        result['alert_level'] = 'SUCCESS'
    print result
    return result

# ------------------------------------------------------------------------
#logging wrapper:

def log(message):
    logging.info(message)
    print(message)
#------------------------------------------------------------------------
if __name__ == '__main__':
    app.run()
