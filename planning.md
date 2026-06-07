# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

University of Washington (UW) Computer Science Course & Professor Reviews: Diving into specific teaching styles, exam difficulties, or project workloads at the Allen School.

This knowledge is incredibly valuable because official channel data (like course catalogs or syllabi) only provides generic academic overviews. It completely leaves out subjective student pain points like project hour demands, strictness of proof grading, flipped classroom pacing, or professor accessibility. Having this context centralized helps incoming students manage their course pacing and avoid burnout.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | `docs/cse311_reviews.txt`| CSE 311: Proof grading, structural induction pacing, and note-taking mechanics. | https://www.reddit.com/r/udub/comments/ptn8kq/what_is_cse_311_like/ |
| 2 | `docs/cse332_workload.txt` | CSE 332: Data structures project implementation depth vs theoretical exam preparation. | https://www.reddit.com/r/udub/comments/13vi0ax/cse_332/ |
| 3 | `docs/cse333_systems_tips.txt` | CSE 333: Memory management workloads, C/C++ exercises, and systems prerequisites.| https://www.reddit.com/r/udub/comments/ut3dto/difficulty_of_cse_333/ |
| 4 | `docs/cse351_hardware_transition.txt` | CSE 351: Transition mechanics from Java to low-level C, memory caching, and assembly language. | https://www.reddit.com/r/udub/comments/51gfgr/tips_for_cse_351/ |
| 5 | `docs/cse344_databases.txt`| CSE 344: SQL query complexities, pairing balance guidelines, and workload tracking. | https://www.reddit.com/r/udub/comments/js515p/cse_344_difficulty/ |
| 6 | `docs/prof_kevin_lin_style.txt` | Kevin Lin: Flipped classrooms, exam-heavy rubrics, and strict styling parameters. | https://www.ratemyprofessors.com/professor/2574020 |
| 7 | `docs/prof_mahmood_hameed_style.txt` | Mahmood Hameed: Rigid course structures, thorough conceptual lecturing, and lab variations. | https://www.ratemyprofessors.com/professor/2834847 |
| 8 | `docs/prof_elba_garza_style.txt`| Elba Garza: Course structural differences across intro programming and advanced hardware interface. | https://www.ratemyprofessors.com/professor/2836919 |
| 9 | `docs/applying_to_allen_school_internal.txt` | Applying to the Allen School internally within UW: Prerequisite strategic pathways, introductory series grading rules, and research acquisition. | https://www.reddit.com/r/udub/comments/1tpts6r/applying_to_the_allen_school_as_a_current_uw/ |
| 10 | `docs/cs_courses_must_takes.txt` | CS Courses Must Takes: Industry elective tracking across systems, software engineering, and machine learning. | https://www.reddit.com/r/udub/comments/1s5q27e/cs_course_must_takes/ |



---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 500 chars

**Overlap:** 100 chars

**Reasoning:** Our document corpus consists of student review blocks that have been condensed into high-density informational paragraphs. Each distinct piece of advice (e.g., a specific textbook name, a unique lab format, or grading criteria) spans roughly 2 to 4 sentences. A character-based chunk size of 500 ensures that a full semantic thought or paragraph is contained within a single vector chunk, preventing it from being diluted by neighboring topics. The 100-character overlap prevents critical proper nouns (like "CSE 452" or "LaTeX") or qualitative descriptions from being severed across chunk boundaries.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

**Top-k:** 3 chunks

**Production tradeoff reflection:** If deployed for real users where financial constraints were lifted, we would evaluate moving to a premier model like `text-embedding-3-large` or `Cohere-embed-v3`. While `all-MiniLM-L6-v2` runs perfectly locally with sub-millisecond latency, its maximum context window is restricted to 256 tokens. A production model would scale our context window up to 8,192 tokens, enabling us to safely ingest full threads of historical student reviews in single chunks. It would also dramatically improve accuracy on domain-specific engineering jargon (e.g., distinguishing between terms like "caches" in systems architecture vs. web browser states) and seamlessly catch nuances in unstructured student sentiment.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |


     ## Evaluation Questions

     ### Question 1
     * **Question:** What is the grading rigor like in CSE 311, and what tools do students recommend for taking notes and writing homework?
     * **Expected Answer:** Grading in CSE 311 is extremely strict and nitpicky, particularly for proofs where no steps can be implied. Students recommend using an iPad for handwritten lecture notes due to the heavy use of mathematical symbols, and utilizing LaTeX to format and write homework assignments.

     ### Question 2
     * **Question:** How does the project workload of CSE 333 compare to CSE 351, and what is the typical format of its assignments?
     * **Expected Answer:** CSE 333 requires a significantly higher time commitment and workload than CSE 351. The course format consists of short C/C++ programming exercises due every few days alongside large, multi-week programming labs due roughly every two weeks that build toward an overall system project.

     ### Question 3
     * **Question:** What are the primary grading and lecture characteristics of Professor Kevin Lin's upper-level courses?
     * **Expected Answer:** Professor Kevin Lin uses a highly test-heavy evaluation structure where exams dictate the majority of the final grade despite highly time-consuming projects. He utilizes a non-conventional grading rubric and runs a flipped classroom style where lectures focus on practice exam problems, requiring students to learn core concepts independently before class.

     ### Question 4
     * **Question:** What specific strategy is recommended for an internal UW student looking to secure an undergraduate research position with a computer science professor?
     * **Expected Answer:** Students should avoid generic or cold requests. Instead, they should build a relationship by consistently attending the professor's weekly office hours, actively asking deep questions adjacent to the lecture material, and researching the professor's published papers beforehand. Once rapport is established mid-quarter, they can formally ask to join the lab.

     ### Question 5
     * **Question:** Which advanced elective courses are considered critical for students aiming for a career in cloud-scale software engineering, and why?
     * **Expected Answer:** Distributed Systems (CSE 452) and Operating Systems (CSE 451) are considered the most career-critical electives for systems and backend engineering. They provide deep, foundational competency in low-level execution and cloud-scale architectures, which distinguishes candidates even when modern tools abstract the operating system away.

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Overlapping Professor/Course Associations (Cross-Context Contamination):** Multiple text files cover identical core classes (e.g., `docs/cse351_hardware_transition.txt` and `docs/prof_elba_garza_style.txt` both heavily hit topics concerning CSE 351). A search query regarding Elba Garza might pull general CSE 351 tips that don't mention her, or vice versa. We will mitigate this by ensuring our generation prompt commands the LLM to strictly isolate professor names from general structural tips during retrieval validation.
2. **Context Boundary Severance on Key Proper Nouns:** Because courses are routinely referred to by numbers alone ("311", "332"), an automated character split could sever a course prefix from its number (e.g., leaving "CSE" in chunk A and "311" in chunk B). We will track this by verifying that our 100-character overlap completely preserves alphanumeric tokens without breaking strings apart.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

See in mermaid.md
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

AI Tool: Claude Opus 4.8 (primary), with Gemini 3.5 Flash for quick cross-checks

Inputs: The ## Documents data schema and the ## Chunking Strategy rules from this planning.md file.

Expected Production Output: A complete, production-ready Python script named ingest.py that crawls our docs/ folder, loops through the text files, slices them into chunks using our specified 500-character size and 100-character overlap parameters, and outputs a validation log displaying the total chunk count generated per file.

Verification Plan: Run the script locally via terminal and assert that the output print array matches our files. We will explicitly print out chunks[0] and chunks[1] of docs/cse311_reviews.txt to verify by hand that the text overlaps precisely by 100 characters.

**Milestone 4 — Embedding and retrieval:**
AI Tool: Claude Opus 4.8 (primary), with Gemini 3.5 Flash for quick cross-checks

Inputs: The ## Retrieval Approach spec, the ChromaDB integration guide from our project requirements, and the working chunk arrays from ingest.py.

Expected Production Output: Updates to our architecture script to instantiate a local vector database directory, translate raw text blocks into math arrays using sentence-transformers, store them in a persistent collection, and run a test query function that successfully extracts the top 3 closest chunks matching a query string.

Verification Plan: Issue a terminal search query: "Kevin Lin flipped classroom". Assert that the terminal prints 3 database chunks originating exclusively from docs/prof_kevin_lin_style.txt.

**Milestone 5 — Generation and interface:**
AI Tool: Claude Opus 4.8 (primary), with Gemini 3.5 Flash for quick cross-checks

Inputs: The entire completed planning.md structure, the active database retrieval hooks from Milestone 4, and the Groq API initialization code snippets (`from groq import Groq`, reading `GROQ_API_KEY` from `.env`).

Expected Production Output: A main application execution file (app.py) that handles incoming user string prompts, executes the data retrieval hook, injects the top-k text chunks into a well-structured system context template, and interfaces with the Groq API (`llama-3.3-70b-versatile`) to return a grounded response. The system prompt will hard-enforce grounding — instructing the model to answer using only the retrieved context and to reply "I don't have enough information on that." when the context is insufficient — and source filenames will be appended programmatically to the response rather than left to the model. The app will be served through a Gradio web UI (`gradio>=6.9.0`) exposing a question textbox, an answer field, and a "Retrieved from" sources field.

Verification Plan: Launch the Gradio app with `python app.py` and open http://localhost:7860. Manually run all 5 questions from our ## Evaluation Plan through the web UI, plus one off-topic question our documents don't cover (which should trigger the "not enough information" decline). For each grounded answer we will confirm the cited source filename(s) match the document the answer was actually drawn from, and compare the generated text against our expected "ground truth" criteria.