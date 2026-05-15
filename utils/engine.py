from __future__ import annotations

import csv
import json
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from utils.loader import Question

TEMPO_TOTAL_SEGUNDOS = 90 * 60


@dataclass
class ExamState:
    title: str
    question_ids: List[int]
    questions: Dict[int, Question]
    current_index: int = 0
    responses: Dict[int, List[str]] = field(default_factory=dict)
    start_timestamp: float = field(default_factory=time.monotonic)
    elapsed_seconds: float = 0.0

    @property
    def total_questions(self) -> int:
        return len(self.question_ids)

    def current_question(self) -> Optional[Question]:
        if self.current_index >= self.total_questions:
            return None
        return self.questions[self.question_ids[self.current_index]]

    def remaining_seconds(self) -> float:
        return max(0.0, TEMPO_TOTAL_SEGUNDOS - self.elapsed_seconds)

    def is_correct(self, question_id: int) -> bool:
        question = self.questions.get(question_id)
        response = self.responses.get(question_id, [])
        if question is None:
            return False
        return set(response) == set(question.resposta_correta)


def select_questions(questions: List[Question], count: int = 65) -> ExamState:
    selected = random.sample(questions, min(count, len(questions)))
    questions_by_id = {question.id: question for question in selected}
    title = selected[0].source if selected else "AWS Cloud Practitioner"
    return ExamState(title=title, question_ids=[question.id for question in selected], questions=questions_by_id)


def score_exam(correct_answers: int, total_questions: int) -> int:
    if total_questions <= 0:
        return 100
    percentage = correct_answers / total_questions
    return int(round(100 + percentage * 900))


def export_report(state: ExamState, report_folder: Path) -> Path:
    report_folder.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = report_folder / f"resultado_{timestamp}.csv"

    with filename.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "ID da Questão",
            "Status",
            "Resposta do Usuário",
            "Resposta Correta",
            "Explicação",
        ])

        for question_id in state.question_ids:
            question = state.questions[question_id]
            user_answer = state.responses.get(question_id, [])
            status = "Acerto" if state.is_correct(question_id) else "Erro"
            writer.writerow(
                [
                    question.id,
                    status,
                    ";".join(answer.upper() for answer in user_answer),
                    ";".join(answer.upper() for answer in question.resposta_correta),
                    question.explicacao,
                ]
            )

    return filename


def save_session(state: ExamState, session_path: Path) -> None:
    session_data = {
        "title": state.title,
        "question_ids": state.question_ids,
        "current_index": state.current_index,
        "responses": {str(qid): answers for qid, answers in state.responses.items()},
        "elapsed_seconds": state.elapsed_seconds,
        "saved_at": datetime.now().isoformat(),
    }
    session_path.write_text(json.dumps(session_data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_session(session_path: Path, available_questions: List[Question]) -> Optional[ExamState]:
    if not session_path.exists():
        return None

    raw = json.loads(session_path.read_text(encoding="utf-8"))
    question_ids = [int(item) for item in raw.get("question_ids", []) if item is not None]
    responses = {
        int(k): [str(answer).strip().lower() for answer in v]
        for k, v in raw.get("responses", {}).items()
        if isinstance(v, list)
    }

    questions_by_id = {question.id: question for question in available_questions if question.id in question_ids}
    filtered_ids = [qid for qid in question_ids if qid in questions_by_id]

    if not filtered_ids:
        return None

    state = ExamState(
        title=str(raw.get("title", "AWS Cloud Practitioner")),
        question_ids=filtered_ids,
        questions=questions_by_id,
        current_index=int(raw.get("current_index", 0)),
        responses=responses,
        elapsed_seconds=float(raw.get("elapsed_seconds", 0.0)),
    )
    state.start_timestamp = time.monotonic() - state.elapsed_seconds
    return state


def delete_state_file(session_path: Path) -> None:
    if session_path.exists():
        try:
            session_path.unlink()
        except OSError:
            pass
