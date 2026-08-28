import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.interview import InterviewSession, Question, Answer, InterviewStatus, QuestionType
from app.models.evaluation import AnswerEvaluation, SessionReport
from app.services.stt_service import stt_service
from app.services.voice_analysis_service import voice_analysis_service
from app.services.nlp_service import nlp_service
from app.services.scoring_service import scoring_service
from app.services.feedback_service import feedback_service
from app.db.init_db import QUESTION_BANK

logger = logging.getLogger(__name__)

class AgentInterviewer:
    """Orchestrates dynamic AI interviewer state machine and adaptive question generation."""

    def _safe_commit(self, db: Session):
        """Commit transaction with automatic reconnect retry if cloud connection dropped during AI calls."""
        try:
            db.commit()
        except Exception as e:
            logger.warning(f"DB Commit warning ({e}). Retrying commit with fresh connection...")
            try:
                db.rollback()
                db.commit()
            except Exception as retry_err:
                logger.error(f"Commit retry failed: {retry_err}")
                raise

    def _get_tailored_template(self, session: InterviewSession, target_index: int, db: Optional[Session] = None) -> Dict[str, Any]:
        """Select a unique, non-repeating question template tailored to candidate's tech stack."""
        role_questions = QUESTION_BANK.get(session.role, QUESTION_BANK.get("Full Stack Engineer", []))
        if not role_questions:
            role_questions = QUESTION_BANK["Full Stack Engineer"]

        # Track questions already asked to this user
        already_asked = set()
        if db and session.id:
            try:
                past_qs = db.query(Question.question_text).join(InterviewSession).filter(
                    InterviewSession.user_id == session.user_id
                ).all()
                already_asked = {q[0] for q in past_qs}
            except Exception:
                pass

        candidate_stacks = []
        if session.tech_stack:
            try:
                candidate_stacks = json.loads(session.tech_stack)
            except Exception:
                candidate_stacks = [s.strip() for s in session.tech_stack.split(",") if s.strip()]

        # Try to find templates that match candidate's tech stack selection
        matched_templates = []
        if candidate_stacks:
            for q in role_questions:
                q_stack = q.get("tech_stack")
                if q_stack and any(cs.lower() in q_stack.lower() or q_stack.lower() in cs.lower() for cs in candidate_stacks):
                    matched_templates.append(q)

        pool = matched_templates if matched_templates else role_questions

        # Exclude questions already asked to this candidate if possible
        unasked_pool = [q for q in pool if q["question_text"] not in already_asked]
        if not unasked_pool:
            unasked_pool = pool

        # Pick unique template deterministically offset by target_index and session id
        import random
        seed_val = (session.id or 1) * 37 + target_index
        rng = random.Random(seed_val)
        selected_template = rng.choice(unasked_pool)
        
        # If candidate specified tech stacks, ensure question and expected keywords reflect them
        if candidate_stacks:
            kw_list = []
            if selected_template.get("expected_keywords"):
                try:
                    kw_list = json.loads(selected_template["expected_keywords"])
                except Exception:
                    kw_list = [k.strip() for k in selected_template["expected_keywords"].split(",")]

            # Inject candidate stack keywords if missing
            for cs in candidate_stacks:
                clean_cs = cs.split("(")[0].strip() # e.g. "MERN Stack" from "MERN Stack (MongoDB...)"
                if clean_cs not in kw_list:
                    kw_list.append(clean_cs)

            # Create tailored copy of template
            q_text = selected_template["question_text"]
            stack_str = ", ".join(candidate_stacks[:3])
            
            # If default template is generic, add tech context prefix or suffix
            if not any(cs.lower() in q_text.lower() for cs in candidate_stacks):
                q_text = f"Regarding your experience with {stack_str}: {q_text}"

            return {
                "question_text": q_text,
                "question_type": selected_template.get("question_type", QuestionType.TECHNICAL.value),
                "competency": selected_template.get("competency", "Technical Competency"),
                "expected_keywords": json.dumps(kw_list)
            }

        return selected_template

    def initialize_interview(self, db: Session, session: InterviewSession) -> Question:
        """Start interview session state machine and generate initial role-based question."""
        session.status = InterviewStatus.IN_PROGRESS.value
        session.current_question_index = 0

        initial_template = self._get_tailored_template(session, 0, db=db)

        first_question = Question(
            session_id=session.id,
            question_text=initial_template["question_text"],
            question_type=initial_template["question_type"],
            competency=initial_template["competency"],
            expected_keywords=initial_template.get("expected_keywords"),
            order_index=0,
            is_followup=False
        )
        db.add(first_question)
        self._safe_commit(db)
        db.refresh(first_question)
        db.refresh(session)
        return first_question

    def process_answer_and_advance(
        self,
        db: Session,
        session_id: int,
        question_id: int,
        audio_file_path: str,
        audio_duration_seconds: float = 0.0,
        provided_transcript: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        State Machine Step:
        1. Transcribe speech to text
        2. Execute acoustic & NLP evaluations
        3. Save evaluation records
        4. Decide next action: adaptive follow-up, next competency topic, or complete interview & generate report.
        """
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            raise ValueError("Interview session not found")

        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise ValueError("Question not found")

        # 1. Speech-to-Text
        stt_result = stt_service.transcribe_audio(audio_file_path, fallback_transcript=provided_transcript)
        transcript = stt_result.get("transcript", "")

        # 2. Store Answer Record
        answer = db.query(Answer).filter(Answer.question_id == question.id).first()
        if not answer:
            answer = Answer(
                question_id=question.id,
                audio_url=audio_file_path,
                audio_duration_seconds=audio_duration_seconds,
                transcript=transcript,
                submitted_at=datetime.now(timezone.utc)
            )
            db.add(answer)
            self._safe_commit(db)
            db.refresh(answer)
        else:
            answer.transcript = transcript
            answer.audio_url = audio_file_path
            answer.audio_duration_seconds = audio_duration_seconds
            self._safe_commit(db)
            db.refresh(answer)

        # 3. Multi-Modal AI Analysis
        expected_kw = []
        if question.expected_keywords:
            try:
                expected_kw = json.loads(question.expected_keywords)
            except Exception:
                expected_kw = [k.strip() for k in question.expected_keywords.split(",") if k.strip()]

        voice_res = voice_analysis_service.analyze_audio_file(audio_file_path, transcript, audio_duration_seconds)
        nlp_res = nlp_service.analyze_answer(question.question_text, transcript, expected_kw)

        composite_score = scoring_service.calculate_answer_score(
            nlp_score=nlp_res["overall_nlp_score"],
            voice_score=voice_res["voice_score"],
            sentiment_score=nlp_res["sentiment_score"],
            star_score=nlp_res["star_score"]
        )

        fb_res = feedback_service.generate_answer_feedback(
            question_text=question.question_text,
            transcript=transcript,
            nlp_res=nlp_res,
            voice_res=voice_res,
            composite_score=composite_score
        )

        # 4. Save Answer Evaluation
        evaluation = db.query(AnswerEvaluation).filter(AnswerEvaluation.answer_id == answer.id).first()
        if not evaluation:
            evaluation = AnswerEvaluation(
                answer_id=answer.id,
                nlp_score=nlp_res["overall_nlp_score"],
                voice_score=voice_res["voice_score"],
                sentiment_score=nlp_res["sentiment_score"],
                star_score=nlp_res["star_score"],
                composite_score=composite_score,
                pace_wpm=voice_res["pace_wpm"],
                filler_words_count=voice_res["filler_words_count"],
                filler_words_breakdown=json.dumps(voice_res["filler_words_breakdown"]),
                pause_ratio=voice_res["pause_ratio"],
                clarity_score=voice_res["clarity_score"],
                feedback_text=fb_res["feedback_text"],
                strengths=json.dumps(fb_res["strengths"]),
                improvements=json.dumps(fb_res["improvements"]),
                suggested_answer=fb_res["suggested_answer"]
            )
            db.add(evaluation)
        else:
            evaluation.nlp_score = nlp_res["overall_nlp_score"]
            evaluation.voice_score = voice_res["voice_score"]
            evaluation.sentiment_score = nlp_res["sentiment_score"]
            evaluation.star_score = nlp_res["star_score"]
            evaluation.composite_score = composite_score
            evaluation.pace_wpm = voice_res["pace_wpm"]
            evaluation.filler_words_count = voice_res["filler_words_count"]
            evaluation.filler_words_breakdown = json.dumps(voice_res["filler_words_breakdown"])
            evaluation.pause_ratio = voice_res["pause_ratio"]
            evaluation.clarity_score = voice_res["clarity_score"]
            evaluation.feedback_text = fb_res["feedback_text"]
            evaluation.strengths = json.dumps(fb_res["strengths"])
            evaluation.improvements = json.dumps(fb_res["improvements"])
            evaluation.suggested_answer = fb_res["suggested_answer"]

        self._safe_commit(db)
        db.refresh(evaluation)

        # 5. Determine Next Question / Interview Completion
        session.current_question_index += 1
        is_completed = session.current_question_index >= session.question_count

        next_question_obj = None

        if not is_completed:
            # Decide next question dynamically (adaptive follow-up vs new competency)
            next_question_obj = self._decide_next_question(
                db=db,
                session=session,
                prev_question=question,
                prev_evaluation=evaluation,
                prev_transcript=transcript
            )
        else:
            # Complete Session & Generate Final Report
            session.status = InterviewStatus.COMPLETED.value
            session.completed_at = datetime.now(timezone.utc)
            self._safe_commit(db)
            self._generate_final_session_report(db, session)

        self._safe_commit(db)
        db.refresh(session)

        return {
            "session_status": session.status,
            "current_index": session.current_question_index,
            "total_questions": session.question_count,
            "is_completed": is_completed,
            "transcript": transcript,
            "evaluation": {
                "composite_score": composite_score,
                "nlp_score": nlp_res["overall_nlp_score"],
                "voice_score": voice_res["voice_score"],
                "sentiment_score": nlp_res["sentiment_score"],
                "pace_wpm": voice_res["pace_wpm"],
                "filler_words_count": voice_res["filler_words_count"],
                "feedback_text": fb_res["feedback_text"],
                "strengths": fb_res["strengths"],
                "improvements": fb_res["improvements"],
            },
            "next_question": {
                "id": next_question_obj.id,
                "question_text": next_question_obj.question_text,
                "question_type": next_question_obj.question_type,
                "competency": next_question_obj.competency,
                "order_index": next_question_obj.order_index,
                "is_followup": next_question_obj.is_followup
            } if next_question_obj else None
        }

    def _decide_next_question(
        self,
        db: Session,
        session: InterviewSession,
        prev_question: Question,
        prev_evaluation: AnswerEvaluation,
        prev_transcript: str
    ) -> Question:
        """Adaptive question selector: probes weak responses or progresses to new topics."""
        # Adaptive Follow-Up Rule: If composite score is low or missing STAR, ask a targeted follow-up
        if prev_evaluation.composite_score < 68.0 and not prev_question.is_followup:
            if not prev_transcript or len(prev_transcript.strip()) < 5 or prev_evaluation.composite_score == 0.0:
                followup_text = (
                    f"No response was recorded for the previous question. Let's address the core requirement: "
                    f"could you walk me through your technical approach and how you would solve this scenario?"
                )
            elif prev_evaluation.composite_score < 40.0:
                followup_text = (
                    f"Your previous response appeared off-target or incomplete. To clarify your technical approach, "
                    f"could you specifically address the core architecture, tools, and trade-offs required for this question?"
                )
            else:
                followup_text = (
                    f"To build on your previous points, could you elaborate further on the specific "
                    f"trade-offs you considered and what the measurable outcome was?"
                )

            q = Question(
                session_id=session.id,
                question_text=followup_text,
                question_type=QuestionType.FOLLOW_UP.value,
                competency=prev_question.competency or "Deep Dive",
                expected_keywords=prev_question.expected_keywords,
                order_index=session.current_question_index,
                is_followup=True,
                parent_question_id=prev_question.id
            )
            db.add(q)
            self._safe_commit(db)
            db.refresh(q)
            return q

        # Otherwise, pick next competency topic from question bank (ensuring unique, unasked templates)
        next_template = self._get_tailored_template(session, session.current_question_index, db=db)

        q = Question(
            session_id=session.id,
            question_text=next_template["question_text"],
            question_type=next_template["question_type"],
            competency=next_template["competency"],
            expected_keywords=next_template.get("expected_keywords"),
            order_index=session.current_question_index,
            is_followup=False
        )
        db.add(q)
        self._safe_commit(db)
        db.refresh(q)
        return q

    def _generate_final_session_report(self, db: Session, session: InterviewSession) -> SessionReport:
        """Aggregate all questions and generate SessionReport model record."""
        questions = db.query(Question).filter(Question.session_id == session.id).order_by(Question.order_index).all()
        evaluations = []
        q_dicts = []

        for q in questions:
            q_dicts.append({"question_text": q.question_text, "competency": q.competency})
            if q.answer and q.answer.evaluation:
                evaluations.append({
                    "composite_score": q.answer.evaluation.composite_score,
                    "nlp_score": q.answer.evaluation.nlp_score,
                    "voice_score": q.answer.evaluation.voice_score,
                    "sentiment_score": q.answer.evaluation.sentiment_score
                })

        summary = scoring_service.calculate_session_summary(evaluations, q_dicts)
        fb_summary = feedback_service.generate_session_summary_feedback(
            role=session.role,
            overall_score=summary["overall_score"],
            technical_score=summary["technical_score"],
            communication_score=summary["communication_score"],
            evaluations=evaluations
        )

        report = db.query(SessionReport).filter(SessionReport.session_id == session.id).first()
        if not report:
            report = SessionReport(
                session_id=session.id,
                overall_score=summary["overall_score"],
                technical_score=summary["technical_score"],
                communication_score=summary["communication_score"],
                confidence_score=summary["confidence_score"],
                strengths=json.dumps(fb_summary["strengths"]),
                weaknesses=json.dumps(fb_summary["weaknesses"]),
                recommendations=json.dumps(fb_summary["recommendations"]),
                competency_breakdown=json.dumps(summary["competency_breakdown"]),
                generated_at=datetime.now(timezone.utc)
            )
            db.add(report)
        else:
            report.overall_score = summary["overall_score"]
            report.technical_score = summary["technical_score"]
            report.communication_score = summary["communication_score"]
            report.confidence_score = summary["confidence_score"]
            report.strengths = json.dumps(fb_summary["strengths"])
            report.weaknesses = json.dumps(fb_summary["weaknesses"])
            report.recommendations = json.dumps(fb_summary["recommendations"])
            report.competency_breakdown = json.dumps(summary["competency_breakdown"])

        self._safe_commit(db)
        db.refresh(report)
        return report

agent_interviewer = AgentInterviewer()
