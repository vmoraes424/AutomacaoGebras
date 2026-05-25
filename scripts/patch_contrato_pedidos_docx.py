"""Insere placeholder dos números de pedido Plune na 3ª linha do cabeçalho do contrato."""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "contrato_padrao.docx"

ROW3_EMPTY = (
    '<w:p w14:paraId="2E5C32FE" w14:textId="45B8CB92" w:rsidR="002358F9" '
    'w:rsidRPr="008A161E" w:rsidRDefault="002358F9" w:rsidP="0E26E280">'
    "<w:pPr><w:jc w:val=\"both\"/><w:rPr><w:rFonts w:asciiTheme=\"minorHAnsi\" "
    "w:hAnsiTheme=\"minorHAnsi\" w:cstheme=\"minorBidi\"/><w:b/><w:bCs/></w:rPr></w:pPr></w:p>"
)

ROW3_PEDIDOS = (
    '<w:p w14:paraId="2E5C32FE" w14:textId="45B8CB92" w:rsidR="002358F9" '
    'w:rsidRPr="008A161E" w:rsidRDefault="002358F9" w:rsidP="0E26E280">'
    "<w:pPr><w:jc w:val=\"both\"/><w:rPr><w:rFonts w:asciiTheme=\"minorHAnsi\" "
    "w:hAnsiTheme=\"minorHAnsi\" w:cstheme=\"minorBidi\"/><w:b/><w:bCs/></w:rPr></w:pPr>"
    "<w:r w:rsidRPr=\"008A161E\"><w:rPr><w:rFonts w:asciiTheme=\"minorHAnsi\" "
    "w:hAnsiTheme=\"minorHAnsi\" w:cstheme=\"minorBidi\"/><w:b/><w:bCs/></w:rPr>"
    "<w:t xml:space=\"preserve\">N\u00ba Pedidos Plune: </w:t></w:r>"
    "<w:r w:rsidR=\"000D3DDE\" w:rsidRPr=\"000D3DDE\"><w:rPr><w:rFonts w:asciiTheme=\"minorHAnsi\" "
    "w:hAnsiTheme=\"minorHAnsi\" w:cstheme=\"minorBidi\"/><w:b/><w:bCs/></w:rPr>"
    "<w:t>{{ numeros_pedidos }}</w:t></w:r></w:p>"
)


def main() -> None:
    with zipfile.ZipFile(DOCX, "r") as zin:
        xml = zin.read("word/document.xml").decode("utf-8")

    if "{{ numeros_pedidos }}" in xml:
        print("Placeholder numeros_pedidos já presente; nada a fazer.")
        return

    if ROW3_EMPTY not in xml:
        raise SystemExit("Linha 3 vazia do cabeçalho não encontrada; revise o template.")

    xml = xml.replace(ROW3_EMPTY, ROW3_PEDIDOS, 1)

    tmp = Path(tempfile.mkdtemp()) / "contrato_patch.docx"
    with zipfile.ZipFile(DOCX, "r") as zin, zipfile.ZipFile(tmp, "w") as zout:
        for item in zin.infolist():
            data = (
                xml.encode("utf-8")
                if item.filename == "word/document.xml"
                else zin.read(item.filename)
            )
            zout.writestr(item, data)
    shutil.copy(tmp, DOCX)
    print(f"Atualizado: {DOCX}")


if __name__ == "__main__":
    main()
