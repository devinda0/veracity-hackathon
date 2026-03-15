# Agents

LangGraph orchestration scaffold implemented for Issue #7.

## Structure

- `orchestrator/`: graph factory, typed state, config, and placeholder nodes
- `domain_agents/`: domain-specific agent placeholders for M2 issues
- `messaging/`: A2A protocol primitives and message bus shell
- `tools/`: base tool contracts and helper module placeholders
- `utils/`: structured JSON logger and validation helpers

## Install

```bash
pip install -r requirements.txt
```

## Next Issues

- Issue #8: A2A message bus implementation
- Issue #9: base data source tool implementation
- Issue #13 onward: router and domain agent logic
