#!/bin/bash
cd integrations
dl() {
    for i in voideditor/void All-Hands-AI/OpenHands olimorris/codecompanion.nvim cline/cline RooCodeInc/Roo-Code Kilo-Org/kilocode Aider-AI/aider plandex-ai/plandex block/goose; do
        dir=$(basename $i)
        if [[ ! -d $dir ]]; then 
            git clone --depth=1 https://github.com/$i
        fi
    done
}

check() {
    [[ -d ../out ]] || mkdir ../out
    fdfind -e ts -e tsx -e go -e rs -e py -e js | grep -v test | while read i; do
        stub=${i//\//_}
        echo "... $i"
        if [[ ! -e ../out/$stub ]]; then
            cat "$i" | llm "Tell me if there's any url or api endpoints that this file accesses ... give me all potential candidates and if possible their line number" > ../out/$stub
        fi

    done
}
dl
