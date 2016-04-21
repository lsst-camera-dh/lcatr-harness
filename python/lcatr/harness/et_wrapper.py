#!/usr/bin/env python
'''
This module is a wrapper for certain functions provided by eTraveler-clientAPI
It makes use of environment variables established by JH to compute some of the
arguments for those functions
'''

from eTraveler.clientAPI.connection import Connection
import os

def __make_connection():
    url=os.environ.get('LCATR_LIMSURL')
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
    db = cmps[cmps.index('Results') - 1]
    return Connection(operator, db, prodServer)


def setHardwareStatus(newStatus):
    '''
    Set hardware status of component job is concerned with.
    newStatus:  String value which must correspond to legitimate hardware
                status
    returns: String value. 'Success' if operation succeeded; else error message
    '''
    conn = __make_connection()
    experimentSN=os.environ.get('LCATR_UNIT_ID')
    htype=os.environ.get('LCATR_UNIT_TYPE')
    msg = conn.setHardwareStatus(experimentSN=experimentSN, htype=htype,
                                 attributeName=newStatus)
    return msg

def adjustHardwareLabel(label, add=True):
    '''
    Add a label to or remove from component job is concerned with.
    label:   String value of label to be added or removed.  Must correspond
             to label known to eTraveler
    add:     Defaults to True.  Set to False to remove a label
    returns: String value. 'Success' if operation succeeded, else error message
    '''
    conn = __make_connection()
    experimentSN=os.environ.get('LCATR_UNIT_ID')
    htype=os.environ.get('LCATR_UNIT_TYPE')
    if add: adding='true'
    else: adding='false'
    msg = conn.adjustHardwareLabel(experimentSN=experimentSN, htype=htype,
                                  attributeName=label, adding=adding)
    return msg
                                   

