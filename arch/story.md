There's a dayzer.pub file in the gitroot that corresponds to the team/person

The next thing is how does someone else pick that up. I can see 3 options:

1. Local mcp - the user installs some local tool calling software that looks and reports

2. Proxy injection - In this model the server is already appending itself to the tool call list and so the pub can be searched for on-demand via some kind of tool-calling proxy with a read_file or
   whatever the next level down is doing.

3. OOB linking - essentially the user does manual context management. This has been an idea I've been trying to find a less confusing way to do. Essentially it's

    $ dayzer add .
    Found dayzer.pub
    Found .git/config
    Adding callable context for $pwd

So assume the user is using the proxy then things like this should work

    "What was the user thinking when they were editing line 410"

   
￼

