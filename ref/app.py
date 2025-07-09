import uuid, os, redis, json, html
import base64, requests
import asyncio
import random
from redis.asyncio import Redis as ioredis
from litellm import completion
import litellm
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request

app = FastAPI()
ws_redis = ioredis.from_url("redis://localhost")
rds = redis.Redis(host="localhost", port=6379, db=0)

_topicList = "convos"
_model = "openrouter/google/gemini-2.0-flash-exp:free"
#_model = "openrouter/deepseek/deepseek-chat-v3-0324:free"

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

        #litellm._turn_on_debug()
        #message = await asyncio.to_thread(
        response = completion(
            api_key=api_key,
            model=_model,
            messages=body["messages"],
            stream=stream
        )
        if not stream:
            return JSONResponse(response.json())
        else:
            def generate():
                for chunk in response:  # Iterate over the streaming response
                    yield f"data:{chunk.model_dump_json()}\n\n"

            return StreamingResponse(generate(), media_type="text/event-stream")

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

@app.post("/chat")
async def chat(data: dict):
    # If we don't have a UID, then we initialize and have the first injected assistant.
    isFirst = not data.get("uid")
    uid = data.get("uid") or initialize_session(data["context"], _model)
    nextLine = None

    if data.get("text"):
        text = data["text"]
        if text[0] == "/":
            parts = text[1:].split(" ")
            cmd = parts[0]
            if cmd == "delete":
                summarize(uid, "")
                rds.hdel(_topicList, uid)
            elif cmd == "update":
                newname = " ".join(parts[1:]).strip()
                if newname:
                    summarize(uid, newname)
                else:
                    summarize(uid)

            return JSONResponse({"res": True, "data": [], "uid": uid})

        # We should also have the first user-generated text at this point
        history = add_to_session(uid, {"role": "user", "content": data["text"]})
        if isFirst:
            summary = generate_summary(data["text"])
            summarize(uid, summary)

        openrouter_model = _model
        openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

        # So this is apparently stateless.
        # We just unroll the entire conversation up to this point.
        message = await asyncio.to_thread(
            completion,
            api_key=openrouter_api_key,
            model=openrouter_model,
            tool_choice="auto",
            tools=_tools,
            messages=history,
        )
        """
        import pdb
        pdb.set_trace()
        print(vars(message.choices))
        """

        tool_calls = message.choices[0].message.tool_calls

        if tool_calls:
            print("\nLength of tool calls", len(tool_calls))
            response = []
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = {
                "generate_image": generate_image,
            }  # only one function in this example, but you can have multiple

            # Step 4: send the info for each function call and function response to the model
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(
                    prompt=function_args.get("prompt")
                )
                response = {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
        else:
            response = message.choices[0].message.content

        # We need to save that response as an assistant
        nextLine = {"role": "assistant", "content": response}

    # We support a blank add_to_session which just uses the mechanics
    # to retrieve. This is what's done on page-load for a session reload
    return JSONResponse(
        {"res": True, "data": add_to_session(uid, nextLine), "uid": uid}
    )




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
