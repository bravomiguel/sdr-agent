def extract_interrupt_payload(response):  
    """Extract the actual payload from an interrupt response, handling both Studio UI format (with interrupt ID wrapper) and direct format."""  
    if not isinstance(response, dict):  
        return response  
      
    # Check if this looks like an interrupt ID wrapper  
    if len(response) == 1:  
        key = next(iter(response.keys()))  
          
        # Check if the key looks like an interrupt ID (UUID-like format with hyphens)  
        # Format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (36 chars total)  
        if (len(key) == 36 and   
            key.count('-') == 4 and  
            all(c in '0123456789abcdef-' for c in key.lower())):  
            # Extract the wrapped payload  
            return response[key]  
      
    # If not wrapped, return as-is  
    return response