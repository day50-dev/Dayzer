#!/bin/sh
KEY=$(head -1 ~/openrouter.key)
HOST="openrouter.ai/api"
MODEL="google/gemini-2.0-flash-exp:free"

check() {
    curl -v $1/v1/chat/completions \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $KEY" \
      -d '{
        "model": "'$MODEL'",
        "messages": [
          {
            "role": "developer",
            "content": "You are a helpful assistant."
          },
          {
            "role": "user",
            "content": "Hello!"
          }
        ],
        "stream": true
      }'
}

#check https://openrouter.ai/api > tmp/oroute
check http://localhost:8000 > tmp/lhost
