# Automacao Gebras

## Docker (worker continuo)

Build da imagem:

```bash
docker build -t automacao-gebras .
```

Execucao local com variaveis do arquivo `.env`:

```bash
docker run --rm --env-file .env automacao-gebras
```

O container inicia o worker principal com:

```bash
python -m core.automacao_contrato
```
