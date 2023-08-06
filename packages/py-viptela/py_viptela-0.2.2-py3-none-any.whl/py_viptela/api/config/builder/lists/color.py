def get(vmanage):
    """
    Get policy lists
    
    Parameters:
            
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/template/policy/list/color"
    response = vmanage.client.apiCall(vmanage.GET, endpoint)
    return response

def create(vmanage, policylist):
    """
    Create policy list
    
    Parameters:
    policylist:	Policy list
    
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/template/policy/list/color"
    response = vmanage.client.apiCall(vmanage.POST, endpoint, policylist)
    return response

def preview(vmanage, policylist):
    """
    Preview a policy list based on the policy list type
    
    Parameters:
    policylist:	Policy list
    
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/template/policy/list/color/preview"
    response = vmanage.client.apiCall(vmanage.POST, endpoint, policylist)
    return response

def previewById(vmanage, id):
    """
    Preview a specific policy list entry based on id provided
    
    Parameters:
    id	 (string):	Policy Id
    
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/template/policy/list/color/preview/{id}"
    response = vmanage.client.apiCall(vmanage.GET, endpoint)
    return response

def getListsById(vmanage, id):
    """
    Get a specific policy list based on the id
    
    Parameters:
    id	 (string):	Policy Id
    
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/template/policy/list/color/{id}"
    response = vmanage.client.apiCall(vmanage.GET, endpoint)
    return response

def edit(vmanage, policylist, id):
    """
    Edit policy list entries for a specific type of policy list
    
    Parameters:
    policylist:	Policy list
	id	 (string):	Policy Id
    
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/template/policy/list/color/{id}"
    response = vmanage.client.apiCall(vmanage.PUT, endpoint, policylist)
    return response

def delete(vmanage, id):
    """
    Delete policy list entry for a specific type of policy list
    
    Parameters:
    id	 (string):	Policy Id
    
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/template/policy/list/color/{id}"
    response = vmanage.client.apiCall(vmanage.DELETE, endpoint)
    return response
