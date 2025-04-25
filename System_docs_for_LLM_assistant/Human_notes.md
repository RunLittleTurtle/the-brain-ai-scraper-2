# Human Notes

## Prompt pour technical overview per module

I need you to create a markdown file that will resume and give an overview for these tow module. The goal for this is to allow anybody to grasp quickly the main objective and how it is configure. What are the main techinal spec of this module. And for an LLM building to udnerstand what is the structure. What is the strucutre. Needs to be 100-200 lines max.`@tool_registry` `@config_secrets`  The file will be called: technical_overview. 



Create a file that goes into each folder. Then make sure that the Moduel index is still relevant and up t0 date.





---

## **LLM Prompt: Generate Module Development Plan**

**Your Task is : Generate Module Development Plan for LLM for the "MODULE X" in Module Index** 

**Core Task:**

Generate a detailed development plan for the new software module: `[New Module Name]`. This plan is the primary specification for *another LLM* that will program the module.

**Analyze Context & Examples:**

1.  **Project Context:** Review the provided `[Project Overview Document Name, e.g., module_index]` to understand the goals and architecture of `[Project Name]`.
2.  **Learn from Examples:** Carefully study the provided Moduel_index and the completed modules plans. Focus on:
    *   The main sections they use.
    *   The *types* of essential technical information they consistently include (like purpose, interfaces, core logic, testing details, guidance for the coder).
    *   The level of detail and use of examples.
    *   **Your goal is to replicate the *spirit* and *utility* of these examples, focusing on clarity and completeness for the coding LLM.**

3.  You need to make sure that this Module plan is threated like a micro service, yes the module will live in the same codebase, but it's developped entirely or the most we can isolated form the rest. The goal is to create module that will be easily maintained, testable, and update bled, independently form the rest of the codebase.

**You need to infer these informations based on the provided documents:**



*   **Core Purpose/Goal:** 
*   **Key Features/Responsibilities:**
*   **Primary Interactions/Dependencies (Internal & External):** 
*   **Key Technologies (if known):** 
*   **Critical Requirements/Constraints:** 
*   **(Optional) Placement/Priority:**

**Required Plan Content (Organize Inspired by Examples):**

Generate the plan as a well-organized Markdown document titled with H1, H2, H3 and bold for the `[Module] [New Module Name]`. Structure the plan using a few **major headings** similar to those observed int he exemple of develpment plan below. Ensure that **within these sections**, you thoroughly cover the following **essential information**:

**I. Core Purpose & Context:**

*   **Description:** What the module does, its significance in `[Project Name]`, and its relationship to other modules.
*   **Main Objective:** The primary goal for the *implementing LLM*.
*   **Dependencies:** Internal modules and external libraries required.
*   **(If applicable) Suggested File Structure:** A logical organization for this module's code.

**II. Technical Design & Interfaces:**

*   **Inputs & Outputs:** Detailed definitions of how the module receives data/commands and what it produces. Must include formats (e.g., API endpoints with JSON schemas/Pydantic, CLI args, message formats) and concrete examples.
*   **Exposed Interface:** Key functions, methods, APIs, or commands provided *by* this module for external use.
*   **Core Logic / Encapsulated Features:** Explanation of the internal algorithms, processes, and key functional components. How does it work?
*   **(If applicable) Data Structures/Models:** Definitions of important internal or external data schemas (beyond basic I/O) with examples.
*   **(If applicable) Storage:** Mention any databases, files, or other persistence mechanisms used.

**III. Development, Testing & Usage:**

*   **Usage Examples:** Concrete examples showing how to interact with the module (e.g., sample API calls, CLI commands, basic code usage). *Crucial for usability.*
*   **Developer Interaction:** Specific guidance on how developers (human or LLM) interact during development/testing (e.g., essential CLI commands, debugging endpoints).
*   **Testing Strategy & Key Tests:** Outline the testing approach and list **specific, critical regression tests** (e.g., `command X with input A yields output B`) needed to verify core functionality.

**IV. Implementation Guidance & Roadmap:**

*   **Notes for Implementing LLM:** *Essential section.* Provide specific guidance, constraints, assumptions, potential pitfalls, edge cases, and implementation hints for the coding LLM.
*   **Task Breakdown / Features to Develop:** An itemized list of implementation tasks/features, logically grouped, with initial statuses (e.g., `[Backlog]`, `[To_Do_Next]`) to guide the work.
*   **(If applicable) Module-Specific Rules:** Any unique business logic, security rules, or performance constraints.
*   **(If applicable) Development Workflow:** Brief notes on the expected development process.

**Key Instructions for the Planning LLM:**

*   **Focus on Essentials:** Prioritize clearly defining the Purpose, Interfaces, Core Logic, Key Tests, and Implementation Notes. Depth here is more important than covering every minor optional point if time/complexity is a constraint.
*   **Adaptability:** Tailor the content and depth appropriately for `[New Module Name]`. If information is missing, state assumptions or mark as TBD.
*   **No Code Implementation:** Do *not* write the actual code. Focus on the plan, specification, and guidance. Minimal, illustrative code snippets for examples are okay.

**Output Format:**

Deliver the plan as a single, well-structured Markdown document. H1, H2, H3.

---

