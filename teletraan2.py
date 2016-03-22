from ConfigParser import ConfigParser as Conf
import os
import sys
import logging
import traceback
import argparse
from  datetime import datetime
import yaml
import pymssql
import operator
from flask import Flask, render_template, flash, redirect, request, url_for

# ------------------------------------------------------------------------
os.chdir(os.path.dirname(sys.argv[0]))

#define err messages
# ------------------------------------------------------------------------
err_config = 'The Config File: \'{0}\' is not recognized by python.\n\n'\
             'Please verify the file name and path.  All config files need to reside in the /cfg directory'

# ------------------------------------------------------------------------
#declare application
app = Flask(__name__, static_url_path = "/static", static_folder = "static")
app.debug = False


job_state = []

# ------------------------------------------------------------------------
@app.route('/index')        #http://localhost:5000/index
def index():
     return 'Teletraan 1.0'

logo_url = '/static/images/equinox.png'

@app.route('/<string:config>/jobs', endpoint='jobs')
def get_jobs(config):
    try:
        config_path = "{0}/cfg/{1}.yaml".format(sys.path[0], config)
        # First verify config file exists
        if os.path.isfile(config_path):
            jobs = GetTestResult().run_tests(config)
            # if sort field then sort by it, else based on name
            try:
                jobs.sort(key=operator.itemgetter('sort'))
                # print 'sorted'
            except:
                jobs.sort()
                # print "no sort"
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
                           title = config.title(),
                           asof = 'Last Updated: ' + datetime.now().strftime("%-I:%M %p"),
                           logo = logo_url,
                           status_path = '/{0}/jobs'.format(config),
                           jobs=jobs)

def parse_checklist(config):
    """
    reads yaml file into python object
    :return: checklist
    """
    config_path = "{0}/cfg/{1}.yaml".format(sys.path[0], config)
    with open(config_path, 'r') as checklist_yaml:
        check_list = yaml.load(checklist_yaml)
    # print check_list
    return check_list


class GetTestResult(object):
    def __init__(self):
        c = Conf()
        c.read('teletraan1.cfg')
        server = c.get('life', 'server')
        database = c.get('life', 'database')
        user = c.get('life', 'user')
        pwd = c.get('life', 'pwd')
        self.TestDBConn = pymssql.connect(server, user, pwd, database)

    def exec_tests(self, config):
        checklist = parse_checklist(config)
        cursor = self.TestDBConn.cursor(as_dict=True)
        for f in checklist:
            check = checklist[f]
            type = check['type']
            cursor.execute(check['sql'])
            row = cursor.fetchone()
            if type == 'latency':
                test = calc_latency_tests(row, check)
            elif type == 'daily':
                test = calc_daily_tests(row, check)
            else:
                print 'invalid test yo!'
                continue
            job_state.append(test)
        return job_state

    def close_connection(self):
        self.TestDBConn.close()

    def run_tests(self, config):
        result = self.exec_tests(config)
        self.close_connection()
        return result


def calc_latency_tests(result, check):
    max_latency = check['latency_min']
    latency = (datetime.now() - result['last_end_time']).seconds/60
    status = result['status']
    if latency >= max_latency:
        result['alert_level'] = 'FAILURE'
        result['status_message'] = result['status_message'] + 'w/ latency issue'
    elif status == 1:
        result['alert_level'] = 'FAILURE'
    elif latency >= max_latency*.8:
        result['alert_level'] = 'WARNING'
    else:
        result['alert_level'] = 'SUCCESS'
    result['latency'] = latency
    result['label'] = check['label']
    result['sort'] = check['sort']
    # print result
    return result


def calc_daily_tests(result, check):
    sched_end_time = datetime.combine(datetime.today(), datetime.strptime(check['end_time'], "%H:%M").time())
    actual_end_time = result['last_end_time']
    status = result['status']
    status_message = result['status_message']
    latency =  (sched_end_time - datetime.now()).seconds/60
    if status == 1:
        result['alert_level'] = 'FAILURE'
    elif status_message == 'success':
        result['alert_level'] = 'SUCCESS'
        latency = 0
    elif status_message == 'running' and latency >0:
        result['alert_level'] = 'WARNING'
        result['status_message'] = 'running, expected by ' + check['end_time']
    elif status_message == 'running' and latency  < 0 :
        result['alert_level'] = 'FAILURE'
        result['status_message'] = 'late running, expected by ' + check['end_time']
    else:
        result['alert_level'] = 'INFO'
    result['label'] = check['label']
    result['sort'] = check['sort']
    result['sched_end_time'] = sched_end_time
    result['latency'] = latency
    # print result
    return result


# ------------------------------------------------------------------------
#logging wrapper:

def log(message):
    logging.info(message)
    print(message)
# ------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = False)
