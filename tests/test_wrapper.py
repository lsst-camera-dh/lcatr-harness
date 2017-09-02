from lcatr.harness.et_wrapper import *

# This script can be used for testing wrapper routines without running
# a harnessed job as long as the following are sensibly defined
#   LCATR_LIMS_URL
#   LCATR_RUN_NUMBER
#   LCATR_UNIT_TYPE
#   LCATR_UNIT_ID
#  See test_env.sh for some plausible values

ourRuns = getComponentRuns()

print 'Returned info on ',len(ourRuns), ' runs'
for k in ourRuns:
    print 'Next run: ',k

ourSummary = getRunSummary()

print 'ourSummary: '
print ourSummary


instances = getHardwareInstances('ITL-CCD', hardwareLabels=['SR_Grade:SR_SEN_reserve'])
print 'Calling getHardwareInstances:'
print 'Found ', len(instances), ' instances'
#for i in instances:
#    print i['experimentSN'], i['hardwareLabels']

d = getRunFilepaths()

print '\nCalling getRunFilepaths:'
for  k in d:
    print 'Key: ',k
    for f in d[k]:
        print 'Basename: ', f['basename']

print '\nCalling getFilepathsJH'
d = getFilepathsJH(htype='ITL-CCD', experimentSN='ITL-3800C-092',
                   travelerName='SR-EOT-1', stepName='flat_acq')
for r in d:
    print 'Key: ',r
    for k in d[r]:
        if k != 'steps':
            print 'Key next level: ', k, ' Value: ', d[r][k]
        else:
            print '# steps is: ', len(d[r][k])

print '\nCalling getManualRunResults'
m = getManualRunResults(4618)
for k in m:
    if k != 'steps':
        print 'Key: ', k, ' Value: ', m[k]
print 'Data for steps '
for s in m['steps']: 
    print 'Step ',s
    for i in m['steps'][s]:
        print 'Input pattern: ', i
          

print '\nCalling getManualRunFilepaths'
m = getManualRunFilepaths(4864)
for k in m:
    if k != 'steps':
        print 'Key: ', k, ' Value: ', m[k]
print 'Data for steps '
for s in m['steps']: 
    print 'Step ',s
    for i in m['steps'][s]:
        print 'Input pattern: ', i

print '\nCalling getManualRunSignatures'
m = getManualRunSignatures(5108, activityStatus=['success', 'inProgress', 'paused'])
for k in m:
    if k != 'steps':
        print 'Key: ', k, ' Value: ', m[k]
print 'Data for steps '
for s in m['steps']: 
    print 'Step ',s
    for i in m['steps'][s]:
        print 'Signer request: ', i







