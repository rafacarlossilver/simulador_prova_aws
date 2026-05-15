from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class Question:
    id: int
    pergunta: str
    opcoes: Dict[str, str]
    resposta_correta: List[str]
    explicacao: str
    source: str


def load_questions(simulados_dir: Path) -> List[Question]:
    if not simulados_dir.exists() or not simulados_dir.is_dir():
        raise FileNotFoundError(f"O diretório {simulados_dir} não existe.")

    questions: List[Question] = []
    seen_ids: set[int] = set()
    json_files = sorted(simulados_dir.glob("*.json"))

    if not json_files:
        raise FileNotFoundError("Nenhum arquivo JSON encontrado na pasta simulados/.")

    for json_path in json_files:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        source_name = data.get("titulo", json_path.stem)
        raw_questions = data.get("questoes", [])

        if not isinstance(raw_questions, list):
            continue

        for raw in raw_questions:
            if not isinstance(raw, dict):
                continue

            qid = raw.get("id")
            if qid is None or not isinstance(qid, int):
                continue

            if qid in seen_ids:
                continue
            seen_ids.add(qid)

            pergunta = str(raw.get("pergunta", "")).strip()
            opcoes = raw.get("opcoes", {}) or {}
            resposta_correta = raw.get("resposta_correta", []) or []
            explicacao = str(raw.get("explicacao", "")).strip()

            if isinstance(resposta_correta, str):
                resposta_correta = [resposta_correta]

            normalized_opcoes: Dict[str, str] = {}
            for key, text in opcoes.items():
                if not isinstance(key, str):
                    continue
                normalized_opcoes[key.strip().lower()] = str(text).strip()

            normalized_correct = [str(item).strip().lower() for item in resposta_correta if item is not None]
            normalized_correct = sorted(set(normalized_correct))

            questions.append(
                Question(
                    id=qid,
                    pergunta=pergunta,
                    opcoes=normalized_opcoes,
                    resposta_correta=normalized_correct,
                    explicacao=explicacao,
                    source=source_name,
                )
            )

    return questions
