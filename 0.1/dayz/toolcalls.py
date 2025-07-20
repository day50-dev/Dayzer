def get_conversations_from(context, query): 
    """
    get contextual conversations from the user
    """
 

def establish_context():
    """
    might not be toolcalled
    """
 

toolList = [
    {
        "type": "function",
        "function": {
            "name": "get_conversations_from",
            "description": "get contextual conversations from the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "The context of the conversation"
                    },
                    "query": {
                        "type": "string",
                        "description": "The query to search for"
                    }
                },
                "required": ["context", "query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "establish_context",
            "description": "might not be toolcalled",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]