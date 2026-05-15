# AWS Cloud Practitioner CLI + Web Simulator

Este projeto é um simulador interativo para prática do exame AWS Certified Cloud Practitioner (CLF-C02).

O objetivo é auxiliar estudantes do exame AWS Cloud Practitioner CLF-C02 por meio de um simulador CLI fiel ao formato de prova e de uma nova interface Web leve e móvel-first.

Este projeto utiliza conteúdo de simulados derivados do repositório original de Marcelo Avelino: https://github.com/maclausk/AWS_Cloud_Practitioner_CLF-C02.

## Estrutura do projeto

- `prova.py`: script de entrada da aplicação CLI.
- `web/index.html`: interface Web autossuficiente com React e Tailwind via CDN.
- `utils/loader.py`: carrega e unifica questões JSON da pasta `simulados/`.
- `utils/engine.py`: lógica de sorteio, timer, pontuação e exportação CSV.
- `utils/ui.py`: renderização de CLI com cores usando `rich`.
- `requirements.txt`: dependências do projeto Python.
- `simulados/`: banco de dados de simulados em JSON.
- `web/manifest.json`: manifesto de simulados disponíveis para a interface Web.
- `reports/`: relatórios exportados em CSV pelo CLI.

## Uso CLI

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Execute o simulador Python:

```bash
python prova.py
```

3. O simulador carregará todos os arquivos JSON em `simulados/`, sorteará 65 questões e exportará um relatório em `reports/`.

## Uso Web

A interface Web está disponível em `web/index.html` e funciona com os arquivos JSON existentes em `simulados/`.

### Como abrir localmente

Como o navegador precisa fazer `fetch` nos arquivos JSON, abra o projeto via servidor HTTP local:

```bash
cd AWS_Cloud_Practitioner_CLF-C02
python -m http.server 8000
```

Em seguida, acesse:

```text
http://localhost:8000/web/
```

### Recursos da interface Web

- Seleção de simulado a partir de `web/manifest.json`.
- Timer regressivo de 90 minutos que persiste no `localStorage`.
- Suporte a questões de resposta única e múltipla resposta.
- Salva automaticamente estado de sessão, pergunta atual, respostas e tempo restante.
- Gera e baixa CSV de desempenho com histórico de respostas.
- Revisão de questões respondidas com explicações técnicas.

## GitHub Pages

Para publicar no GitHub Pages:

1. Envie `web/index.html`, `web/manifest.json`, e `simulados/` para o branch principal do repositório.
2. Nas configurações do repositório, habilite GitHub Pages apontando para o branch `main` e a pasta `/root`.
3. Acesse a URL de Pages que o GitHub fornecer.

> Observação: o Web App busca os arquivos JSON diretamente em `simulados/`, portanto a pasta deve estar presente no deploy.

## Compartilhamento de dados entre CLI e Web

Os dados JSON são compartilhados entre as versões CLI e Web.

- A versão CLI carrega os mesmos arquivos JSON em `simulados/` usando o Python.
- A versão Web faz `fetch` desses mesmos arquivos JSON no navegador.

Isso garante que o conteúdo do banco de questões seja o mesmo para ambas as interfaces.

## Exportação de resultados

### CLI

- O CLI exporta um relatório CSV automático para `reports/` ao final da prova.

### Web

- A interface Web gera um CSV para download com as colunas:
  - `ID`
  - `Pergunta`
  - `Status`
  - `Sua_Resposta`
  - `Resposta_Correta`

- O nome do arquivo contém o score final e o timestamp.

## Créditos

Este simulador referencia e agradece o autor original Marcelo Avelino pelo repositório e pelo material de questões utilizado como base: https://github.com/maclausk/AWS_Cloud_Practitioner_CLF-C02.
