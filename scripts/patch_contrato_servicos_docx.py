"""Insere placeholders Jinja para Gestão ACL e Usina no contrato_padrao.docx."""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "contrato_padrao.docx"

ACL_ANCHOR = (
    'w14:paraId="34F3E406" w14:textId="26510CB7" w:rsidR="00F64BAD" '
    'w:rsidRPr="000D3DDE" w:rsidRDefault="623CE0AE" w:rsidP="011C7467">'
    '<w:pPr><w:jc w:val="center"/><w:rPr><w:rFonts w:asciiTheme="minorHAnsi" '
    'w:hAnsiTheme="minorHAnsi" w:cstheme="minorBidi"/><w:sz w:val="18"/>'
    '<w:szCs w:val="18"/></w:rPr></w:pPr><w:r w:rsidRPr="000D3DDE"><w:rPr>'
    '<w:rFonts w:asciiTheme="minorHAnsi" w:hAnsiTheme="minorHAnsi" '
    'w:cstheme="minorBidi"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'
    "<w:t>-</w:t></w:r></w:p></w:tc></w:tr><w:tr w:rsidR=\"008B6FD8\""
)

USINA_ANCHOR = (
    'w14:paraId="0B2E23D6" w14:textId="17FE067D" w:rsidR="008B6FD8" '
    'w:rsidRPr="000D3DDE" w:rsidRDefault="008B6FD8" w:rsidP="008B6FD8">'
    '<w:pPr><w:jc w:val="center"/><w:rPr><w:rFonts w:asciiTheme="minorHAnsi" '
    'w:hAnsiTheme="minorHAnsi" w:cstheme="minorBidi"/><w:sz w:val="18"/>'
    '<w:szCs w:val="18"/></w:rPr></w:pPr><w:r w:rsidRPr="000D3DDE"><w:rPr>'
    '<w:rFonts w:asciiTheme="minorHAnsi" w:hAnsiTheme="minorHAnsi" '
    'w:cstheme="minorBidi"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'
    "<w:t>-</w:t></w:r></w:p></w:tc></w:tr><w:tr w:rsidR=\"008B6FD8\""
)


def main() -> None:
    with zipfile.ZipFile(DOCX, "r") as zin:
        xml = zin.read("word/document.xml").decode("utf-8")

    if "{{ gestao_acl }}" in xml:
        print("Placeholders já presentes; nada a fazer.")
        return

    xml = xml.replace(
        ACL_ANCHOR,
        ACL_ANCHOR.replace("<w:t>-</w:t>", "<w:t>{{ gestao_acl }}</w:t>"),
        1,
    )
    xml = xml.replace(
        USINA_ANCHOR,
        USINA_ANCHOR.replace(
            "<w:t>-</w:t>", "<w:t>{{ gestao_usina_fotovoltaica }}</w:t>"
        ),
        1,
    )

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
