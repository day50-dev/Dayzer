This comes from iface, we are talking about the schema here.

Stupid obvious things
    users
    projects
    conversations
    ideas
    code

This might be N by N meaning
users have (many) projects & projects have (many) users 
users have (many) conversations & conversations have (many) users
...

So Are we looking at {type, id, meta} and a graph? ugh ... that's nasty.

Let's do this in the dumbest way possible: sqlite!

We have just two tables:
    objects
    relationships

    objects are
        id, type, meta

    relationships are
        id[1] id[2]

That's probably the dumbest way.
    Does it create technical debt?
        Only if you stick with it!
    Is it more complicated to implement?
        Only if you stick with it!
        
The problem is I usually don't ever get around to the rewrite - maybe ORM it?
