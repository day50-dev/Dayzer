#!/bin/bash
LITELLM_MASTER_KEY="sk-1234" # Your master key for the proxy server. Can use this to send /chat/completion requests etc
TELLM_SALT_KEY="sk-XXXXXXXX" # Can NOT CHANGE THIS ONCE SET - It is used to encrypt/decrypt credentials stored in DB. If value of 'LITELLM_SALT_KEY' changes your models cannot be retrieved from DB

install() {
    uvx --from=litellm[proxy] litellm-proxy
    uv tool install litellm[proxy]
}

run() {
    litellm --config ./example.yaml
}

run
