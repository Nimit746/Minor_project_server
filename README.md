# Project Structure

```
├── docs
│   └── personalised_interview_generation.drawio
├── server
│   ├── Agentic_wf
│   │   ├── agents
│   │   │   ├── evaluation
│   │   │   │   ├── nodes
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── prompts
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── states
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── tools
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── utils
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── graph_builder.py
│   │   │   ├── generate_questions
│   │   │   │   ├── nodes
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── cache_lookup.py
│   │   │   │   │   ├── controller.py
│   │   │   │   │   ├── evaluate_answer.py
│   │   │   │   │   ├── finalize_session.py
│   │   │   │   │   ├── generate_question.py
│   │   │   │   │   ├── interrupt_for_answer.py
│   │   │   │   │   ├── llm_judge.py
│   │   │   │   │   └── load_candidate_profile.py
│   │   │   │   ├── prompts
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── question_generation.py
│   │   │   │   ├── states
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── schemas.py
│   │   │   │   ├── tools
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── company_profiler.py
│   │   │   │   │   └── resume_analyzer.py
│   │   │   │   ├── utils
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── router.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── graph_builder.py
│   │   │   ├── research
│   │   │   │   ├── nodes
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── prompts
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── states
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── tools
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── utils
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── graph_builder.py
│   │   │   ├── resume_parse
│   │   │   │   ├── nodes
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── add_metadata.py
│   │   │   │   │   ├── chunk.py
│   │   │   │   │   ├── download_file_node.py
│   │   │   │   │   ├── load_file.py
│   │   │   │   │   └── store.py
│   │   │   │   ├── states
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── file.py
│   │   │   │   ├── utils
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── router.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── graph_builder.py
│   │   │   ├── roadmap
│   │   │   │   ├── nodes
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── prompts
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── states
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── tools
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── utils
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── graph_builder.py
│   │   │   └── __init__.py
│   │   ├── config
│   │   │   ├── RAG
│   │   │   │   ├── chunking.py
│   │   │   │   ├── embeddings.py
│   │   │   │   ├── loader.py
│   │   │   │   ├── retriever.py
│   │   │   │   └── vector_store.py
│   │   │   ├── __init__.py
│   │   │   ├── cloud_settings.py
│   │   │   ├── database.py
│   │   │   ├── llm.py
│   │   │   └── settings.py
│   │   ├── core
│   │   │   ├── __init__.py
│   │   │   └── exceptions.py
│   │   ├── services
│   │   │   ├── cloud
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_cloud_service.py
│   │   │   │   ├── cloud_service_factory.py
│   │   │   │   ├── cloudinary_service.py
│   │   │   │   ├── r2_service.py
│   │   │   │   └── s3_service.py
│   │   │   ├── RAG
│   │   │   │   ├── chunking_service.py
│   │   │   │   ├── embeddings_service.py
│   │   │   │   ├── loader_service.py
│   │   │   │   ├── retriever_service.py
│   │   │   │   └── vector_store_service.py
│   │   │   ├── __init__.py
│   │   │   ├── ingestion_pipeline.py
│   │   │   └── llm_service.py
│   │   ├── tools
│   │   │   ├── __init__.py
│   │   │   └── db_tools.py
│   │   ├── utils
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── app
│   │   ├── config
│   │   ├── core
│   │   │   └── __init__.py
│   │   ├── db
│   │   │   └── __init__.py
│   │   ├── models
│   │   │   └── __init__.py
│   │   ├── routers
│   │   │   └── v1
│   │   │       └── endpoints
│   │   │           └── __init__.py
│   │   ├── schemas
│   │   │   └── __init__.py
│   │   ├── services
│   │   │   └── __init__.py
│   │   ├── utils
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── tests
│   │   ├── agents
│   │   │   └── resume_parse
│   │   │       └── test_download_node.py
│   │   ├── test_imports.py
│   │   └── test_main.py
│   ├── graph.png
│   ├── main.py
│   ├── model.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── test_agent.py
└── README.md
```

## Advancements for this project

- Add a chatbot to the project and give it RAG abilities and image processing using OCR.
