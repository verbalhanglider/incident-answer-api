# incident-answer-api

## Quickstart

### Dependencies

- [docker desktop](https://www.docker.com/products/docker-desktop/)
- [kind](https://kind.sigs.k8s.io/)

# With Kubernetes Quickstart

```sh
git clone <repo>
cd <repo>

# 1. Create kind cluster
kind create cluster --name incident-answer-api-dev

# 2. Build app image
docker compose build incident-answer-api

# 3. Load image into kind
kind load docker-image incident-answer-api:latest --name incident-dev

# 4. Apply K8s manifests (Deployment + Services)
kubectl apply -f k8s/ollama-deployment.yaml
kubectl apply -f k8s/ollama-service.yaml
kubectl apply -f k8s/incident-answer-api-deployment.yaml
kubectl apply -f k8s/api-service.yaml

# 5. Wait for pods to be ready
kubectl get pods
kubectl rollout status deployment/ollama
kubectl rollout status deployment/llm-incident-answer-api

# 6. Port-forward API to localhost
kubectl port-forward svc/llm-incident-answer-api 8000:8000
```

No Kubernetes Quickstart

```sh
$ git clone <repo name>
$ cd <repo name>
$ ollama run gemma3
$ uv sync --locked
$ ollama run gemma3 
$ docker run --name my-postgres -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres -v my_pgdata:/var/lib/postgresql/data
$ uv run uvicorn app.main:app --reload --log-config uvicorn_logging_config.json
```

Or via Docker

```sh
$ docker build -t fastapi-llm-incident-answer-api .
$ docker  run --rm -p 8000:8000 fastapi-llm-incident-answer-api
$ docker run -it --entrypoint /bin/bash fastapi-llm-demo # to debug container issues
```
## Local Live Test

```sh
$ curl http://127.0.0.1:8000/sre_api/extract -d '{"text": "what hours are you open"}' -H 'Content-Type: application/json'
$ curl http://127.0.0.1:8000/sre_api/classify -d '{"text": "what hours are you open"}' -H 'Content-Type: application/json'
$ curl http://127.0.0.1:8000/sre_api/answer/context -d '{"text": "what hours are you open"}
```

## Tests

```sh
$ uv run pytest 
```

## API docs

- http://127.0.0.1:8000/docs for OpenAPI UI
- http://127.0.0.1:8000/redoc for Redoc UI
- htpp://127.0.0.1:8000/openapi.json for the schema