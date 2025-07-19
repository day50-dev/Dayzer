C client
M middleware
S server

User messages, we establish context. If the context is not fully established or can be inferred (we can do this classically), 
then we want to tool-call back down to C. The logic for doing this
could either be classical or llm. 

Essentially:
  .git/config
  .git/HEAD

and MAYBE, but probably not
  ~/.gitconfig

The user should establish their globals at registration
  git config --get user.email is minimal

There are probably 2 levels: anonymous and credentialed. 

We use the 

Looking at the use-cases we'll need something like:

{
  meta:
  history:
}

where history is actually

{
  role:
  data:
  meta:
} 

The realization is only partial meta data is discoverable at any given point.

    Some important things
        date
        user
        tool (header)
