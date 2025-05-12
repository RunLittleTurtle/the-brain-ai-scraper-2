```kanban
  Backlog
    id4[intent_inference]@{status: 'Backlog', summary: "Transform raw user input into structured IntentSpec JSON."}
    id5[progress_tracker]@{status: 'Backlog', summary: "Publish/subscribe run status & logs with progress indicators."}
    id6[api_gateway]@{status: 'Backlog', summary: "Single REST/MCP FastAPI entrypoint with SSE events."}
    id7[pipeline_builder]@{status: 'Backlog', summary: "Dynamically build PipelineSpec JSON from IntentSpec."}
    id8[executor]@{status: 'Backlog', summary: "Execute pipelines and return scraped results."}
    id9[evaluator]@{status: 'Backlog', summary: "Analyze results, clean outputs, and suggest fixes."}
    id10[knowledge_base]@{status: 'Backlog', summary: "Store past runs for learning and reuse."}
    id11[aggregator]@{status: 'Backlog', summary: "Merge multiple JSON runs into a consolidated output."}
  To_Do
  LLM_In_Progress
    id2[config_secrets]@{status: 'LLM_In_Progress', summary: "Centralized secrets management via local .env loader."}
    id3[cli]@{status: 'LLM_In_Progress', summary: "Thin CLI wrapper for user interaction & testing."}
  LLM_testing
  LLM_test_copmplete
  Human_Review
  Done
    id1[tool_registry]@{status: 'Done', summary: "Plug-and-play catalogue of scraping tools with metadata."}
```



