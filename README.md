# incident-answer-api

## Quickstart

```sh
$ ollama run gemma3
$ git clone <repo name>
$ cd <repo name>
$ uv sync --locked
$ uv run uvicorn app.main:app --reload
```

## Local Live Test

```sh
$ curl http://127.0.0.1:8000/llm_request -d '{"text": "what hours are you open", "task": "answer_with_context"}' -H 'Content-Type: application/json'
```

## Tests

```sh
$ uv run pytest 
```

## API docs

- http://127.0.0.1:8000/docs for OpenAPI UI
- http://127.0.0.1:8000/redoc for Redoc UI
- htpp://127.0.0.1:8000/openapi.json for the schema