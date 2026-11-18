# CrewAI Automated Document Pipeline

**A multi-agent system built with CrewAI that takes a topic from the user, researches it on the web and produces a formatted PDF report.**

> **Context.** Built in June 2025 as a coursework project at UPV (the report calls it a "práctica" and is signed by two students), when I was in the middle of my Computer Engineering degree and just starting to publish on GitHub. It is kept as it was submitted; the code is not maintained. It was my first contact with agent frameworks, an interest that later shaped the LLM and RAG work in my newer repositories.

## What it does

- Asks for a topic on the command line.
- Runs four CrewAI agents in sequence: researcher, analyst, verifier and formatter.
- Uses web search (`SerperDevTool`) and page scraping (`ScrapeWebsiteTool`) to ground the research.
- Writes the analyst's report to `archivo.txt` and renders it as `documento_final.pdf` with ReportLab, with a cover, footer and date.
- Plots the flow graph to `flujo_documento.png` (the repo contains the interactive HTML version, `flujo_documento.png.html`).

## How it works

`flujo_investigador.py` defines a `DocumentFlow` (a CrewAI `Flow`) with a `DocumentState` that holds the topic and the intermediate results. Each step is a separate sequential `Crew` with one agent and one task:

1. `realizar_investigacion`: the researcher gathers and synthesizes information on the topic.
2. `redactar_analisis`: the analyst turns that research into a structured report.
3. `verificar_documento`: the verifier audits the report for accuracy, sources and clarity.
4. `generar_documento_final`: the formatter prepares the final text.
5. `guardar_documento`: the analyst's report is saved to `archivo.txt`, Markdown markers are cleaned (`limpiar_txt_markdown`) and `generar_pdf` builds the PDF.

Note that the saved text is the analyst's output; the verifier's and formatter's outputs are printed but not written to the PDF. The accompanying memo (`Memoria CrewAI.pdf`, in Spanish) labels the formatting step "Conceptual". The LLM is `openai/qwen3:4b`, served through the university's OpenAI-compatible endpoint (`api.poligpt.upv.es`).

## Results

The repo includes one sample run, `documento_final.pdf` (3 pages, "Informe Práctica 2", dated 1 June 2025), a report titled "Análisis Técnico de CrewAI: Un Marco para la Automatización Autónoma de Sistemas Inteligentes". No metrics are reported. The memo notes that the scrape tool can occasionally fail for external reasons and that the agent then usually tries another page.

## Run it

Not re-run for this README; the commands are inferred from the imports and entry point.

```bash
pip install crewai crewai-tools reportlab python-dotenv pydantic
```

The script sets `OPENAI_API_KEY`, `SERPER_API_KEY` and the LLM `api_key` to `XXXX...` placeholders in the source. Replace them with your own keys (and change `base_url`/`model` if you do not have access to the UPV endpoint) before running:

```bash
python flujo_investigador.py
```

Enter a topic when prompted (the prompt appears a second time before the graph is plotted, because `plot()` builds a new flow state). The run writes `archivo.txt` and `documento_final.pdf`, then `flujo_documento.png`.

## Repository layout

```
flujo_investigador.py        agents, tasks, flow, text cleanup and PDF generation
archivo.txt                  sample report text
documento_final.pdf          sample generated PDF
flujo_documento.png.html     interactive plot of the flow
Memoria CrewAI.pdf           course memo (Spanish): design and requirements
```

## Stack

Python, CrewAI (agents and flows), crewai-tools (Serper, web scraping), ReportLab, Pydantic, python-dotenv, an OpenAI-compatible LLM endpoint.
