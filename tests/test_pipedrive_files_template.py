"""Testes unitários: seleção de template `contrato_padrao%` nos arquivos do deal."""

from __future__ import annotations

from core.pipedrive_files import escolher_docx_contrato_padrao


def test_escolhe_por_prefixo_contrato_padrao():
    arquivos = [
        {"id": 1, "file_type": "docx", "name": "x-contrato_padrao.docx", "add_time": "2026-05-01 10:00:00"},
        {"id": 2, "file_type": "docx", "name": "contrato_padrao - Copia.docx", "add_time": "2026-05-02 10:00:00"},
        {"id": 3, "file_type": "pdf", "name": "contrato_padrao.pdf", "update_time": "2026-05-03 10:00:00"},
    ]
    escolhido = escolher_docx_contrato_padrao(arquivos)
    assert escolhido is not None
    assert escolhido["id"] == 2


def test_escolhe_mais_recente_quando_multiplos_prefixos():
    arquivos = [
        {"id": 10, "file_type": "docx", "name": "contrato_padrao.docx", "add_time": "2026-05-01 10:00:00"},
        {"id": 11, "file_type": "docx", "name": "Contrato_Padrao2.docx", "add_time": "2026-05-03 10:00:00"},
        {"id": 12, "file_type": "docx", "name": "contrato_padrao - Copia.docx", "add_time": "2026-05-02 10:00:00"},
    ]
    escolhido = escolher_docx_contrato_padrao(arquivos)
    assert escolhido is not None
    assert escolhido["id"] == 11


def test_escolhe_ultimo_envio_mesmo_nome_mesmo_prefixo():
    """update_time antigo não deve vencer add_time de upload mais recente."""
    arquivos = [
        {
            "id": 100,
            "file_type": "docx",
            "name": "contrato_padrao.docx",
            "add_time": "2026-05-29 11:17:00",
            "update_time": "2026-05-29 11:55:00",
        },
        {
            "id": 101,
            "file_type": "docx",
            "name": "contrato_padrao.docx",
            "add_time": "2026-05-29 11:50:00",
            "update_time": "2026-05-29 11:50:00",
        },
    ]
    escolhido = escolher_docx_contrato_padrao(arquivos)
    assert escolhido is not None
    assert escolhido["id"] == 101


def test_sem_prefixo_retorna_none():
    arquivos = [
        {"id": 1, "file_type": "docx", "name": "modelo_contrato.docx"},
        {"id": 2, "file_type": "docx", "name": "x-contrato_padrao.docx"},
    ]
    assert escolher_docx_contrato_padrao(arquivos) is None

