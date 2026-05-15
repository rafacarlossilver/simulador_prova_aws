from __future__ import annotations

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def format_duration(seconds: float) -> str:
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"


def render_welcome(title: str, total_questions: int) -> None:
    console.clear()
    console.rule("[bold green]Simulador AWS Certified Cloud Practitioner (CLF-C02)[/]")
    console.print(
        Panel(
            f"[bold]Título do simulado:[/] {title}\n"
            f"[bold]Total de questões:[/] {total_questions}\n"
            f"[bold]Tempo total:[/] 90 minutos\n"
            f"[bold]Pontuação de aprovação:[/] 700 pontos\n",
            title="Instruções",
            border_style="blue",
        )
    )


def render_header(title: str, current: int, total: int, remaining_seconds: float) -> None:
    header_text = (
        f"[bold green]{title}[/] • Questão [bold]{current}/{total}[/] • "
        f"Tempo restante: [bold yellow]{format_duration(remaining_seconds)}[/]"
    )
    console.rule(header_text)


def render_question(question) -> None:
    console.print(Text(question.pergunta, style="bold white"))
    table = Table(show_header=False, box=None)
    table.add_column("Letra", style="bold cyan", width=6)
    table.add_column("Descrição")

    for key, value in sorted(question.opcoes.items()):
        table.add_row(key.upper(), value)

    console.print(table)
    if len(question.resposta_correta) > 1:
        console.print(
            "[magenta]Questão de múltipla resposta. Informe as alternativas separadas por vírgula ou espaço.[/]")


def show_invalid_input(message: str) -> None:
    console.print(f"[red]Entrada inválida:[/] {message}")


def show_saved_progress(state) -> None:
    console.print(
        Panel(
            f"Progresso salvo encontrado. \nQuestões respondidas: [bold]{len(state.responses)}[/] de [bold]{state.total_questions}[/]."
            f"\nTempo restante estimado: [bold yellow]{format_duration(state.remaining_seconds())}[/]",
            title="Retomar sessão",
            border_style="yellow",
        )
    )


def show_time_expired() -> None:
    console.print("\n[bold red]O tempo expirou. A prova foi encerrada automaticamente.[/]")


def render_summary(score: int, passed: bool, correct_count: int, total_questions: int, remaining_seconds: float) -> None:
    outcome = "APROVADO" if passed else "NÃO APROVADO"
    color = "green" if passed else "red"
    percentage = 0 if total_questions == 0 else (correct_count / total_questions) * 100

    summary = Table(show_header=False, box=None)
    summary.add_column("Campo", style="bold cyan")
    summary.add_column("Resultado")
    summary.add_row("Pontuação", f"[bold]{score}[/]")
    summary.add_row("Resultado", f"[{color}]{outcome}[/{color}]")
    summary.add_row("Acertos", f"{correct_count}/{total_questions}")
    summary.add_row("Percentual", f"{percentage:.1f}%")
    summary.add_row("Tempo restante", f"{format_duration(remaining_seconds)}")

    console.print(Panel(summary, title="Resumo final", border_style=color))


def render_error_list(state) -> None:
    incorrect = [
        state.questions[qid]
        for qid in state.question_ids
        if not state.is_correct(qid)
    ]

    if not incorrect:
        console.print("[bold green]Parabéns! Todas as questões foram respondidas corretamente.[/]")
        return

    console.print("\n[bold yellow]Questões incorretas:[/]")
    for question in incorrect:
        user_answer = ";".join(answer.upper() for answer in state.responses.get(question.id, []))
        correct_answer = ";".join(answer.upper() for answer in question.resposta_correta)

        panel = Panel(
            f"[bold]Questão {question.id}[/]\n"
            f"[bold white]Sua resposta:[/] {user_answer or 'Nenhuma'}\n"
            f"[bold white]Resposta correta:[/] {correct_answer}\n\n"
            f"[bold]Explicação:[/]\n{question.explicacao}",
            border_style="red",
        )
        console.print(panel)


def render_report_exported(report_path: Path) -> None:
    console.print(
        Panel(
            f"Relatório CSV exportado para:\n[bold]{report_path}[/]",
            title="Relatório gerado",
            border_style="green",
        )
    )
