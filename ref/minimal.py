import os
import uvicorn
from litellm import completion
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import Request

app = FastAPI()

@app.post("/v1/chat/completions")
async def chat_completions_proxy(request: Request):
    body = await request.json()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    stream = body.get('stream') or False

    try:
        response = completion(
            api_key=api_key,
            model="openrouter/google/gemini-2.0-flash-exp:free",
            messages=body["messages"],
            stream=stream
        )

        if not stream:
            return JSONResponse(response.json())
        
        def generate():
            for chunk in response: 
                print(chunk.model_dump_json())
                yield f"data:{chunk.model_dump_json()}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        return JSONResponse(
            {"error": f"OpenAI API error: {str(e)}"},
            status_code=500
        )

uvicorn.run(app, host="0.0.0.0", port=8000)
