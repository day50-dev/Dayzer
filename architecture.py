# This is all based on the minimal.py
import os
import uvicorn
from litellm import completion
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import Request
from . import Dayzer

app = FastAPI()

def completion_caller(body):
    api_key = # get it from the header
    model = body['model']

    body['messages'] = Dayzer.history_process(api_key, body['messages'])
    user_api_key = Dayzer.get_api_key(caller_key=api_key, model=model)
    tools = Dayzer.add_tools(body)

    response = completion(
        api_key=user_api_key,
        model=model,
        messages=body["messages"],
        tools,
        stream=body.get('stream') or False
    )
    return response

@app.post("/v1/chat/completions")
async def chat_completions_proxy(request: Request):
    body = await request.json()
    api_key = os.environ.get("OPENROUTER_API_KEY")

    try:
        response = completion_caller(body)

        if not stream:
            return JSONResponse(response.json())
        
        def generate():
            for chunk in response: 
                yield f"data:{chunk.model_dump_json()}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        return JSONResponse(
            {"error": f"OpenAI API error: {str(e)}"},
            status_code=500
        )

uvicorn.run(app, host="0.0.0.0", port=8000)
