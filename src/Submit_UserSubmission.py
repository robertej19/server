#****************************************************************
"""
# This file will query the command line to see what UserSubmissionID it should use,
# or if no arguement is given on the CL, the most recent UserSubmissionID will be used
# This UserSubmissionID is used to identify the proper scard and gcards, and then submission
# files corresponding to each gcard are generated and stored in the database, as
# well as written out to a file with a unique name. This latter part will be passed
# to the server side in the near future.
"""
#****************************************************************
from __future__ import print_function
import os, sqlite3, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../../utils')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../submission_files')
import farm_submission_manager, script_factory, submission_script_manager
import utils, fs, scard_helper, lund_helper, get_args

def count_user_submission_id(user_sub_id):
    """Select and count instances of the UserSubmissionID and return a count."""
    
    query = """
    SELECT COUNT(UserSubmissionID) FROM UserSubmissions
        WHERE UserSubmissionID = {0}; 
    """.format(user_sub_id)
    
    count = utils.db_grab(query)

    # The database call returns an array with a tuple inside of it 
    # so we need the first element of each.
    return int(count[0][0])


def Submit_UserSubmission(args):

    if args.lite is not None: 
        print('Server received --lite={}'.format(args.lite))

        # This actually doesn't work, most likely 
        # subsequent imports of fs overwrite this 
        # variable. 
        if os.path.exists(args.lite):
            fs.SQLite_DB_Path = args.lite 
            fs.use_mysql = False 
        else:
            print('SQLite database not found at {}'.format(args.lite))

    if args.UserSubmissionID != 'none':
        if count_user_submission_id(args.UserSubmissionID) > 0:
            submission_script_manager.process_jobs(args, args.UserSubmissionID)
        else:
            print("The selected UserSubmission (UserSubmissionID = {0}) does not exist, exiting".format(args.UserSubmissionID))
            exit()

            # UserSubmissionID is not specified (normal running operation).
            # Here we will select all UserSubmissionIDs corresponding to UserSubmissions that have not yet been simulated, and push
            # Then through the simulation.
    else:
        """
        # There are three options for values in the run_status field in the Submissions table:
        # "Not Submitted", "Submission scripts generated" ,and "Submitted to __",
        # Consider the following cases:
        # 1.) When a user submits a job on the client side, the newly created entry has value "Not Sumbitted"
        # 2.) If the server side code runs without the -s flag, submission scripts will be generated in the DB,
        #     but the jobs will NOT be pushed to HTCondor/Slurm,
        #     and the run_status value will be updated to "Submission scripts generated"
        # 3.) If the server side code runs with the -s flag, ALL jobs that do NOT have the value "Submitted to __"
        #     will have submission scripts generated, and the jobs will be passed to HTCondor/Slurm,
        #     and the value of run_status for all submitted UserSubmissions will update to "Submitted to __"
        # Case (2) will just create submission scripts for UserSubmissions created in status (1)
        # Case (3) will create submission scripts and submit jobs for all UserSubmissions in status (1) and (2)
        """
        if args.submit: # Here, we will grab ALL UserSubmissions that have NOT been simulated
            strn = "SELECT UserSubmissionID FROM FarmSubmissions WHERE run_status NOT LIKE '{0}';".format("Submitted to%")
            UserSubmissions_to_submit = utils.db_grab(strn)
            if len(UserSubmissions_to_submit) == 0:
                print("There are no UserSubmissions which have not yet been submitted to a farm")
            else: # Here,if the -s flag was not used, we will just generate submission scripts from UserSubmissions that have not had any generated yet
                strn = "SELECT UserSubmissionID FROM FarmSubmissions WHERE run_status = '{0}';".format("Not Submitted")
                UserSubmissions_to_submit = utils.db_grab(strn)
                if len(UserSubmissions_to_submit) == 0:
                    print("There are no UserSubmissions which do not yet have submission scripts generated")
                    
            # From the above we have our (non-empty) UserSubmission of jobs to submit. Now we can pass it through process_jobs
            for UserSubmission in UserSubmissions_to_submit:
                UserSubmissionID = UserSubmission[0] #UserSubmissionID is the first element of the tuple
                utils.printer("Generating scripts for UserSubmission with UserSubmissionID = {0}".format(str(UserSubmissionID)))
                submission_script_manager.process_jobs(args, UserSubmissionID)


if __name__ == "__main__":
    args = get_args.get_args()
    Submit_UserSubmission(args)
