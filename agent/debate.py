import os
from groq import Groq
import google.generativeai as genai

_groq = None
_gemini = None


def _get_groq() -> Groq:
    global _groq
    if _groq is None:
        _groq = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _groq


def _get_gemini():
    global _gemini
    if _gemini is None:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        _gemini = genai.GenerativeModel("gemini-1.5-flash")
    return _gemini


def _groq_chat(prompt: str) -> str:
    try:
        res = _get_groq().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"[Groq error: {e}]"


def _gemini_chat(prompt: str) -> str:
    try:
        res = _get_gemini().generate_content(prompt)
        return res.text.strip()
    except Exception as e:
        return f"[Gemini error: {e}]"


def run_debate(title: str, summary: str) -> dict:
    topic = f"{title}\n\n{summary}"

    insight = _groq_chat(
        f"You are an expert analyst. Given this article, present the single most important insight in 2-3 sentences.\n\nArticle: {topic}"
    )

    counterpoint = _gemini_chat(
        f"You are a critical thinker. Given this insight about an article, present a thoughtful counterpoint or alternative perspective in 2-3 sentences.\n\nInsight: {insight}\n\nOriginal article: {title}"
    )

    rebuttal = _groq_chat(
        f"You are a debater. Respond to this counterpoint with a concise rebuttal in 2-3 sentences.\n\nOriginal insight: {insight}\n\nCounterpoint: {counterpoint}"
    )

    synthesis = _groq_chat(
        f"Synthesize the following three perspectives into one clear, actionable conclusion in 3-4 sentences.\n\n1. Insight: {insight}\n2. Counterpoint: {counterpoint}\n3. Rebuttal: {rebuttal}"
    )

    return {
        "topic": title,
        "insight": insight,
        "counterpoint": counterpoint,
        "rebuttal": rebuttal,
        "synthesis": synthesis,
    }
