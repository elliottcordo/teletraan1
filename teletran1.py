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
             'Please verify the file name and path.  All config files need to reside in the HAMbot/cfg directory'

# ------------------------------------------------------------------------
#declare application
app = Flask(__name__, static_url_path = "/static", static_folder = "static")
app.debug = True

# ------------------------------------------------------------------------
@app.route('/index')        #http://localhost:5000/index
def index():
     return 'Teletran 1.0'


test_data = ({'job_id':1, 'job_name':'test', 'start_time':datetime.now(), 'percent_complete':100,
              'duration':50, 'current_test_name':'test', 'status':'FAILED', 'url':None},
             {'job_id':2, 'job_name':'test2', 'start_time':datetime.now(), 'percent_complete':50,
              'duration':50, 'current_test_name':'test', 'status':'ERROR', 'url':None},
             {'job_id':3, 'job_name':'test3', 'start_time':datetime.now(), 'percent_complete':50,
              'duration':50, 'current_test_name':'test', 'status':'SUCCESS', 'url':None})

config = 'test'


#get status of jobs -- http://localhost:5000/Theorem/jobs
@app.route('/<string:config>/jobs', endpoint='jobs')
def get_jobs(config):
    try:
        config_path = "{0}/cfg/{1}.cfg".format(sys.path[0], config)
        #First verify config file exists
        if os.path.isfile(config_path):

            #job = test_Module.DqTesting(config_path)
            logo_url = 'http://www.underconsideration.com/brandnew/archives/equinox_logo.png'
            jobs = test_data
            #Populate URL key with address to connect to specific job results
            for my_job in jobs:
                my_job['url'] = '/{0}/{1}/results'.format(config, my_job['job_id'])
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
                           title=config,
                           logo = logo_url,
                           status_path = '/{0}/jobs'.format(config),
                           jobs=jobs)

# ------------------------------------------------------------------------
#logging wrapper:
#log_name = datetime.datetime.now().strftime("hambot-%Y%m%d-%H%M%S.log")
#logging.basicConfig(filename=log_name,level=logging.DEBUG, format='%(asctime)s %(message)s',filmode='w')

def log(message):
    logging.info(message)
    print(message)
#------------------------------------------------------------------------
if __name__ == '__main__':
    app.run()
#Valid Arg1 value will call DW job, optional Arg2 boolean will set debug mode
#need to add command line at some point
    # if len(sys.argv)==1:
    #print "HAMbot.py requires arguments for the testModule and testSet. No Action Taken."
    # sys.exit
    # if len(sys.argv)==4:
    # debug=sys.argv[3]
    # else:
    # debug=False

#get_jobs('stuff')
#job_results('Theorem', 84)
#get_jobs('Theorem')
#run('Theorem', 'Simul_Data_Test')
#run('TheoremDQ', 'Timed Tests1'
#test_notes('TheoremDQ', 125)
#http://localhost:5000/Theorem/126/log
#test_log('Theorem', 126)