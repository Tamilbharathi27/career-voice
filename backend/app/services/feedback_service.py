import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class FeedbackService:
    """Service to produce personalized, actionable feedback and improvement recommendations."""

    def generate_answer_feedback(
        self,
        question_text: str,
        transcript: str,
        nlp_res: Dict[str, Any],
        voice_res: Dict[str, Any],
        composite_score: float
    ) -> Dict[str, Any]:
        """Generate specific per-question coaching feedback, strengths, and improvement suggestions."""
        if not transcript or len(transcript.strip()) < 5:
            return {
                "feedback_text": "No spoken or written answer was provided for this question. Zero credit recorded.",
                "strengths": [],
                "improvements": ["Be sure to record your spoken response or type your answer before clicking Submit."],
                "suggested_answer": f"When answering '{question_text[:70]}...', structure your response using Situation, Task, Action, and Result (STAR)."
            }

        strengths: List[str] = []
        improvements: List[str] = []

        # Acoustic & Delivery Feedback
        wpm = voice_res.get("pace_wpm", 130.0)
        fillers_count = voice_res.get("filler_words_count", 0)
        
        if 120 <= wpm <= 160:
            strengths.append(f"Well-paced delivery ({wpm} WPM) maintaining steady conversational rhythm.")
        elif wpm < 115:
            improvements.append(f"Speaking pace was slightly slow ({wpm} WPM). Practice speaking with more energy and momentum.")
        else:
            improvements.append(f"Speaking pace was brisk ({wpm} WPM). Integrate intentional 1-second pauses after key points.")

        if fillers_count == 0:
            strengths.append("Crisp vocal delivery with zero detected filler words.")
        elif fillers_count <= 2:
            strengths.append("Minimal filler words used, maintaining a professional presence.")
        else:
            fillers_str = ", ".join([f"'{k}' ({v}x)" for k, v in voice_res.get("filler_words_breakdown", {}).items()])
            improvements.append(f"Detected {fillers_count} filler words ({fillers_str}). Practice replacing fillers with silent pauses.")

        # NLP & Technical Feedback
        matched_kw = nlp_res.get("matched_keywords", [])
        missing_kw = nlp_res.get("missing_keywords", [])
        star_breakdown = nlp_res.get("star_breakdown", {})

        if matched_kw:
            strengths.append(f"Strong technical vocabulary covering: {', '.join(matched_kw[:4])}.")
        if missing_kw:
            improvements.append(f"Consider referencing key concepts like: {', '.join(missing_kw[:3])}.")

        # STAR Method Analysis
        star_missing = [k.capitalize() for k, v in star_breakdown.items() if not v]
        if not star_missing:
            strengths.append("Structured response adhering fully to the STAR framework (Situation, Task, Action, Result).")
        elif len(star_missing) <= 2:
            improvements.append(f"Enhance answer structure by explicitly emphasizing the '{', '.join(star_missing)}' phase of STAR.")

        # Suggested Answer formulation
        suggested_answer = (
            f"When answering '{question_text[:70]}...', start by defining the direct context (Situation), "
            f"specify your technical goal (Task), detail the exact libraries, patterns, or architecture you chose (Action), "
            f"and conclude with quantifiable metrics or system impact (Result)."
        )

        # Summary text
        if composite_score >= 85:
            feedback_text = "Exceptional response demonstrating technical mastery, articulate cadence, and structured thought."
        elif composite_score >= 70:
            feedback_text = "Solid response with good technical substance. Focus on eliminating remaining filler words and quantifying results."
        elif composite_score >= 50:
            feedback_text = "Partially accurate response with room for improvement. Focus on technical keywords and STAR structure."
        elif composite_score >= 30:
            feedback_text = "Response needs significant improvement. Key technical concepts were missing or off-target."
        else:
            feedback_text = "Incorrect or off-target response. The answer did not address the core technical requirement of the question."

        return {
            "feedback_text": feedback_text,
            "strengths": strengths,
            "improvements": improvements,
            "suggested_answer": suggested_answer
        }

    def generate_session_summary_feedback(
        self,
        role: str,
        overall_score: float,
        technical_score: float,
        communication_score: float,
        evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate high-level report card strengths, weaknesses, and targeted recommendations."""
        strengths: List[str] = []
        weaknesses: List[str] = []
        recommendations: List[str] = []

        if technical_score >= 80:
            strengths.append(f"Demonstrated deep technical competency and domain mastery for {role}.")
        elif technical_score >= 50:
            strengths.append(f"Basic familiarity with core concepts in {role}.")
            weaknesses.append("Technical answers were partially accurate but lacked specific architecture patterns and concrete trade-offs.")
        else:
            strengths.append("Attempted mock interview session.")
            weaknesses.append(f"Responses failed to cover key technical requirements and concepts expected for a {role}.")
            weaknesses.append("Answers lacked technical depth, keyword coverage, and STAR methodology structure.")

        if communication_score >= 80:
            strengths.append("High vocal clarity, balanced speech pace, and polished professional poise.")
        elif communication_score >= 50:
            weaknesses.append("Delivery showed speech cadence variance or filler word accumulation under pressure.")
        else:
            weaknesses.append("Speech delivery was incomplete, silent, or lacked clear vocal projection.")

        # Aggregate recommendations
        if overall_score < 40:
            recommendations.append(f"Thoroughly review fundamental concepts, system design, and terminology for {role} roles.")
            recommendations.append("Practice structuring technical answers explicitly into Situation, Task, Action, and Result (STAR).")
            recommendations.append("Ensure you record a complete, articulate spoken answer for every interview question.")
        else:
            recommendations.append("Continue practicing structured STAR method delivery for technical scenarios.")
            recommendations.append("Quantify results with metrics (e.g., 'reduced latency by 35%', 'improved throughput by 2x').")
            recommendations.append(f"Review core design patterns and concurrency mechanisms relevant to {role} roles.")

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations
        }

feedback_service = FeedbackService()
