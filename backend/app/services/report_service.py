import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.interview import InterviewSession, Question
from app.models.evaluation import SessionReport
from app.models.user import User

logger = logging.getLogger(__name__)

class ReportService:
    """PDF and structured data reporting generator."""

    def generate_pdf_report(self, db: Session, session_id: int) -> str:
        """Generate a stylized PDF report card for an interview session."""
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            raise ValueError(f"Interview session {session_id} not found")

        user = db.query(User).filter(User.id == session.user_id).first()
        report = db.query(SessionReport).filter(SessionReport.session_id == session_id).first()
        questions = db.query(Question).filter(Question.session_id == session_id).order_by(Question.order_index).all()

        filename = f"career_voice_report_{session_id}_{int(datetime.now().timestamp())}.pdf"
        output_path = os.path.join(settings.REPORT_DIR, filename)

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )

            styles = getSampleStyleSheet()
            
            # Custom Palette
            PRIMARY = colors.HexColor("#2557e4")
            DARK = colors.HexColor("#0f172a")
            SECONDARY = colors.HexColor("#64748b")
            ACCENT = colors.HexColor("#10b981")
            BG_LIGHT = colors.HexColor("#f8fafc")

            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontSize=22,
                leading=26,
                textColor=PRIMARY,
                spaceAfter=6
            )
            subtitle_style = ParagraphStyle(
                'DocSubtitle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=SECONDARY,
                spaceAfter=14
            )
            heading_style = ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading2'],
                fontSize=14,
                leading=18,
                textColor=DARK,
                spaceBefore=12,
                spaceAfter=8
            )
            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=DARK
            )
            bullet_style = ParagraphStyle(
                'Bullet',
                parent=styles['Normal'],
                fontSize=9,
                leading=13,
                textColor=DARK,
                leftIndent=12
            )

            story = []

            # Header Banner
            story.append(Paragraph("<b>CAREER VOICE</b> — AI Mock Interview Report", title_style))
            date_str = session.completed_at.strftime("%B %d, %Y - %I:%M %p") if session.completed_at else datetime.now().strftime("%B %d, %Y")
            candidate_name = user.name if user else "Candidate"
            story.append(Paragraph(f"Candidate: <b>{candidate_name}</b> | Role: <b>{session.role}</b> ({session.difficulty.capitalize()}) | Date: {date_str}", subtitle_style))
            story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))

            # Score Summary Table
            overall = report.overall_score if report else 0.0
            tech = report.technical_score if report else 0.0
            comm = report.communication_score if report else 0.0
            conf = report.confidence_score if report else 0.0

            score_data = [
                ["Overall Score", "Technical NLP", "Speech & Delivery", "Confidence & Tone"],
                [f"{overall}%", f"{tech}%", f"{comm}%", f"{conf}%"]
            ]
            score_table = Table(score_data, colWidths=[130, 130, 130, 130])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, 1), BG_LIGHT),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, 1), 14),
                ('TEXTCOLOR', (0, 1), (-1, 1), PRIMARY),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('TOPPADDING', (0, 1), (-1, 1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 8),
            ]))
            story.append(score_table)
            story.append(Spacer(1, 14))

            # Strengths & Weaknesses
            if report and report.strengths:
                try:
                    strengths_list = json.loads(report.strengths)
                    story.append(Paragraph("<b>Key Strengths Identified</b>", heading_style))
                    for s in strengths_list:
                        story.append(Paragraph(f"• {s}", bullet_style))
                except Exception:
                    pass

            if report and report.weaknesses:
                try:
                    weaknesses_list = json.loads(report.weaknesses)
                    story.append(Paragraph("<b>Areas for Growth & Improvement</b>", heading_style))
                    for w in weaknesses_list:
                        story.append(Paragraph(f"• {w}", bullet_style))
                except Exception:
                    pass

            story.append(Spacer(1, 14))

            # Question by Question Detailed Breakdown
            story.append(Paragraph("<b>Question Performance Breakdown</b>", heading_style))
            for i, q in enumerate(questions, 1):
                story.append(Paragraph(f"<b>Q{i} ({q.competency or 'General'}):</b> {q.question_text}", body_style))
                if q.answer and q.answer.evaluation:
                    ev = q.answer.evaluation
                    eval_summary = f"Score: <b>{ev.composite_score}%</b> | Pace: <b>{ev.pace_wpm} WPM</b> | Filler Words: <b>{ev.filler_words_count}</b>"
                    story.append(Paragraph(eval_summary, subtitle_style))
                    if q.answer.transcript:
                        transcript_preview = q.answer.transcript if len(q.answer.transcript) < 220 else q.answer.transcript[:220] + "..."
                        story.append(Paragraph(f"<i>Transcript snippet:</i> \"{transcript_preview}\"", bullet_style))
                    if ev.feedback_text:
                        story.append(Paragraph(f"<i>Feedback:</i> {ev.feedback_text}", bullet_style))
                story.append(Spacer(1, 8))

            doc.build(story)
            logger.info(f"Generated PDF report at: {output_path}")

            # Update report URL in database
            if report:
                report.report_url = output_path
                db.commit()

            return output_path

        except Exception as e:
            logger.error(f"Error generating PDF with reportlab: {e}")
            # Write a plain text fallback if PDF generator encounters library issues
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"CAREER VOICE REPORT - SESSION #{session_id}\n")
                f.write(f"Role: {session.role}\nOverall Score: {overall}%\n")
            return output_path

report_service = ReportService()
