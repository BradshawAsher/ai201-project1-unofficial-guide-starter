# The Unofficial Guide — Project 1

A retrieval-augmented question-answering system over collected student reviews of
University of Washington Allen School CS courses and professors.

**Stack:** Python · `sentence-transformers` (all-MiniLM-L6-v2) · ChromaDB · Groq
(`llama-3.3-70b-versatile`) · Gradio

**Run it:**
```bash
python ingest.py          # inspect chunking
python vector_store.py    # build the ChromaDB index
python app.py             # launch the Gradio UI at http://localhost:7860
python evaluate.py        # run all 5 eval questions + off-topic control
```

---

## Domain

Student reviews of University of Washington (UW) Allen School computer science
courses and professors — specific teaching styles, exam difficulty, project
workloads, and grading rigor.

This knowledge is valuable because official channels (course catalogs, syllabi)
only provide generic academic overviews. They leave out the subjective student
pain points that actually shape a quarter: project hour demands, strictness of
proof grading, flipped-classroom pacing, and professor accessibility.
Centralizing this context helps incoming students pace their course load and
avoid burnout — information that is otherwise scattered across Reddit threads and
RateMyProfessors pages and hard to search coherently.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | `documents/cse311_reviews.txt` | Reddit thread (r/udub) | https://www.reddit.com/r/udub/comments/ptn8kq/what_is_cse_311_like/ |
| 2 | `documents/cse332_workload.txt` | Reddit thread (r/udub) | https://www.reddit.com/r/udub/comments/13vi0ax/cse_332/ |
| 3 | `documents/cse333_system_tips.txt` | Reddit thread (r/udub) | https://www.reddit.com/r/udub/comments/ut3dto/difficulty_of_cse_333/ |
| 4 | `documents/cse351_hardware_transition.txt` | Reddit thread (r/udub) | https://www.reddit.com/r/udub/comments/51gfgr/tips_for_cse_351/ |
| 5 | `documents/cse344_databases.txt` | Reddit thread (r/udub) | https://www.reddit.com/r/udub/comments/js515p/cse_344_difficulty/ |
| 6 | `documents/prof_kevin_lin_style.txt` | RateMyProfessors | https://www.ratemyprofessors.com/professor/2574020 |
| 7 | `documents/prof_mahmood_hameed_style.txt` | RateMyProfessors | https://www.ratemyprofessors.com/professor/2834847 |
| 8 | `documents/prof_elba_garza_style.txt` | RateMyProfessors | https://www.ratemyprofessors.com/professor/2836919 |
| 9 | `documents/applying_to_allen_school_internal.txt` | Reddit thread (r/udub) | https://www.reddit.com/r/udub/comments/1tpts6r/applying_to_the_allen_school_as_a_current_uw/ |
| 10 | `documents/cs_courses_must_takes.txt` | Reddit thread (r/udub) | https://www.reddit.com/r/udub/comments/1s5q27e/cs_course_must_takes/ |

The set deliberately mixes **two source types** — Reddit course threads (workload,
assignment format, difficulty) and RateMyProfessors pages (individual instructor
teaching/grading style) — so the corpus covers both *course-level* and
*professor-level* questions.

---

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Preprocessing:** Before chunking, each document's whitespace is normalized with
`" ".join(text.split())`, which collapses newlines, tabs, and repeated spaces into
single spaces. This removes the irregular line breaks that come from
copy-pasting forum posts so they don't fragment chunks. Chunks are produced with a
sliding window (`chunk_text()` in [ingest.py](ingest.py)), and empty/whitespace-only
fragments are filtered out.

**Why these choices fit your documents:** The corpus is short, high-density student
review prose. Each distinct piece of advice (a textbook name, a lab format, a
grading rule) spans roughly 2–4 sentences, which fits comfortably inside 500
characters — large enough to keep one complete thought together, small enough to
avoid diluting a chunk with multiple unrelated topics. The 100-character overlap
guards against severing key proper nouns and course codes (e.g. "CSE 311",
"LaTeX") across a chunk boundary, since courses are frequently referenced by number
alone.

**Final chunk count:** 54 chunks across 10 documents (per-file: 8/4/4/3/4/6/9/6/5/5).

---

## Sample Chunks

Five representative chunks (evenly sampled across the corpus by `ingest.py`), each
labeled with its source document and character length:

**Chunk 1 — `applying_to_allen_school_internal.txt` (499 chars)**
> "What is the optimal course pathway, extracurricular strategy, and research acquisition method for a current UW student applying to transfer into the Allen School? Navigating the internal application pathway requires a strategic blend of maintaining an exceptional prerequisite GPA, displaying consistent academic pacing, and building strong relationships with the computer science faculty. Prerequisite Course Selection and Pacing (CSE 12x Track): - Progression Choices: Students entering with prior"

**Chunk 2 — `cse332_workload.txt` (500 chars)**
> "332 and CSE 421 would give you the depth for those topics, while leetcode will give you breadth. In 332, you just learn the different data structures and algorithms and how to implement them. It's more just going in and getting your hands dirty through projects while the exams test you on your theoretical knowledge. I found 332 helpful but I also came into UW with almost no coding experience. For me it helped to review the concepts from 332 before interviewing, but I used the LeetCode 75 list fo"

**Chunk 3 — `cse351_hardware_transition.txt` (500 chars)**
> "ing and provide the best frameworks for starting the difficult projects. - Textbooks and Reading: The classic textbook 'The C Programming Language' by Kernighan and Ritchie (K&R) is highly recommended for building foundational C proficiency before or during the first few weeks of class. Reading through it allows students to parse the course's code requirements with much less trouble. The official class textbook is also noted as being helpful specifically for mastering the complex mechanics of ha"

**Chunk 4 — `prof_elba_garza_style.txt` (500 chars)**
> "ng on technical mechanics. Some students opt to watch archived lectures from prior quarters to understand the programming syntax, though her one-on-one conceptual explanations during office hours are noted as being significantly clearer than her main lectures. - Hardware/Software Interface (CSE 351): In advanced systems courses, students frequently describe her lectures as highly disorganized and difficult to follow, noting that it can be tough to map her train of thought. Additionally, she occa"

**Chunk 5 — `prof_mahmood_hameed_style.txt` (386 chars)**
> "el. In foundational environments like Fundamentals of Electrical Engineering (EE 215), his pacing is highly praised for clarity. In subsequent signals and systems tracks (EE 242) or advanced design tracks (EE 371), the lecture delivery can occasionally feel rushed or disconnected, forcing students to rely more heavily on external engineering textbooks and supplementary video content."

These illustrate two chunking behaviors worth noting: Chunks 3–5 begin mid-word
("ing", "ng", "el") because fixed-character splitting cuts across token boundaries —
the 100-character overlap exists precisely so the preceding chunk still carries the
start of that thought. Each chunk also stays tightly on a single topic, which is the
goal of the 500-character size.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, run locally through
ChromaDB's `SentenceTransformerEmbeddingFunction`. The vector store uses **cosine
distance** (`hnsw:space: "cosine"`). Retrieval returns the **top-3** chunks per query.

**Production tradeoff reflection:** `all-MiniLM-L6-v2` is fast, free, and runs
locally with near-instant latency, which is ideal for this project. If cost were
not a constraint in a real deployment, the main tradeoff worth weighing is its
**256-token context limit** — long student threads get truncated. A hosted model
like `text-embedding-3-large` or Cohere `embed-v3` would extend the window to
~8,192 tokens (letting whole threads embed as single units), improve accuracy on
domain-specific jargon (e.g. distinguishing "cache" in a systems-architecture sense
from a browser cache), and better capture nuanced student sentiment. The costs are
real money per call, network latency, and a dependency on an external API instead
of a self-contained local model.

---

## Retrieval Test Results

Raw retrieval output from `vector_store.py` (cosine distance; lower = more similar).
These show the top chunks returned *before* generation, so retrieval quality can be
judged independently of the LLM.

**Query 1 — "What is the grading rigor like in CSE 311, and what tools do students recommend for taking notes and writing homework?"**

| Rank | Distance | Source | Chunk excerpt |
|------|----------|--------|---------------|
| 1 | 0.3428 | `prof_kevin_lin_style.txt` | "...his upper-level courses, such as data structures (CSE 373), present a significantly stressful and polarizing experience..." |
| 2 | 0.3517 | `cse311_reviews.txt` | "What is CSE 311 like? ...Would an iPad su[ffice]..." |
| 3 | 0.3773 | `cse311_reviews.txt` | "...the TAs often make mistakes in grading if you give them a correct but unusual solution..." |
| 4 | 0.4195 | `cse311_reviews.txt` | "special symbols that a laptop can get in the way of... [suggest learning LaTeX]" |

*Why relevant:* Ranks 2–4 all come from `cse311_reviews.txt` and directly address the
question's two halves — grading strictness (rank 3) and note-taking tools (ranks 2,
4). This query also exposes the system's main weakness: rank 1 is an off-document
`prof_kevin_lin_style.txt` chunk scoring highest, and since the app retrieves only
**top-3**, the LaTeX chunk (rank 4) is excluded — see the Failure Case Analysis.

**Query 2 — "How does the project workload of CSE 333 compare to CSE 351, and what is the typical format of its assignments?"**

| Rank | Distance | Source | Chunk excerpt |
|------|----------|--------|---------------|
| 1 | 0.2099 | `cse333_system_tips.txt` | "What is the workload for CSE 333 and how does it compare to CSE 351?..." |
| 2 | 0.3307 | `cse333_system_tips.txt` | "...definitely more demanding than CSE 351. The course structure generally requires completing a small programming exercise in C..." |
| 3 | 0.3357 | `cse351_hardware_transition.txt` | "What makes CSE 351 difficult compared to the introductory programming courses..." |
| 4 | 0.3363 | `cse344_databases.txt` | "...Workload Comparison: CSE 344 requires less week[ly]..." |

*Why relevant:* This is the cleanest retrieval of the set — the strongest match
(distance 0.21) is the exact question phrased back, and ranks 1–3 pair the two
courses being compared (`cse333` and `cse351`). The chunk at rank 2 literally
contains both the comparison ("more demanding than CSE 351") and the assignment
format, which is why the generated answer for this question was fully accurate.

**Query 3 — "What specific strategy is recommended for an internal UW student looking to secure an undergraduate research position with a computer science professor?"**

| Rank | Distance | Source | Chunk excerpt |
|------|----------|--------|---------------|
| 1 | 0.4570 | `applying_to_allen_school_internal.txt` | "What is the optimal course pathway, extracurricular strategy, and research acquisition method..." |
| 2 | 0.4822 | `applying_to_allen_school_internal.txt` | "...students should avoid generic, cold inquiries. Instead, they should consistently attend the weekly office hours..." |
| 3 | 0.5076 | `applying_to_allen_school_internal.txt` | "...the depth of active participation and documented learning outcomes..." |
| 4 | 0.5959 | `cs_courses_must_takes.txt` | "...Sophomore Research Pathways (CSE 494M): A structured undergraduate research seminar..." |

*Why relevant:* All three top chunks come from the single most on-topic document, and
rank 2 contains the exact recommended strategy (avoid cold inquiries, attend office
hours). The distances are higher (0.46–0.51) than the other queries because this is a
longer, more abstract question, but the source is still correctly isolated.

---

## Grounded Generation

**System prompt grounding instruction:** The system prompt (in [query.py](query.py))
does not merely *suggest* using the documents — it constrains the model explicitly:

> "You answer using ONLY the information in the CONTEXT block provided with each
> question. ... Use only facts stated in the CONTEXT. Do not use any outside or
> prior knowledge, even if you are confident it is correct. If the CONTEXT does not
> contain enough information to answer the question, reply with exactly this
> sentence and nothing else: *'I don't have enough information on that.'* Do not
> speculate, generalize, or fill gaps with what is 'usually' true."

Each query is sent at `temperature=0` for deterministic, context-faithful output.
The retrieved chunks are injected as a labelled `CONTEXT` block, each tagged with
its source filename, and the user turn ends with "Answer using only the CONTEXT
above."

**How source attribution is surfaced in the response:** Source attribution is
**guaranteed programmatically, not left to the model.** After retrieval, `ask()`
collects the distinct `source` filenames from the retrieved chunks' metadata
(preserving relevance order) and returns them as a separate `sources` list. The
Gradio UI renders these in a dedicated "Retrieved from" field. Because the
citations are derived from retrieval metadata rather than parsed out of the model's
prose, the model cannot invent, omit, or misattribute a source. A relevance
backstop also filters chunks beyond a cosine-distance cutoff; if nothing relevant is
retrieved, the system returns the decline message **without** calling the LLM at all.

---

## Example Responses

Two grounded responses (with source attribution as shown in the UI's "Retrieved
from" field) plus one out-of-scope query showing the refusal.

**Example 1 — grounded answer**
> **Q:** How does the project workload of CSE 333 compare to CSE 351, and what is the typical format of its assignments?
>
> **Answer:** The workload for CSE 333 is a pretty big time commitment and is definitely more demanding than CSE 351. The typical format of its assignments includes completing a small programming exercise in C or C++ every few days, alongside a much larger, multi-week programming lab due every two weeks.
>
> **Retrieved from:**
> • cse333_system_tips.txt
> • cse351_hardware_transition.txt

**Example 2 — grounded answer**
> **Q:** What specific strategy is recommended for an internal UW student looking to secure an undergraduate research position with a computer science professor?
>
> **Answer:** To secure a research position, students should consistently attend the weekly office hours of their core computer science professors, actively asking deep, adjacent questions about lecture material, and reading the professor's published research papers beforehand to build an authentic academic relationship. Once rapport is established, mid-quarter, students can leverage this connection to formally ask for a position.
>
> **Retrieved from:**
> • applying_to_allen_school_internal.txt

**Example 3 — out-of-scope refusal**
> **Q:** What is the best pizza place near the UW campus?
>
> **Answer:** I don't have enough information on that.
>
> **Retrieved from:** — (no sources)

The third response confirms grounding: nothing in the corpus covers campus dining,
so the system declines with its fixed refusal sentence rather than answering from the
model's general knowledge, and no sources are attached.

---

## Query Interface

The interface is a **Gradio web app** ([app.py](app.py)), launched with `python app.py`
and served at `http://localhost:7860`.

**Input field:**
- *Your question* — a single-line textbox. The query submits either by clicking the
  **Ask** button or by pressing Enter in the textbox.

**Output fields:**
- *Answer* — a multi-line textbox (8 lines) showing the grounded response generated by
  Groq from the retrieved context.
- *Retrieved from* — a multi-line textbox (4 lines) listing the source document
  filename(s) the answer drew from, one per line. For out-of-scope questions it shows
  a note that the question was outside the documents.

**Sample interaction transcript:**
```
Your question:  What are the primary grading and lecture characteristics of
                Professor Kevin Lin's upper-level courses?

[Ask]

Answer:         Professor Kevin Lin's upper-level courses, such as data structures
                (CSE 373), have a grading system that is heavily test-heavy, with
                exams being the primary metric for a student's final score. The
                lectures present a significantly stressful and polarizing
                experience for many students. Daily participation, attendance, and
                coding projects require a large time commitment but contribute
                relatively little to the final score.

Retrieved from: • prof_kevin_lin_style.txt
                • prof_mahmood_hameed_style.txt
```

---

## Evaluation Report

All 5 questions were run through the live system via `python evaluate.py`. Responses
below are summarized; full verbatim output is in `eval_results.md`.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | CSE 311 grading rigor + note/HW tools | Strict, nitpicky proof grading; iPad notes + LaTeX for homework | Confirmed rigorous, nitpicky proof grading (every step explicit) and iPad notes for symbols — **but omitted the LaTeX-for-homework recommendation.** Cited `cse311_reviews.txt`, `prof_kevin_lin_style.txt`. | Partially relevant | **Partially accurate** |
| 2 | CSE 333 vs CSE 351 workload + assignment format | 333 much heavier; short C/C++ exercises + multi-week labs | 333 more demanding than 351; small C/C++ exercise every few days + larger multi-week lab every two weeks. Cited `cse333_system_tips.txt`, `cse351_hardware_transition.txt`. | Relevant | **Accurate** |
| 3 | Prof. Kevin Lin grading + lecture style | Test-heavy, unconventional rubric, flipped classroom | Test-heavy exams as primary metric; projects/attendance high effort but low weight — **but did not surface the flipped-classroom style or the unconventional rubric.** Cited `prof_kevin_lin_style.txt`, `prof_mahmood_hameed_style.txt`. | Partially relevant | **Partially accurate** |
| 4 | Strategy for landing UG research | Build rapport via office hours, read papers, ask mid-quarter | Attend weekly office hours, ask deep adjacent questions, read the professor's papers, then ask mid-quarter once rapport is built. Cited `applying_to_allen_school_internal.txt`. | Relevant | **Accurate** |
| 5 | Career-critical electives for cloud-scale SWE | CSE 452 (Distributed) + CSE 451 (OS) | Recommended CSE 452 (Distributed Systems) + CSE 451 (Operating Systems) as career-critical for cloud-scale/backend; minor nuance ("distinguishes candidates even as tools abstract the OS away") dropped. Cited `cs_courses_must_takes.txt`, `applying_to_allen_school_internal.txt`. | Relevant | **Accurate** |

**Off-topic control** ("best pizza place near UW campus"): the system correctly
returned *"I don't have enough information on that."* with no sources — confirming
the grounding instruction holds for questions the corpus doesn't cover.

**Summary:** 3 of 5 accurate, 2 of 5 partially accurate, 0 inaccurate. Both partial
results stem from the *same* root cause (see below): a required secondary fact lived
in a chunk that fell outside the top-3 retrieval window.

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** Question 1 — *"What is the grading rigor like in CSE 311,
and what tools do students recommend for taking notes and writing homework?"*
(Judged **partially accurate**.)

**What the system returned:** It correctly described the rigorous, nitpicky proof
grading and recommended using an **iPad** for note-taking — but it **omitted the
recommendation to learn LaTeX for writing homework assignments**, which was part of
the expected answer.

**Root cause (tied to a specific pipeline stage):** This is a **retrieval-breadth**
failure at the top-k stage, not a generation failure. The LaTeX recommendation *is*
in the corpus — it sits in `documents/cse311_reviews.txt` ("The class will suggest
learning LaTeX to write your homework assignments..."), and that file split into 4
separate chunks. The question requires **two distinct facts** (grading rigor *and*
homework tooling) that live in **different chunks** of that document. With retrieval
fixed at **top-k = 3**, and one of those three slots consumed by a
`prof_kevin_lin_style.txt` chunk (cross-context contamination — Kevin Lin teaches
CSE-adjacent courses, so his page scores highly for a CSE 311 query), only ~2
`cse311_reviews.txt` chunks survived into the context window. The chunk carrying the
LaTeX sentence was crowded out. The model grounded faithfully on what it *did*
receive — which is exactly the correct behavior — so the gap is upstream, in what
retrieval surfaced. (Question 3 fails the same way: the "flipped classroom" detail
lives in a `prof_kevin_lin_style.txt` chunk that didn't make the top-3, with a slot
lost to an off-target `prof_mahmood_hameed_style.txt` chunk.)

**What you would change to fix it:** (1) Raise `TOP_K` from 3 to ~5 so multi-fact
questions have room for both halves of the answer. (2) Add a small per-document cap
or metadata filter so a query explicitly about a course (CSE 311) prefers
course-thread chunks and down-weights professor-page chunks, reducing cross-context
contamination. (3) Longer term, add a reranking pass over a larger candidate pool
(e.g. retrieve top-10, rerank to top-5) to surface both required facts even when
they're distributed across several chunks of the same source.

---

## Spec Reflection

**One way the spec helped you during implementation:**
The Chunking Strategy section of `planning.md` translated almost directly into code.
Because the spec committed to concrete numbers — 500-character chunks, 100-character
overlap, with a stated reason (keeping a single 2–4 sentence piece of advice intact
while preserving course codes across boundaries) — `chunk_text()` was implemented
with those exact parameters as defaults and required no guesswork or back-and-forth.
Having the rationale written down also made it easy to defend the choice rather than
treating it as arbitrary.

**One way your implementation diverged from the spec, and why:**
The original plan specified the **Gemini API** for generation and a **terminal CLI**
for the interface. During implementation both changed: generation moved to **Groq
(`llama-3.3-70b-versatile`)** because it is free-tier, OpenAI-compatible, and the key
provisioning was simpler for this project, and the interface moved to a **Gradio web
UI** so a viewer can use the system without command-line knowledge and so source
citations render in a clearly labelled field. `planning.md` and the architecture
diagram were updated to match these decisions.

---

## AI Usage

**Instance 1 — Generation + interface code (Claude Opus 4.8)**

- *What I gave the AI:* My Milestone 5 plan from `planning.md`, the pipeline diagram
  in `mermaid.md`, my existing `vector_store.py` (so it knew the collection name,
  embedding model, and metadata schema), and the Milestone 5 rubric — including the
  grounding requirement and the Gradio skeleton.
- *What it produced:* `query.py` with an `ask()` function (retrieve top-k → build a
  labelled context block → call Groq with a strict grounding system prompt →
  return `{"answer", "sources"}`) and `app.py` wiring it to a Gradio UI.
- *What I changed or overrode:* I directed it to switch from Gemini to **Groq** and
  from a terminal CLI to **Gradio**, and I had it make **source attribution
  programmatic** (pulled from chunk metadata) rather than asking the model to cite
  sources in prose — so citations can't be hallucinated. I also reviewed the system
  prompt to confirm it *enforces* grounding (exact decline sentence, "no outside
  knowledge") rather than merely suggesting it.

**Instance 2 — Ingestion/retrieval code + environment setup (Gemini 3.5 Flash)**

- *What I gave the AI:* For Milestones 1–4, I gave Gemini my `planning.md` Chunking
  Strategy and Retrieval Approach sections (the 500-char / 100-char parameters and
  the `all-MiniLM-L6-v2` + ChromaDB choices) and asked it to generate the ingestion
  and vector-store code. Separately, I asked it for help standing up the project
  environment — creating the virtual environment, installing dependencies
  (`sentence-transformers`, `chromadb`, `groq`, `python-dotenv`), and configuring the
  `.env` / `GROQ_API_KEY` loading.
- *What it produced:* `ingest.py` (a `chunk_text()` sliding-window chunker plus a
  diagnostic ingestion pipeline) and `vector_store.py` (builds a persistent ChromaDB
  collection with the all-MiniLM-L6-v2 embedding function and cosine distance), along
  with the step-by-step venv creation, `pip install` commands, and the
  `python-dotenv` setup for reading the API key.
- *What I changed or overrode:* I kept the generated code largely as-is, but the key
  point is that I **directed it with my own spec up front** rather than accepting
  defaults — the 500/100 chunking and the embedding/distance/top-k configuration came
  from my `planning.md`, not from Gemini's suggestions. After it generated the code I
  **verified the output against my spec** before trusting it: I ran `ingest.py` and
  confirmed it produced 54 chunks, and ran `vector_store.py`'s test queries to confirm
  retrieval returned the expected source documents at strong distances. I also later
  overrode the original generation/interface plan (Gemini API → Groq, CLI → Gradio) in
  Milestone 5 — see Instance 1.