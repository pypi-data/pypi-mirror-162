def createServerInfo(vmanage):
    """
    Get Server info
    
    Parameters:
            
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/server/info"
    response = vmanage.client.apiCall(vmanage.GET, endpoint)
    return response
