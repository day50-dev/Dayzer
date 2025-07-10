def add_to_memory(query):
    # see the memory discussion in the google doc
    # Store across all modes, always
    for f in [store_as_graph, store_as_embedding, store_as_document]:
        f(memory_fragment)

    # Retrieval time = decision point
    if query.intent == "just find something relevant":
        result = retrieve_as_embedding(query)

    elif query.intent == "reason about implications":
        result = ensemble_retrieve(query, fidelity="high")

    else:
        result = retrieve_as_document(query)

