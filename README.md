# ConsensusGraph

`ConsensusGraph` is currently a small CLI prototype for generating a balanced answer to a question by explicitly running two research passes:

- a `pro` pass that argues in favor of the topic
- a `con` pass that argues against it
- a final synthesis pass that summarizes both sides and gives a recommendation

Today, the app uses:

- `LangGraph` to orchestrate the flow
- `OpenRouter` for the model call
- `Tavily` for web search
- an in-memory checkpoint saver for the current process

## Current State

What works now:

- You enter a debate topic or decision prompt in the terminal.
- A planner creates one focused prompt for each side plus search topics.
- The app searches the web for each side separately.
- The model produces a pro argument, a con argument, and a final balanced answer.

What this is not yet:

- not a visual graph UI yet
- not a persistent database-backed app yet
- not a citation-heavy research report yet
- not a multi-turn debate system yet

## Setup

This project expects:

- Python `3.13+`
- an `OPENROUTER_API_KEY`
- a `TAVILY_API_KEY` or `TAVILY_SEARCH_KEY`
- `uv` for dependency management

Use this from the repo root:

```bash
cd ~/ConsensusGraph

uv sync

cat > .env <<'EOF'
OPENROUTER_API_KEY=your_openrouter_key_here
TAVILY_API_KEY=your_tavily_key_here
EOF
```

## Run

```bash
cd ~/ConsensusGraph
uv run python app.py
```

You will be prompted for a topic, for example:

```text
Should schools ban smartphones in classrooms?
```

If you press Enter without typing anything, the app uses that question as the default.

## Notes

- The model is currently hard-coded in `app.py` as `moonshotai/kimi-k2.6`.
- The Tavily key is required at startup; the app raises an error if it is missing.
- State is only kept in memory for the current run.
