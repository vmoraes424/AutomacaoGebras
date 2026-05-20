"""Substitui o traço fixo em 4.1 SOLE Consultoria por {{ sole_consultoria }}."""

from __future__ import annotations

import io
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "contrato_padrao.docx"
BAK = ROOT / "contrato_padrao.docx.bak"

MARKER = "4.1 SOLE Consultoria:</w:t></w:r></w:p></w:tc><w:tc>"
DASH = (
    '<w:r w:rsidRPr="000D3DDE"><w:rPr><w:rFonts w:asciiTheme="minorHAnsi" '
    'w:hAnsiTheme="minorHAnsi" w:cstheme="minorBidi"/><w:sz w:val="18"/>'
    '<w:szCs w:val="18"/></w:rPr><w:t>-</w:t></w:r>'
)
PLACEHOLDER = (
    '<w:r w:rsidRPr="000D3DDE"><w:rPr><w:rFonts w:asciiTheme="minorHAnsi" '
    'w:hAnsiTheme="minorHAnsi" w:cstheme="minorBidi"/><w:sz w:val="18"/>'
    '<w:szCs w:val="18"/></w:rPr><w:t>{{ sole_consultoria }}</w:t></w:r>'
)


def main() -> None:
    if not DOCX.exists():
        raise SystemExit(f"Arquivo não encontrado: {DOCX}")
    if not BAK.exists():
        shutil.copy(DOCX, BAK)

    with zipfile.ZipFile(DOCX, "r") as zin:
        xml = zin.read("word/document.xml").decode("utf-8")
        pos = xml.find(MARKER)
        if pos < 0:
            raise SystemExit("Marcador '4.1 SOLE Consultoria' não encontrado no XML.")
        idx = xml.find(DASH, pos)
        if idx < 0:
            if "{{ sole_consultoria }}" in xml:
                print("Modelo já contém {{ sole_consultoria }} — nada a fazer.")
                return
            raise SystemExit("Célula com '-' após 4.1 não encontrada.")
        xml_new = xml[:idx] + PLACEHOLDER + xml[idx + len(DASH) :]

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    data = xml_new.encode("utf-8")
                zout.writestr(item, data)
        DOCX.write_bytes(buf.getvalue())
    print(f"Atualizado: {DOCX}")


if __name__ == "__main__":
    main()
