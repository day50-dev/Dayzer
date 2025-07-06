_tools =  [{
    "type": "function",
    "function": {
        "name": "generate_image",
        "description": "Generate a relevant image given a prompt",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The thing to generate. e.g, a lovely spring day",
                },
            },
        },
    },
}] 

def history_process(api_key, message):
    pass

def get_api_key(caller_key, model):
    pass

def add_tools(body):
    toolList = body.get('tools') or []
    toolList += _tools
    return toolList
