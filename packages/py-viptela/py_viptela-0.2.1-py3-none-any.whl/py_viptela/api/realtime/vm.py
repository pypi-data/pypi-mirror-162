from py_viptela.query_builder import Builder
from py_viptela import HttpMethods

def getVbranchNics(vmanage, deviceId):
    """
    Get vbranch vm lifecycle state (NIC)
    
    Parameters:
    deviceId	 (string):	Device IP
    
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/device/vm/nics?deviceId={deviceId}"
    response = vmanage.client.apiCall(HttpMethods.GET, endpoint)
    return response
def getCloudDockNics(vmanage, userGroup):
    """
    Get CloudDock vm lifecycle state
    
    Parameters:
    userGroup	 (string):	userGroup Name
    
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/device/vm/notifications?userGroup={userGroup}"
    response = vmanage.client.apiCall(HttpMethods.GET, endpoint)
    return response
def getVbranch(vmanage, deviceId):
    """
    Get vbranch vm lifecycle state
    
    Parameters:
    deviceId	 (string):	Device IP
    
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/device/vm/oper/state?deviceId={deviceId}"
    response = vmanage.client.apiCall(HttpMethods.GET, endpoint)
    return response
def getState(vmanage, deviceId):
    """
    Get vm lifecycle state
    
    Parameters:
    deviceId	 (string):	Device IP
    
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/device/vm/state?deviceId={deviceId}"
    response = vmanage.client.apiCall(HttpMethods.GET, endpoint)
    return response
