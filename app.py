"""
Milestone 5 — Gradio web interface for The Unofficial Guide.

Run:
    python app.py
Then open http://localhost:7860
"""

import gradio as gr

from query import ask


def handle_query(question):
    """Adapt ask() to Gradio's (answer, sources) two-output layout."""
    result = ask(question)
    if result["sources"]:
        sources = "\n".join(f"• {s}" for s in result["sources"])
    else:
        sources = "— (no sources: question was outside the documents)"
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide — UW Allen School") as demo:
    gr.Markdown(
        "# The Unofficial Guide — UW Allen School\n"
        "Ask about CSE course workloads, professor styles, and Allen School "
        "advice. Answers are grounded only in collected student reviews — if the "
        "documents don't cover your question, the system will say so."
    )

    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. How strict is grading in CSE 311?",
    )
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
