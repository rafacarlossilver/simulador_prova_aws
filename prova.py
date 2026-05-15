from __future__ import annotations

import sys
import time
from pathlib import Path

from utils.engine import (
    TEMPO_TOTAL_SEGUNDOS,
    ExamState,
    delete_state_file,
    export_report,
    load_session,
    save_session,
    score_exam,
    select_questions,
)
from utils.loader import load_questions
from utils.ui import (
    console,
    render_error_list,
    render_header,
    render_question,
    render_report_exported,
    render_summary,
    render_welcome,
    show_invalid_input,
    show_saved_progress,
    show_time_expired,
)


def parse_answer(raw_input: str, valid_choices: set[str], required_count: int) -> list[str] | None:
    if not raw_input:
        show_invalid_input("Digite uma ou mais alternativas válidas.")
        return None

    normalized = raw_input.strip().lower().replace(",", " ")
    tokens = [token.strip() for token in normalized.split() if token.strip()]
    if len(tokens) == 1 and len(tokens[0]) > 1:
        tokens = list(tokens[0])

    answers: list[str] = []
    for token in tokens:
        if token not in valid_choices:
            show_invalid_input(f"Alternativa inválida: '{token}'. Use apenas {', '.join(sorted(valid_choices)).upper()}.")
            return None
        if token in answers:
            continue
        answers.append(token)

    if len(answers) != required_count:
        show_invalid_input(f"Esta questão exige {required_count} alternativa(s). Você enviou {len(answers)}.")
        return None

    return sorted(answers)


def ask_resume(session_path: Path) -> bool:
    while True:
        answer = console.input("Deseja retomar a sessão anterior? ([bold]s[/]/n): ").strip().lower()
        if answer in {"s", "sim", "y", "yes", ""}:
            return True
        if answer in {"n", "nao", "não", "no"}:
            return False
        show_invalid_input("Responda com 's' ou 'n'.")


def run_exam() -> int:
    root_dir = Path(__file__).resolve().parent
    simulados_dir = root_dir / "simulados"
    reports_dir = root_dir / "reports"
    reports_dir.mkdir(exist_ok=True)

    try:
        all_questions = load_questions(simulados_dir)
    except Exception as exc:
        console.print(f"[red]Falha ao carregar questões:[/] {exc}")
        return 1

    if not all_questions:
        console.print("[red]Nenhuma questão encontrada na pasta simulados/. Verifique os arquivos JSON.[/]")
        return 1

    session_path = root_dir / ".session_progress.json"
    state = None
    if session_path.exists():
        if ask_resume(session_path):
            state = load_session(session_path, all_questions)
            if state:
                show_saved_progress(state)
            else:
                console.print("[yellow]Não foi possível retomar a sessão. Iniciando novo simulado.[/]")

    if not state:
        state = select_questions(all_questions, count=65)

    render_welcome(state.title, state.total_questions)
    state.start_timestamp = time.monotonic() - state.elapsed_seconds

    try:
        while state.current_index < state.total_questions and state.remaining_seconds() > 0:
            question = state.current_question()
            if question is None:
                break

            render_header(state.title, state.current_index + 1, state.total_questions, state.remaining_seconds())
            render_question(question)

            valid_choices = set(question.opcoes.keys())
            required_count = len(question.resposta_correta) or 1

            answer = None
            while answer is None and state.remaining_seconds() > 0:
                raw = console.input("[bold blue]Sua resposta[/]> ")
                answer = parse_answer(raw, valid_choices, required_count)
                state.elapsed_seconds = time.monotonic() - state.start_timestamp

            if state.remaining_seconds() <= 0:
                break

            state.responses[question.id] = answer
            state.current_index += 1
            state.elapsed_seconds = time.monotonic() - state.start_timestamp
            save_session(state, session_path)

        if state.remaining_seconds() <= 0:
            show_time_expired()

        correct_count = sum(1 for qid in state.question_ids if qid in state.responses and state.is_correct(qid))
        total = state.total_questions
        score_value = score_exam(correct_count, total)
        passed = score_value >= 700

        report_path = export_report(state, reports_dir)
        render_summary(score_value, passed, correct_count, total, state.remaining_seconds())
        render_error_list(state)
        render_report_exported(report_path)

        delete_state_file(session_path)
        return 0
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Sessão interrompida. Salvando progresso...[/]")
        save_session(state, session_path)
        return 0


if __name__ == "__main__":
    raise SystemExit(run_exam())
