from __future__ import annotations

from pydantic import BaseModel, Field


class HubInstalacaoOut(BaseModel):
    codigo: int
    codigo_cliente: int
    identificacao: str = ""
    razao_social: str = ""
    cidade: str = ""
    uf: str = ""
    ativo: bool = True
    selecionada: bool = False


class HubInstalacoesOut(BaseModel):
    codigo_cliente: int
    codigos_instalacao_selecionados: list[int] = Field(default_factory=list)
    formato_pipedrive: str
    instalacoes: list[HubInstalacaoOut]
    codigos_nao_encontrados: list[int] = Field(default_factory=list)


class HubServicoCatalogoOut(BaseModel):
    codigo_servico: int
    chave: str
    nome: str
    sigla: str
    nome_pipe: str
    ordem_form: int


class HubServicosOut(BaseModel):
    servicos: list[HubServicoCatalogoOut]
