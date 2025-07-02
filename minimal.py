import os
import requests
from litellm import completion
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request

app = FastAPI()
_model = "openrouter/google/gemini-2.0-flash-exp:free"

@app.post("/v1/chat/completions")
async def chat_completions_proxy(request: Request):
    body = await request.json()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    stream = body.get('stream') or False

    try:
        response = completion(
            api_key=api_key,
            model=_model,
            messages=body["messages"],
            stream=stream
        )

        if not stream:
            return JSONResponse(response.json())
        
        def generate():
            for chunk in response:  # Iterate over the streaming response
                yield f"data:{chunk.model_dump_json()}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        return JSONResponse(
            {"error": f"OpenAI API error: {str(e)}"},
            status_code=500
        )

uvicorn.run(app, host="0.0.0.0", port=8000)
