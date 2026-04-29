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
        f"당신은 전문 분석가입니다. 다음 기사에서 가장 중요한 핵심 인사이트를 2~3문장으로 한국어로 설명해주세요.\n\n기사: {topic}"
    )

    counterpoint = _gemini_chat(
        f"당신은 비판적 사고자입니다. 다음 인사이트에 대해 반론 또는 다른 시각을 2~3문장으로 한국어로 제시해주세요.\n\n인사이트: {insight}\n\n원문 제목: {title}"
    )

    rebuttal = _groq_chat(
        f"당신은 토론자입니다. 다음 반론에 대해 간결한 재반박을 2~3문장으로 한국어로 작성해주세요.\n\n원래 인사이트: {insight}\n\n반론: {counterpoint}"
    )

    synthesis = _groq_chat(
        f"다음 세 가지 관점을 종합하여 명확하고 실용적인 결론을 3~4문장으로 한국어로 작성해주세요.\n\n1. 인사이트: {insight}\n2. 반론: {counterpoint}\n3. 재반박: {rebuttal}"
    )

    return {
        "topic": title,
        "insight": insight,
        "counterpoint": counterpoint,
        "rebuttal": rebuttal,
        "synthesis": synthesis,
    }
