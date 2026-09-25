# Project Structure

```
├── docs
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
│   │   │   │   │   ├── controller.py
│   │   │   │   │   ├── evaluate_answer.py
│   │   │   │   │   ├── finalize_session.py
│   │   │   │   │   ├── generate_question.py
│   │   │   │   │   ├── interrupt_for_answer.py
│   │   │   │   │   └── load_candidate_profile.py
│   │   │   │   ├── prompts
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── question_generation_prompt.py
│   │   │   │   │   ├── rag_question_generation_prompt.py
│   │   │   │   │   └── resume_analyzer_prompt.py
│   │   │   │   ├── states
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── candidate_profile.py
│   │   │   │   │   ├── question.py
│   │   │   │   │   ├── resume_analysis.py
│   │   │   │   │   └── session_state.py
│   │   │   │   ├── tools
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── company_profiler.py
│   │   │   │   │   └── resume_analyzer.py
│   │   │   │   ├── utils
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── bump_difficulty.py
│   │   │   │   │   ├── cache_lookup.py
│   │   │   │   │   ├── calculate_detailed_metrics.py
│   │   │   │   │   ├── clean_llm_json_response.py
│   │   │   │   │   ├── docx_extractor.py
│   │   │   │   │   ├── file_downloader.py
│   │   │   │   │   ├── generate_batch_questions.py
│   │   │   │   │   ├── get_available_topics_for_session.py
│   │   │   │   │   ├── get_cache_key.py
│   │   │   │   │   ├── get_next_question_type.py
│   │   │   │   │   ├── get_safe_batch_size.py
│   │   │   │   │   ├── groq_judge.py
│   │   │   │   │   ├── pdf_extractor.py
│   │   │   │   │   ├── pick_next_topic.py
│   │   │   │   │   ├── recompute_weak_topics.py
│   │   │   │   │   ├── resume_text_extractor.py
│   │   │   │   │   ├── retrieve_relevant_chunks.py
│   │   │   │   │   ├── router.py
│   │   │   │   │   ├── run_sandbox_tests.py
│   │   │   │   │   └── skill_extraction.py
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
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── analyze_topics.py
│   │   │   │   │   ├── compile_roadmap.py
│   │   │   │   │   ├── create_sections.py
│   │   │   │   │   ├── generate_sections.py
│   │   │   │   │   └── get_candidate_data.py
│   │   │   │   ├── prompts
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── section_creation.py
│   │   │   │   │   ├── section_enrichment.py
│   │   │   │   │   └── topic_analysis.py
│   │   │   │   ├── states
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── roadmap.py
│   │   │   │   ├── tools
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── roadmap_search.py
│   │   │   │   ├── utils
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── json_parser.py
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
│   │   │   ├── db_tools.py
│   │   │   └── web_search.py
│   │   ├── utils
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── app
│   │   ├── config
│   │   │   └── __init__.py
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
│   │   ├── e2e
│   │   │   └── test_interview_session.py
│   │   ├── fixtures
│   │   │   ├── data
│   │   │   │   ├── candidate.json
│   │   │   │   ├── questions.json
│   │   │   │   └── roadmap.json
│   │   │   ├── responses
│   │   │   │   └── llm_responses.json
│   │   │   └── resumes
│   │   ├── integration
│   │   │   ├── agents
│   │   │   │   └── test_generate_questions_workflow.py
│   │   │   ├── cloud
│   │   │   ├── database
│   │   │   └── rag
│   │   ├── unit
│   │   │   ├── agents
│   │   │   │   ├── evaluation
│   │   │   │   ├── generate_questions
│   │   │   │   │   ├── test_controller.py
│   │   │   │   │   ├── test_evaluate_answer.py
│   │   │   │   │   ├── test_finalize_session.py
│   │   │   │   │   ├── test_generate_question.py
│   │   │   │   │   ├── test_graph_builder.py
│   │   │   │   │   ├── test_load_candidate_profile.py
│   │   │   │   │   └── test_utils.py
│   │   │   │   ├── research
│   │   │   │   ├── resume_parse
│   │   │   │   │   └── test_graph_builder.py
│   │   │   │   ├── roadmap
│   │   │   │   │   └── test_graph_builder.py
│   │   │   │   └── __init__.py
│   │   │   ├── config
│   │   │   ├── core
│   │   │   ├── services
│   │   │   │   ├── cloud
│   │   │   │   └── rag
│   │   │   ├── tools
│   │   │   └── utils
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_imports.py
│   │   └── test_main.py
│   ├── pyproject.toml
│   ├── test_agent.py
│   ├── test_question_generator_agent.py
│   ├── test_resume_parse_agent.py
│   ├── test_roadmap_agent.py
│   └── test_roadmap_agent1.py
└── README.md
```


## Advancements for this project

- Add a chatbot to the project and give it RAG abilities and image processing using OCR.
