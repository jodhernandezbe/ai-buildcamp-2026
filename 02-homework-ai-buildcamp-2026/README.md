# Homework 2 (Week 3): AI Engineering Buildcamp - Wikipedia Agent

This folder contains the second homework, which belongs to the third week of the
course. The goal is to build an agent that answers questions by searching Wikipedia and reading
page content. It uses LangChain as the framework and OpenAI as the inference
provider.

## Structure

```
02-homework-ai-buildcamp-2026/
  tools/
    wikipedia/
      wikipedia_client.py    shared HTTP helper (URLs, User-Agent, timeout)
      search_wikipedia.py    search for pages related to a query
      get_page.py            fetch the raw content of a page
  agent/
    config.py                AgentConfig: model, temperature, prompt name
    models.py                builds the chat model from "<provider>:<model>"
    tool_registry.py         wraps the plain tool functions as LangChain tools
    prompts/
      registry.py            loads versioned prompts from Markdown files
      templates/
        wikipedia_agent.md   system prompt
    agent.py                 build_agent(): assembles model, tools, and prompt
  homework.py                prints the answer to each homework question
```

## Design notes

- **Tools stay framework-agnostic.** The functions in `tools/` are plain Python
  with typed docstrings. Only `agent/tool_registry.py` imports LangChain; it
  builds each tool's name, description, and schema from the function's docstring.
  To add a tool, write the function and list it in `WIKIPEDIA_TOOLS`.
- **Swapping provider is a config change.** The model is a
  `"<provider>:<model>"` string (default `openai:gpt-4o-mini`), set with the
  `AGENT_MODEL` environment variable. For example, `anthropic:...` works after
  installing `langchain-anthropic`.
- **Prompts live in Markdown.** `PromptRegistry` loads `.md` files with `version`
  and `description` front matter. Variables are written as `$name` (the agent
  fills in `$today`).
- **Everything is injectable.** `build_agent(model=, tools=, config=, prompts=)`
  accepts replacements, so tests can use a fake model.

## Usage

Requires `OPENAI_API_KEY` in the environment.

```
python homework.py [-q {1,2,3,5,6,all}]
```

- `-q, --question` (optional, default `all`): which question to answer.

| Question | What it answers |
|----------|-----------------|
| 1 | Total results for the query `capybara` |
| 2 | Results with `capybara` in the title (case-insensitive) |
| 3 | Characters in the `Capybara` page |
| 5 | Agent: what is the Capybara page about? |
| 6 | Agent: main threats to capybara populations (tool calls and answer) |

Example:
```
python homework.py -q 3
python homework.py
```

Questions 5 and 6 call an LLM and Wikipedia, so their answers and tool-call
counts can differ slightly from run to run.
