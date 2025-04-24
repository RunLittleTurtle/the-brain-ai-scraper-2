# User‑Centric Flows – **The Brain** (Local & Hosted)

>  Each flow is a sequence of Agile‐style **user‑stories**.
>  Column **“CLI vs LLM”** clarifies who triggers the step.
>  Modules list ties back to `MODULE_INDEX.md` for traceability.

------

## **Flow 1 – One‑Shot Iteration (Local CLI)**

| #    | User‑Story (Agile)                                           | CLI vs LLM                                         | Core Modules / Features                                      |
| ---- | ------------------------------------------------------------ | -------------------------------------------------- | ------------------------------------------------------------ |
| 1    | **As a solo developer**, I paste a LinkedIn URL into `brain run`, **so that** I automaticaly receive a JSON of job posts. | *CLI command*: `brain run <url>`                   | cli/run, api_gateway, pipeline_builder, build_engine, executor (local), progress_tracker |
| 2    | **As the developer**, I watch a live progress bar and logs, **so that** I see anti‑bot issues early. | *LLM streams*, CLI auto‑updates                    | progress_tracker (SSE)                                       |
| 3    | **As the developer**, I mark the output **Bad** and add a comment "salary missing", **so that** The Brain auto‑tunes the pipeline. | *CLI command*: `brain score <run_id> bad`          | cli/score, evaluator → pipeline_builder/modify_spec, build_engine, executor |
| 4    | **As the developer**, I rerun automatically and get a **Good** JSON, **so that** the run is stored for reuse. | *LLM action*(auto‑retry), then *CLI score*: `good` | evaluator, knowledge_base                                    |

------

## **Flow 2 – Package Suggestion & Hot‑Swap (Local CLI)**

| #    | User‑Story (Agile)                                           | CLI vs LLM                                                   | Core Modules / Features                                      |
| ---- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 1    | **As a developer**, when I run my URL for the first time, I receive 3 package suggestions from The Brain, **so that** I can choose one to execute. | *LLM suggestion* → CLI list                                  | pipeline_builder (`suggest_packages`), knowledge_base, cli/suggest |
| 2    | **As the developer**, I execute suggestion #2 and hot-swap **Playwright** for **undetected-chromedriver**, **so that** I test stealth mode. | *CLI command*: `brain run --package 2 --swap playwright=ucd` | cli options, pipeline_builder/modify_spec, build_engine      |
| 3    | **As the developer**, I mark the run **Bad**, **so that** The Brain retries automatically with alternative proxies and updates its package ranking. | *CLI command*: `brain score <run_id> bad`                    | evaluator, pipeline_builder auto-loop, knowledge_base feedback |

------

## **Flow 3 – Promote to Hosted & Unified Logs**

| #    | User‑Story (Agile)                                           | CLI vs LLM                             | Core Modules / Features                       |
| ---- | ------------------------------------------------------------ | -------------------------------------- | --------------------------------------------- |
| 1    | **As the same developer**, I push the working spec to hosted with `--hosted`, **so that** my laptop can sleep. | *CLI flag*                             | cli/run --hosted, api_gateway, executor (K8s) |
| 2    | **As the developer**, I view combined logs (local + hosted) in my terminal, **so that** I track the job anywhere. | *CLI command*: `brain status <run_id>` | progress_tracker dual endpoint                |
| 3    | **As the developer**, I score the hosted output **Good**, **so that** KB stores the spec & user review for future ranking. | *CLI score good*                       | evaluator, knowledge_base (store review)      |

------

## **Flow 4 – Daily Multi‑Source Crawl & Merge (Hosted)**

| #    | User‑Story (Agile)                                           | CLI vs LLM                                         | Core Modules / Features                                      |
| ---- | ------------------------------------------------------------ | -------------------------------------------------- | ------------------------------------------------------------ |
| 1    | **As a remote dev**, I schedule daily LinkedIn **and**Indeed crawls tagged `jobs`, **so that** I wake up to fresh listings. | *CLI commands*: two `brain schedule … --tag jobs`  | cli/schedule, api_gateway, pipeline_builder, build_engine, executor (K8s) |
| 2    | **As the dev**, I merge the last 24 h of `jobs` runs into one JSON, **so that** downstream tools get a single feed. | *CLI command*: `brain merge tag=jobs --window 24h` | aggregator/merge, object storage                             |
| 3    | **As the dev**, I score the merged output **Good**, **so that**all contributing pipelines receive positive feedback. | *CLI score good*                                   | evaluator (propagate), knowledge_base                        |

------

## **Flow 5 – Auto‑Repair & Connector Alert (Hosted)**

| #    | User‑Story (Agile)                                           | CLI vs LLM                             | Core Modules / Features                                      |
| ---- | ------------------------------------------------------------ | -------------------------------------- | ------------------------------------------------------------ |
| 1    | **As a hosted developer**, I rely on a weekly Marketplace crawler; if coverage <90 %, I want The Brain to auto‑repair up to 3 tries, **so that**I still get usable data. | *LLM auto‑workflow*(no CLI)            | executor (K8s), evaluator (<90 trigger), pipeline_builder auto_fix loop |
| 2    | **As that developer**, I only want a Make webhook when the final run is **Good** or the auto‑repair exhausted, **so that** I avoid noise. | *Connector event*                      | connectors/Make, progress_tracker gating                     |
| 3    | **As that developer**, I review the spec diff with `brain spec‑diff`, **so that** I understand what changed. | *CLI command*: `brain spec-diff <run>` | cli/spec-diff, knowledge_base versions                       |

------

## **Flow 6 – Add New Tool & A/B Report**

| #    | User‑Story (Agile)                                           | CLI vs LLM                                                   | Core Modules / Features                              |
| ---- | ------------------------------------------------------------ | ------------------------------------------------------------ | ---------------------------------------------------- |
| 1    | **As an OSS contributor**, I register `marketplace_scraper`via one command, **so that** it becomes available. | *CLI*: `brain tools add marketplace_scraper`                 | installer, tool_registry                             |
| 2    | **As the contributor**, I ask The Brain to run an A/B test between the new tool and Playwright, **so that** I compare field completeness. | *CLI*: `brain experiment <url> --tools marketplace_scraper,playwright` | pipeline_builder (two specs), build_engine, executor |
| 3    | **As the contributor**, I receive an evaluator report comparing coverage, **so that** I choose the winner. | *LLM auto‑report to CLI*                                     | evaluator comparative, aggregator                    |

------

> **How users score builds**: `brain score <run_id> good|bad [comment]` → routed to `evaluator`, stored in `RunMeta.review`, indexed in `knowledge_base` for ranking.
>
> **Package suggestion & swap**: `brain suggest`, `--package`, `--swap toolA=toolB` let users override the LLM while still recording decisions in KB.

This single Markdown document now aggregates **all 6 flows** with explicit CLI vs LLM roles and user scoring/review integration.