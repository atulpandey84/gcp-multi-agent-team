# GCP Multi-Agent Engineering Team

LangGraph + NVIDIA multi-agent engineering organization.

## Model policy
- Nemotron Ultra: critical architecture/orchestration
- Nemotron Super: senior reasoning
- DeepSeek V4 Pro: coding/implementation
- Nemotron Lightning: fast routine work
- DeepSeek V4 Flash: fast coding
- Nemotron Embed/Rerank: RAG

## Safety defaults
GCP mutations, Terraform apply and production deployment are disabled by default.
Implement tool authorization and human approval before enabling them.

## Run
```bash
cp .env.example .env
# add NVIDIA_API_KEY
source .venv/bin/activate
make test
make run
```

Verify exact model identifiers against the current NVIDIA Build catalog before production deployment.
