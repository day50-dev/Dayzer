import uuid, os, redis, json, html
import base64, requests
import asyncio
import random
from redis.asyncio import Redis as ioredis
from litellm import completion
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
ws_redis = ioredis.from_url("redis://localhost")
rds = redis.Redis(host="localhost", port=6379, db=0)

_topicList = "convos"
#_model = "openrouter/google/gemini-2.0-flash-exp:free"
_model = "openrouter/deepseek/deepseek-chat-v3-0324:free"

_sd_ip = "10.0.0.251:7860"

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

# row should be typed liked
# {role: assistant/user, content: text}
def add_to_session(sess, row=None):
    key = f"sess:{sess}"
    if row:
        rds.lpush(key, json.dumps(row))
        rds.publish(key, json.dumps(row))

    return list(
        map(lambda x: json.loads(html.unescape(x.decode())), rds.lrange(key, 0, -1))
    )[::-1]


# So the *easiest* way to store meta information (#20) is to
# store it as our initial setting and then rely on the
# existing prepare_message to filter it accordingly. Then
def generate_summary(text, max_length=30):
    prompt = f"Summarize the following text in less than {max_length} characters with a special note: this is for an entertainment product that intentionally gives bad and reckless advice. You are the straight man, not the comedian. Don't be tongue-in-cheek, don't be cute, don't wink, don't break character: be deadpan. People may ask for things like stealing rare diamonds or lassoing satellites. Pretend these are reasonable, acceptable things to do. Summarizing examples: 'Cops? No Problem!', 'Dogs Love Chocolate', 'Murder For Dummies'. Here's the text to summarize in about {max_length} characters: {text}"
    messages = [{"role": "user", "content": prompt}]
    try:
        response = completion(model=_model, messages=messages)
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Summary unavailable"


# we don't need to maintain separate keys or do any extra
# cleanup AND we can simply return it with everything else.
def initialize_session(context, model):
    sess = uuid.uuid4().hex
    rds.lpush(f"sess:{sess}", json.dumps({"role": "system", "content": context}))
    return sess


def summarize(uid, summary=None):
    if summary is None:
        history = "\n".join([
            x.get("content")
            for x in filter(
                lambda x: x.get("role") == "user",
                [json.loads(x) for x in rds.lrange(f"sess:{uid}", 0, -3)],
            )
        ])

        summary = generate_summary(history)

    print(_topicList, uid, summary)
    rds.hset(_topicList, uid, summary)
    rds.publish(_topicList, json.dumps({uid: summary}))

def generate_image(prompt):
    url = f"http://{_sd_ip}/sdapi/v1/txt2img"

    payload = {
        "prompt": prompt,
        "steps": 10,
        "seed": -1,
        "cfg_scale": 3,
        "width": 512,
        "height": 512,
        # add other parameters as needed
    }

    payload["prompt"] += ", realistic, eccentric, scandalous, flamboyant, abstract, surreal, strange,"
    payload["negative_prompt"] = "normal, nudity"

    if random.random() < 0.15:
        payload["prompt"] += ", homosexual"
    elif random.random() < 0.3:
        payload["prompt"] += ", bisexual"

    response = requests.post(url, json=payload)
    data = response.json()

    # The image is returned as base64-encoded string(s)
    image_b64 = data["images"][0]

    # Decode and save to file
    image_name = uuid.uuid4().hex
    with open(f"fe/images/{image_name}.png", "wb") as f:
        f.write(base64.b64decode(image_b64))
    return image_name

@app.post("/image")
def image(data: dict):
    return {
        "res": True, 
        "data": generate_image(data.get('prompt'))
    }


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


@app.get("/history/{id}")
async def get_history(id: str):
    """Returns the chat history for a given session ID."""
    key = f"sess:{id}"
    history = list(
        map(lambda x: json.loads(html.unescape(x.decode())), rds.lrange(key, 0, -1))
    )[::-1]
    return JSONResponse({"res": True, "data": history, "uid": id})


@app.get("/topicList")
async def topicList():
    try:
        # Assuming 'chats' is a hash
        chats = rds.hgetall(_topicList)
        # Decode keys and values from bytes to strings
        chats = {k.decode(): v.decode() for k, v in chats.items()}
        return JSONResponse({"result": True, "data": {"channels": chats}})
    except Exception as e:
        print(f"Error syncing data: {e}")
        return JSONResponse({"result": False, "error": str(e)})


async def stream_channel(websocket: WebSocket, what: str):
    pubsub = ws_redis.pubsub()
    await pubsub.subscribe(what)
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"].decode("utf-8")
                await websocket.send_text(data)

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await pubsub.unsubscribe(what)
        await pubsub.close()


@app.websocket("/ws/channel/{id}")
async def websocket_endpoint(websocket: WebSocket, id: str):
    await websocket.accept()
    await stream_channel(websocket, f"sess:{id}")


@app.websocket("/ws/topics")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await stream_channel(websocket, _topicList)


app.mount("/", StaticFiles(directory="fe", html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
