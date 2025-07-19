This is a list of the use-cases & features

self memory:
    user: remember when we talked

    - (about concept)
    - (specific date)
    - (some object such as code)

    agent: has a few ways to query and then presents the user with options

someone else:
    What was the person who wrote this thinking?
    Why didn't the person do this?


So it's historical holistically.
We need to come up with function names
Essentially all the params are (context, query)

Context is maybe a dictionary?
{
    repo: (can be injected),
    files: [
        {
            name:
            lines:
        }
    ]
}

The problem with the files approach of course is things move around and get refactored.

Maybe this won't matter - it all depends on how the querying is done.

Eventually there can be something like purpose included but for now let's ignore the problem

We should probably be more specific on a call-by-call basis.
