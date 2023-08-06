from py_viptela.query_builder import Builder
from py_viptela import HttpMethods

def getVPNInstances(vmanage, deviceId):
    """
    Get VPN instance list from device (Real Time)
    
    Parameters:
    deviceId	 (string):	Device Id
    
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/device/vpn?deviceId={deviceId}"
    response = vmanage.client.apiCall(HttpMethods.GET, endpoint)
    return response
