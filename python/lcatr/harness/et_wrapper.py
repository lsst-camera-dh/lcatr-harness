#!/usr/bin/env python
'''
This module is a wrapper for certain functions provided by eTraveler-clientAPI
It makes use of environment variables established by JH to compute some of the
arguments for those functions
'''

from eTraveler.clientAPI.connection import Connection
import os

class EtWrapperConnectionError(RuntimeError):
    pass

def __make_connection(writer=False, cnfPath=None, debug=False):
    url=os.environ.get('LCATR_LIMS_URL')
    operator=os.environ.get('LCATR_OPERATOR')
    # Need to parse out experiment, db and whether it's prod or dev server
    # Assume defaults to start
    prodServer=True
    exp = 'LSST-CAMERA'
    if 'localhost' in url:
        db = 'Dev'
        if 'ETAPI_DEVSERVER' in os.environ:
            prodServer=False
        if 'ETAPI_DB' in os.environ:
            db = os.environ.get('ETAPI_DB')
            if db == 'Prod':
                raise EtWrapperConnectionError("May not access Prod database with fake eTraveler")
        # look for alternate settings in environment variables
        #    ETAPI_EXPERIMENT -- don't bother for now; not supported by API
        #    ETAPI_DEVSERVER     --     if defined, use dev server
        #    ETAPI_DB            -- if defined and not 'Prod', use it
    else:
        if 'dev' in url: prodServer=False
        if 'srs.slac.stanford' in url: prodServer=False
        cmps = url.split('/')
        if 'exp' in cmps:
            expIx = cmps.index('exp') + 1
            exp = cmps[expIx]
        if 'Results' in cmps:
            db = cmps[cmps.index('Results') - 1]
        else:
            if 'eTraveler' in cmps:
                db = cmps[cmps.index('eTraveler') + 1]
            else:
                msg = "Inappropriate value for LCATR_LIMS_URL: " + url 
                raise EtWrapperConnectionError(msg)
    
    if (writer) and (cnfPath != None):
        return Connection(operator, db, prodServer, cnfPath=cnfPath)
    else:
        return Connection(operator, db, prodServer, debug=debug)
def __ourRun():
    return os.environ.get('LCATR_RUN_NUMBER')


def setHardwareStatus(newStatus, reason='From harnessed job',cnfPath=None):
    '''
    Set hardware status of component job is concerned with.
    newStatus:  String value which must correspond to legitimate hardware
                status
    returns: String value. 'Success' if operation succeeded; else error message
    '''
    if (cnfPath != None):
        conn = __make_connection(cnfPath=cnfPath)
    else:
        conn = __make_connection()
    expSN=os.environ.get('LCATR_UNIT_ID')
    ht=os.environ.get('LCATR_UNIT_TYPE')
    actId = os.environ.get('LCATR_JOB_ID')
    msg = conn.setHardwareStatus(experimentSN=expSN, htype=ht,
                                 status=newStatus, 
                                 reason=reason, activityId=actId)
    return msg

def adjustHardwareLabel(label, add=True, reason='from harnessed job',
                        cnfPath=None):
    '''
    Add a label to or remove from component job is concerned with.
    label:   String value of label to be added or removed.  Must correspond
             to label known to eTraveler
    add:     Defaults to True.  Set to False to remove a label
    returns: String value. 'Success' if operation succeeded, else error message
    '''
    if (cnfPath != None):
        conn = __make_connection(cnfPath=cnfPath)
    else:
        conn = __make_connection()
    experimentSN=os.environ.get('LCATR_UNIT_ID')
    htype=os.environ.get('LCATR_UNIT_TYPE')
    if add: adding='true'
    else: adding='false'
    actId = os.environ.get('LCATR_JOB_ID')
    msg = conn.adjustHardwareLabel(experimentSN=experimentSN, htype=htype,
                                   label=label, adding=adding,
                                   reason=reason, activityId=actId)
    return msg
                                   
def getHardwareHierarchy(noBatched='true'):
    '''
    Return array of dicts describing relationships of all subcomponents
    of current component.  If noBatched is true (the default) relationships
    involving batched components will be ignored.
    '''
    conn = __make_connection()
    experimentSN=os.environ.get('LCATR_UNIT_ID')
    htype=os.environ.get('LCATR_UNIT_TYPE')
    a = conn.getHardwareHierarchy(experimentSN=experimentSN, htype=htype,
                                  noBatched=noBatched)
    return a

def getContainingHardware():
    '''
    Return array of dicts describing relationships of all ancestors
    of current component.  
    '''
    conn = __make_connection()
    expSN=os.environ.get('LCATR_UNIT_ID')
    htype=os.environ.get('LCATR_UNIT_TYPE')
    a = conn.getContainingHardware(experimentSN=expSN, 
                                   htype=htype)
    return a

def getManufacturerId():
    '''
    Return manufacturer id string for current component
    '''
    conn = __make_connection()
    expSN=os.environ.get('LCATR_UNIT_ID')
    htype=os.environ.get('LCATR_UNIT_TYPE')
    mId = conn.getManufacturerId(experimentSN=expSN, htype=htype)

    return mId

def setManufacturerId(newId, reason="Set from et_wrapper",cnfPath=None):
    '''
    Set manufacturer id for current component to supplied value.
    Fails (throws exception) if component already had a 
    non-blank manufacturer id.
    '''
    if (cnfPath != None):
        conn = __make_connection(cnfPath=cnfPath)
    else:
        conn = __make_connection()
    expSN=os.environ.get('LCATR_UNIT_ID')
    htype=os.environ.get('LCATR_UNIT_TYPE')
    conn.setManufacturerId(experimentSN=expSN, htype=htype,
                           manufacturerId=newId,
                           reason=reason)

def getActivity(activityId):
    '''
    Get information about specified activity, including begin and end times
    Returns a dict with keys 'begin', 'end', 'stepName', 'status', 'activityId'
    May throw eTraveler.clientAPI.connection.ETClientAPIException,
    ETClientAPINoDataException
    '''
    conn = __make_connection()
    return conn.getActivity(activityId=activityId)

def getRunActivities(run):
    '''
    Get information about activities in specified run.
    Returns a list of dicts, ordered by activity id.
    Comments for getActivity apply
    '''
    conn = __make_connection()
    if (run == None) or (run == "@"):
        return conn.getRunActivities(run=__ourRun())
    return conn.getRunActivities(run=run)

def getRunSummary(run=None):
    '''
    Get information about specified run.
    Returns a dict.
    '''
    conn = __make_connection()
    if (run == None) or (run == "@"):
        return conn.getRunSummary(run=__ourRun())
    return conn.getRunSummary(run=run)

def getComponentRuns(htype=None, experimentSN=None):
    
    conn = __make_connection()
    if experimentSN == None:
        return conn.getComponentRuns(htype=os.environ.get('LCATR_UNIT_TYPE'),
                                     experimentSN=os.environ.get('LCATR_UNIT_ID'))
    if htype==None:
        raise ValueError("et_wrapper.getComponentRuns: Missing htype argument")
    return conn.getComponentRuns(htype=htype, experimentSN=experimentSN)

def getHardwareInstances(htype, experimentSN=None, hardwareLabels=None):

    conn = __make_connection()
    rqst = {"htype": htype}
    if experimentSN != None: rqst["experimentSN"] = experimentSN
    if hardwareLabels != None: rqst['hardwareLabels'] = hardwareLabels;
    return conn.getHardwareInstances(**rqst)

def getRunResults(run, **kwds):
    '''
    Get summary information from harnessed jobs in specified run. Several
    optional keyword arguments are available for filtering.  They may
    be used in any combination
    stepName - restrict output to this step
    schemaName - restrict output to this schema
    itemFilter - key-value pair, e.g. ("amp", 3).  For schemas containing
                 the key, only return data where value matches specified.
                 If schema does not contain the key, include its data as is
    '''
    if (run == None) or (run == "@"):
        rqst = {"run" : __ourRun()}
    else:
        rqst = {"run" : run}
    for k in kwds:
        rqst[k] = kwds[k]
    conn = __make_connection()
    return conn.getRunResults(**rqst)

def getResultsJH(**kwds):
    '''
    Get summary information for components from a particular step within
    a particular traveler type.
    Required keywords are
    htype  - hardware type name
    travelerName
    stepName
    If no optional arguments are included, data will be returned for all
    components of the specified type for which the step has been successfully
    executed. 

    Optional keyword arguments are available for filtering.  They may
    be used in any combination except that model will be ignored if
    experimentSN is included
    schemaName - restrict output to this schema
    itemFilter - key-value pair, e.g. ("amp", 3).  For schemas containing
                 the key, only return data where value matches specified.
                 If schema does not contain the key, include its data as is
    model      - restrict output just to components of this model
    experimentSN - return output only for the single specified component
    hardwareLabels - set of strings.  Only return information for components
    with at least one label in the set
    '''
    rqst = {}
    for k in kwds:
        rqst[k] = kwds[k]
    conn = __make_connection()
    return conn.getResultsJH(**rqst)

def getFilepathsJH(**kwds):
    '''
    Get filepath information for components from a particular step within
    a particular traveler type.
    Required keywords are
    htype  - hardware type name
    travelerName
    stepName
    If no optional arguments are included, data will be returned for all
    components of the specified type for which the step has been successfully
    executed. 

    Optional keyword arguments are available for filtering. 
    model will be ignored if experimentSN is included
    model      - restrict output just to components of this model
    experimentSN - return output only for the single specified component
    hardwareLabels - set of strings.  Only return information for components
    with at least one label in the set
    '''
    rqst = {}
    for k in kwds:
        rqst[k] = kwds[k]
    conn = __make_connection()
    return conn.getFilepathsJH(**rqst)

def getRunFilepaths(run=None, **kwds):
    '''
    Get filepath information from harnessed jobs in specified run.
    stepName optional keyword argument can be used for filter.
    If run is None or "@" return info for current run
    stepName - restrict output to this step
    itemFilter - key-value pair, e.g. ("amp", 3).  For schemas containing
                 the key, only return data where value matches specified.
                 If schema does not contain the key, include its data as is
    '''
    if (run == None) or (run == "@"):
        rqst = {"run" : __ourRun()}
    else:
        rqst = {"run" : run}
    for k in kwds:
        rqst[k] = kwds[k]
    conn = __make_connection()
    return conn.getRunFilepaths(**rqst)

def getManualRunResults(run=None, **kwds):
    '''
    Get operator inputs (int, float or string) in specified run.
    stepName optional keyword argument can be used for filter. 
    If run is None or "@" return info for current run
    stepName - restrict output to this step
    itemFilter - key-value pair, e.g. ("amp", 3).  For schemas containing
                 the key, only return data where value matches specified.
                 If schema does not contain the key, include its data as is
    '''
    if (run == None) or (run == "@"):
        rqst = {"run" : __ourRun()}
    else:
        rqst = {"run" : run}
    for k in kwds:
        rqst[k] = kwds[k]
    conn = __make_connection()
    return conn.getManualRunResults(**rqst)

def getManualRunFilepaths(run=None, **kwds):
    '''
    Get operator inputs (filepaths) in specified run.
    stepName optional keyword argument can be used for filter. 
    If run is None or "@" return info for current run
    stepName - restrict output to this step
    itemFilter - key-value pair, e.g. ("amp", 3).  For schemas containing
                 the key, only return data where value matches specified.
                 If schema does not contain the key, include its data as is
    '''
    if (run == None) or (run == "@"):
        rqst = {"run" : __ourRun()}
    else:
        rqst = {"run" : run}
    for k in kwds:
        rqst[k] = kwds[k]
    conn = __make_connection()
    return conn.getManualRunFilepaths(**rqst)

def getManualRunSignatures(run=None, **kwds):
    '''
    Get operator inputs (signatures) in specified run.
    stepName optional keyword argument can be used for filter. 
    If run is None or "@" return info for current run
    stepName - restrict output to this step
    itemFilter - key-value pair, e.g. ("amp", 3).  For schemas containing
                 the key, only return data where value matches specified.
                 If schema does not contain the key, include its data as is
    '''
    if (run == None) or (run == "@"):
        rqst = {"run" : __ourRun()}
    else:
        rqst = {"run" : run}
    for k in kwds:
        rqst[k] = kwds[k]
    conn = __make_connection(debug=True)
    return conn.getManualRunSignatures(**rqst)

def getManualResultsStep(**kwds):
    '''
    Get operator-entered information for components from a particular step 
    within a particular traveler type.
    Required keywords are
    htype  - hardware type name
    travelerName
    stepName
    If no optional arguments are included, data will be returned for all
    components of the specified type for which the step has been successfully
    executed. 

    Optional keyword arguments are available for filtering. model
    will be ignored if experimentSN is included
    model      - restrict output just to components of this model
    experimentSN - return output only for the single specified component
    hardwareLabels - set of strings.  Only return information for components
    with at least one label in the set
    '''
    rqst = {}
    for k in kwds:
        rqst[k] = kwds[k]
    conn = __make_connection()
    return conn.getManualResultsStep(**rqst)

def getManualFilepathsStep(**kwds):
    '''
    Get operator-entered filepaths for components from a particular step 
    within a particular traveler type.
    Required keywords are
    htype  - hardware type name
    travelerName
    stepName
    If no optional arguments are included, data will be returned for all
    components of the specified type for which the step has been successfully
    executed. 

    Optional keyword arguments are available for filtering. model
    will be ignored if experimentSN is included
    model      - restrict output just to components of this model
    experimentSN - return output only for the single specified component
    hardwareLabels - set of strings.  Only return information for components
    with at least one label in the set
    '''
    rqst = {}
    for k in kwds:
        rqst[k] = kwds[k]
    conn = __make_connection()
    return conn.getManualFilepathsStep(**rqst)

def getManualSignaturesStep(**kwds):
    '''
    Get operator-entered filepaths for components from a particular step 
    within a particular traveler type.
    Required keywords are
    htype  - hardware type name
    travelerName
    stepName
    If no optional arguments are included, data will be returned for all
    components of the specified type for which the step has been successfully
    executed. 

    Optional keyword arguments are available for filtering. model
    will be ignored if experimentSN is included
    model      - restrict output just to components of this model
    experimentSN - return output only for the single specified component
    hardwareLabels - set of strings.  Only return information for components
    with at least one label in the set
    '''
    rqst = {}
    for k in kwds:
        rqst[k] = kwds[k]
    conn = __make_connection()
    return conn.getManualSignaturesStep(**rqst)
