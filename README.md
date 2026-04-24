# ConsensusGraph

`ConsensusGraph` is currently a small CLI prototype for generating a balanced answer to a question by explicitly running two research passes:

- a `pro` pass that argues in favor of the topic
- a `con` pass that argues against it
- a final synthesis pass that summarizes both sides and gives a recommendation

Today, the app uses:

- `LangGraph` to orchestrate the flow
- `OpenRouter` for the model call
- `Tavily` for web search
- a persistent `AsyncSqliteSaver` checkpointer backed by a local SQLite database

## Current State

What works now:

- You enter a debate topic or decision prompt in the terminal.
- A planner creates one focused prompt for each side plus search topics.
- The app searches the web for each side separately.
- The model produces a pro argument, a con argument, and a final balanced answer.

What this is not yet:

- not a visual graph UI yet
- not a multi-user server yet
- not a citation-heavy research report yet
- not a multi-turn debate system yet

## Setup

This project expects:

- Python `3.13+`
- `uv` for dependency management

The application loads all configuration from a `.env` file in the project root. An `.env.example` template is included in the repo with every available variable documented and commented.

### Creating Your `.env` File

1. Run `uv sync` from the repo root to install dependencies.
2. Copy the example file:

   ```bash
   cp .env.example .env
   ```

3. Open `.env` in your editor and fill in your API keys. The file is self-documenting — each variable has an inline comment explaining what it does and where to get it.

4. **Important:** Never commit your `.env` file to version control. It is already listed in `.gitignore`.

### Environment Variables Reference

| Variable | Required | Purpose |
|---|---|---|
| `OPENROUTER_API_KEY` | Yes | Authenticates LLM calls via OpenRouter |
| `TAVILY_API_KEY` | Yes | Enables web search for research agents |
| `DEFAULT_MODEL_NAME` | No | Override the default LLM model (default: `moonshotai/kimi-k2.6`) |
| `LANGSMITH_TRACING` | No | Master switch for LangSmith tracing (`true`/`false`) |
| `LANGSMITH_API_KEY` | No | LangSmith authentication (only needed if tracing is enabled) |
| `LANGSMITH_PROJECT` | No | Project name in the LangSmith dashboard (default: `consensusgraph`) |

### Configuring the Model

The LLM is used for every step of the graph (planning, research, rebuttal, and synthesis). By default the app uses `moonshotai/kimi-k2.6`. You can override this by setting `DEFAULT_MODEL_NAME` in your `.env` file:

```env
DEFAULT_MODEL_NAME=anthropic/claude-sonnet-4-20250514
```

Any model identifier supported by OpenRouter will work. Some good alternatives:
- `openai/gpt-4o`
- `anthropic/claude-sonnet-4-20250514`
- `google/gemini-2.5-pro-preview`
- `mistralai/mistral-large-2`

If `DEFAULT_MODEL_NAME` is not set or is empty, the built-in default (`moonshotai/kimi-k2.6`) is used.

## LangSmith Tracing Setup

LangSmith is LangChain's observability platform that helps you trace, debug, and monitor LLM applications. It captures every LLM call, including prompts, responses, costs, and latency.

### Why Use LangSmith?

- **Debugging:** See exactly what the agent did at each step
- **Performance Monitoring:** Track token usage, costs, and response times
- **Reproducibility:** Review past runs for analysis and iteration
- **Multi-Agent Visibility:** Trace the entire agentic workflow from planning through search to synthesis

### How It Works in This App

When tracing is enabled (`LANGSMITH_TRACING=true`):

- **Every LLM call is captured** with full prompts and responses
- **Automatic metadata** is attached to each run: `{"model": "...", "langsmith_tracing": true}`
- **Automatic tags** are added: `["langsmith:nostream"]` for consistent filtering
- **Callbacks run asynchronously** in background threads for better performance

### Insights & Tips

1. **Enable tracing early** - Start with tracing ON during development to understand agent behavior. You can disable it in production if needed.

2. **Understand token costs** - LangSmith shows tokens used per run. For multi-agent apps like this, expect multiple LLM calls per question (planning, pro research, con research, synthesis).

3. **Use the dashboard** - At https://smith.langchain.com/?project=consensusgraph, you can:
   - Browse runs by date, tags, or metadata
   - Compare different runs side-by-side
   - Filter by specific agents or steps

4. **Streaming is disabled** - The `langsmith:nostream` tag disables streaming to ensure complete traces for debugging purposes. This is a best practice for observability.

5. **Performance impact** - Tracing adds minimal overhead since callbacks run in background threads. You won't notice a difference in app responsiveness.

6. **Security** - API keys are never logged in traces - only usage metadata and prompts/responses. Your `.env` file stays private.

### Quick Start

1. **Sign up at LangSmith:** Visit https://smith.langchain.com/settings to get your API key.
2. **Set environment variables:** Add `LANGSMITH_TRACING=true` and your API key to `.env`.
3. **Run the app:** You'll see "> LangSmith Tracing: ON" in the startup summary.
4. **View your traces:** Visit https://smith.langchain.com/?project=consensusgraph to see your first runs.

## Running the App

From the repo root:

```bash
cd ~/ConsensusGraph
uv run python app.py
```

You will see a startup configuration summary, for example:

```text
> Configuration Summary:
>   Model: openrouter/moonshotai/kimi-k2.6
>   OpenRouter API key: Present
>   Tavily API key: Present
>   LangSmith Tracing: ON
>   Tracing Dashboard: https://smith.langchain.com/?project=consensusgraph
```

You will then be prompted for a topic, for example:

```text
Should schools ban smartphones in classrooms?
```

If you press Enter without typing anything, the app uses that question as the default.

## Notes

- The default model (`moonshotai/kimi-k2.6`) can be overridden with `DEFAULT_MODEL_NAME` in `.env`.
- The Tavily key is required at startup; the app raises an error if it is missing.
- Graph state is persisted across runs in `consensusgraph.db` (SQLite).
- All configuration is validated at startup with a helpful summary printed to the console.
- The app uses LangGraph for stateful multi-step orchestration with automatic thread ID generation for each session.
