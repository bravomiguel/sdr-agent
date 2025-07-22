from langgraph_sdk import Auth  
  
auth = Auth()  
  
@auth.authenticate  
async def authenticate(authorization: str | None) -> Auth.types.MinimalUserDict:  
    """Accept any request - fully permissive authentication."""  
    # For development/testing - accept any request  
    return {  
        "identity": "default-user",  
        "is_authenticated": True,  
    }  