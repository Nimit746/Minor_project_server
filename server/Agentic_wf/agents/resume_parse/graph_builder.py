from langgraph.graph import StateGraph, START, END
from Agentic_wf.agents.resume_parse.states import FileState
from Agentic_wf.agents.resume_parse.utils import check_already_ingested, skip_processing
from Agentic_wf.agents.resume_parse.nodes import chunk_documents, load_file, download_file, store_in_vector_db, add_metadata

def build_ingestion_graph():
    gr = StateGraph(FileState)
    gr.add_node('load_file', load_file)
    gr.add_node('download_file', download_file)
    gr.add_node('chunk_documents', chunk_documents)
    gr.add_node('add_metadata', add_metadata)
    gr.add_node('store_in_vector_db', store_in_vector_db)
    gr.add_node("skip_processing", skip_processing)

    gr.add_conditional_edges(
        START,
        check_already_ingested,
        {
            "download_file": "download_file",
            "skip_processing": "skip_processing"
        }
    )
    gr.add_edge('download_file', 'load_file')
    gr.add_edge('load_file', 'chunk_documents') 
    gr.add_edge('chunk_documents', 'add_metadata')
    gr.add_edge('add_metadata', 'store_in_vector_db')
    gr.add_edge('store_in_vector_db', END)
    gr.add_edge('skip_processing', END)

    workflow = gr.compile()
    return workflow