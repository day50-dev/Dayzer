import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import json
import os

from litellm import completion
import litellm

app = FastAPI()

async def make_openai_request(request: Request, endpoint: str):
    body = await request.json()

    api_key = os.environ.get("OPENROUTER_API_KEY")

    try:
        if not _model:
            return JSONResponse(
                {"error": "Model not specified in request body"},
                status_code=400
            )

        stream = body.get('stream') or False

        if not stream:
            response = completion(
                api_key=api_key,
                model=_model,
                messages=body["messages"],
                stream=False
            )
            return JSONResponse(response.json())  # Use the working non-streaming code
        else:
            queue = asyncio.Queue()

            async def stream_to_queue():
                try:
                    response = completion(
                        api_key=api_key,
                        model=_model,
                        messages=body["messages"],
                        stream=True
                    )
                    for chunk in response:
                        await queue.put(chunk)  # Put chunks into the queue
                finally:
                    await queue.put(None)  # Signal the end of the stream

            asyncio.create_task(stream_to_queue()) # Start streaming in the background

            async def generate():
                while True:
                    chunk = await queue.get()
                    if chunk is None:
                        break  # End of stream
                    yield chunk  # Yield chunks to the client.  The object yield must be string, bytes or buffer

            return StreamingResponse(generate(), media_type="application/json")

    except Exception as e:
        return JSONResponse(
            {"error": f"OpenAI API error: {str(e)}"},
            status_code=500
        )

@app.post("/v1/completions")
async def completions_proxy(request: Request):
    """OpenAI Completion endpoint proxy"""
    return await make_openai_request(request, "completions")

@app.post("/v1/chat/completions")
async def chat_completions_proxy(request: Request):
    """OpenAI Chat Completion endpoint proxy"""
    return await make_openai_request(request, "chat/completions")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
