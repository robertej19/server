"""

This module provides functions to distribute
jobs to htcondor.

"""

from __future__ import print_function

import argparse
import os
import sqlite3
import sys
import time
from subprocess import PIPE, Popen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))
                + '/../../utils')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))
                + '/../submission_files')
import htcondor_submit
import update_tables
import utils

def farm_submission_manager(args, usub_id, file_extension,
                            scard, params, db_conn, sql):

  timestamp = utils.gettime()
  if scard.farm_name == "OSG":
    utils.printer("Passing to htcondor_submit")
    htcondor_submit_new.htcondor_submit(args,scard,usub_id,file_extension,params,
                                    db_conn, sql)
  else:
    raise ValueError('Unable to submit for {}'.format(
      scard.farm_name
    ))
