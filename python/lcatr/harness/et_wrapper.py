#!/usr/bin/env python
'''
This module is a wrapper for certain functions provided by eTraveler-clientAPI
It makes use of environment variables established by JH to compute some of the
arguments for those functions
'''

from eTraveler.clientAPI.connection import Connection
import os

def __make_connection():
    url=os.environ.get('LCATR_LIMS_URL')
    operator=os.environ.get('LCATR_OPERATOR')
    # Need to parse out experiment, db and whether it's prod or dev server
    # Assume defaults to start
    prodServer=True
    exp = 'LSST-CAMERA'
    if '8180' in url: prodServer=False
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
            return None
    
    return Connection(operator, db, prodServer)


def setHardwareStatus(newStatus, reason='From harnessed job'):
    '''
    Set hardware status of component job is concerned with.
    newStatus:  String value which must correspond to legitimate hardware
                status
    returns: String value. 'Success' if operation succeeded; else error message
    '''
    conn = __make_connection()
    if conn == None: return 'Unable to connect to eTraveler server'
    expSN=os.environ.get('LCATR_UNIT_ID')
    ht=os.environ.get('LCATR_UNIT_TYPE')
    actId = os.environ.get('LCATR_JOB_ID')
    msg = conn.setHardwareStatus(experimentSN=expSN, htype=ht,
                                 status=newStatus, 
                                 reason=reason, activityId=actId)
    return msg

def adjustHardwareLabel(label, add=True, reason='from harnessed job'):
    '''
    Add a label to or remove from component job is concerned with.
    label:   String value of label to be added or removed.  Must correspond
             to label known to eTraveler
    add:     Defaults to True.  Set to False to remove a label
    returns: String value. 'Success' if operation succeeded, else error message
    '''
    conn = __make_connection()
    if conn == None: return 'Unable to connect to eTraveler server'
    experimentSN=os.environ.get('LCATR_UNIT_ID')
    htype=os.environ.get('LCATR_UNIT_TYPE')
    if add: adding='true'
    else: adding='false'
    actId = os.environ.get('LCATR_JOB_ID')
    msg = conn.adjustHardwareLabel(experimentSN=experimentSN, htype=htype,
                                   label=label, adding=adding,
                                   reason=reason, activityId=actId)
    return msg
                                   

