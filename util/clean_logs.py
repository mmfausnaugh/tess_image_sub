import numpy as np
import glob
import os
import re

logdir=os.environ['LOG_DIR']
logfiles_outputs = np.sort(glob.glob(
    os.path.join(logdir,'*.o*_*')
))

logfiles_errors = np.sort(glob.glob(
    os.path.join(logdir,'*.e*_*')
))

#do the output logs
job_IDs = [ ]
names = []
for logfile in logfiles_outputs:
    match = re.search('\.o(\d*)_', logfile)
    job_IDs.append(int(match.group(1))  )
    match = re.search('logs/(\w*)\.o', logfile)
    names.append(match.group(1))
    
job_IDs = np.array(job_IDs)
names   = np.array(names)

for job_ID in np.unique(job_IDs):
    matches = job_IDs == job_ID

    assert all( names[matches] == names[matches][0] )
    #print(names[matches])
    with open('{}.o{}'.format(names[matches][0], job_ID), 'w' ) as fout:
        for ii in np.where(matches == 1)[0]:
            with open(logfiles_outputs[ii], 'r') as fin:
                fout.write('Contents of {}:  \n'.format(logfiles_outputs[ii]))
                for line in fin:
                    fout.write(line)


                fout.write('\n\n\n')
            os.remove(logfiles_outputs[ii])



#do the error logs
job_IDs = [ ]
names = []
for logfile in logfiles_errors:
    match = re.search('\.e(\d*)_', logfile)
    job_IDs.append( int(match.group(1))  )
    match = re.search('logs/(\w*)\.e', logfile)
    names.append(match.group(1))
    
job_IDs = np.array(job_IDs)
names   = np.array(names)

for job_ID in np.unique(job_IDs):
    matches = job_IDs == job_ID

    assert all( names[matches] == names[matches][0] )
    #print(names[matches])
    with open('{}.e{}'.format(names[matches][0], job_ID), 'w' ) as fout:
        for ii in np.where(matches == 1)[0]:
            with open(logfiles_errors[ii], 'r') as fin:
                fout.write('Contents of {}:  \n'.format(logfiles_errors[ii]))
                for line in fin:
                    fout.write(line)


                fout.write('\n\n\n')
                
            os.remove(logfiles_errors[ii])
