from langgraph.graph import StateGraph, START, END

async def build_ingestion_graph():
    gr = StateGraph()
    gr.add_node()

    gr.add_conditional_edges()
    gr.add_edge()

    workflow = gr.compile()
    return workflow