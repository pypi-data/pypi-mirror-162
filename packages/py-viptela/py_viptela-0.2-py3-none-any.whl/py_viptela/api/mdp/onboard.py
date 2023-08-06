from py_viptela.query_builder import Builder
from py_viptela import HttpMethods

def onboardMDP(vmanage, onboard):
    """
    Start MDP onboarding operation
    
    Parameters:
    onboard:	Onboard
    
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/mdp/onboard"
    response = vmanage.client.apiCall(HttpMethods.POST, endpoint, onboard)
    return response

def getOnboardStatus(vmanage):
    """
    Get MDP onboarding status
    
    Parameters:
            
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/mdp/onboard/status"
    response = vmanage.client.apiCall(HttpMethods.GET, endpoint)
    return response

def updateOnboardingPayload(vmanage, onboard, nmsId):
    """
    update MDP onboarding document
    
    Parameters:
    onboard:	Onboard
	Parameter Description
    
    Returns
    response    (dict)
    
    
    """
    
    endpoint = f"https://{vmanage.host}:{vmanage.port}/dataservice/mdp/onboard/{nmsId}"
    response = vmanage.client.apiCall(HttpMethods.PUT, endpoint, onboard)
    return response
