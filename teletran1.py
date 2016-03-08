import ConfigParser
import os
import sys
import logging
import traceback
import argparse
from  datetime import datetime
#import run_multi
#from app import app
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
     return 'Teletran 1.0'


test_data = ({'job_id':1, 'job_name':'test', 'start_time':datetime.now(), 'duration':50,'status':'FAILURE'},
             {'job_id':2, 'job_name':'test2', 'start_time':datetime.now(),'duration':50, 'status':'WARNING'},
             {'job_id':4, 'job_name':'test4', 'start_time':datetime.now(),'duration':50, 'status':'RUNNING'},
             {'job_id':3, 'job_name':'test3', 'start_time':datetime.now(),'duration':50, 'status':'SUCCESS'},)

config = 'DayEnd'
logo_url = '/static/images/equinox.png'

#get status of jobs -- http://localhost:5000/Theorem/jobs
@app.route('/<string:config>/jobs', endpoint='jobs')
def get_jobs(config):
    try:
        config_path = "{0}/cfg/{1}.cfg".format(sys.path[0], config)
        #First verify config file exists
        if os.path.isfile(config_path):
            jobs = test_data
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

# ------------------------------------------------------------------------
#logging wrapper:

def log(message):
    logging.info(message)
    print(message)
#------------------------------------------------------------------------
if __name__ == '__main__':
    app.run()
