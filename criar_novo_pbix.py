# -*- coding: utf-8 -*-
"""
Cria dashboard_socioeconomico_novo.pbix:
  - Base estrutural: Aula 10 Exercicio Inicial.pbix (DataModel valido)
  - Report/Layout: dashboard_socioeconomico.pbix (Pagina 2 com 13 visuais)
  - Tema: CY26SU04.json extraido do temp save (referenciado no Layout)

Usa zipfile API pura. DataModel preservado como ZIP_STORED.
"""
import zipfile, json
from pathlib import Path

DONOR    = Path(r"C:\Users\roberg\OneDrive - Alvarez and Marsal\Desktop\Projeto em Ciência de Dados III\Aula 10 Arquivos\Aula 10 Exercicio Inicial.pbix")
TEMP_SAVE = Path(r"C:\Users\roberg\Microsoft\Power BI Desktop Store App\TempSaves\dashboard_socioeconomico2c927522-bf4e-4884-8c11-c6bb44b8bae3.pbix")
LAYOUT_SRC = Path(__file__).parent / "dashboard_socioeconomico.pbix"
OUT        = Path(__file__).parent / "dashboard_socioeconomico_novo.pbix"

THEME_PATH = "Report/StaticResources/SharedResources/BaseThemes/CY26SU04.json"

# ── 1. Ler Layout com Pagina 2 ───────────────────────────────────────────────
print("1. Lendo Layout com Pagina 2...")
with zipfile.ZipFile(LAYOUT_SRC, "r") as z:
    layout_bytes = z.read("Report/Layout")

layout = json.loads(layout_bytes.decode("utf-16-le"))
for s in layout["sections"]:
    vc = len(s.get("visualContainers", []))
    print("   " + s["displayName"] + ": " + str(vc) + " visuais")

# Verificar tema referenciado no Layout
config_obj = json.loads(layout.get("config", "{}"))
tema = config_obj.get("themeCollection", {}).get("baseTheme", {}).get("name", "")
print("   Tema referenciado: " + tema)

# ── 2. Extrair CY26SU04.json do temp save ───────────────────────────────────
print("2. Extraindo " + tema + ".json do temp save...")
assert TEMP_SAVE.exists(), "Temp save nao encontrado: " + str(TEMP_SAVE)
with zipfile.ZipFile(TEMP_SAVE, "r") as z:
    theme_bytes = z.read(THEME_PATH)
print("   " + tema + ".json: " + str(len(theme_bytes)) + " bytes")

# ── 3. Reconstruir ZIP ───────────────────────────────────────────────────────
print("3. Construindo novo ZIP...")
with zipfile.ZipFile(DONOR, "r") as zin, zipfile.ZipFile(OUT, "w", allowZip64=False) as zout:
    for item in zin.infolist():
        if item.filename == "Report/Layout":
            zout.writestr(item, layout_bytes, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
            print("   Report/Layout: substituido (" + str(len(layout_bytes)) + " bytes)")
        elif item.filename == "DataModel":
            raw = zin.read(item.filename)
            zout.writestr(item, raw, compress_type=zipfile.ZIP_STORED)
            print("   DataModel: copiado STORED (" + str(len(raw)) + " bytes)")
        else:
            raw = zin.read(item.filename)
            zout.writestr(item, raw, compress_type=item.compress_type)
            print("   " + item.filename + ": copiado")

    # Adicionar tema CY26SU04.json (nao existe no Aula 10)
    zout.writestr(THEME_PATH, theme_bytes, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    print("   " + THEME_PATH.split("/")[-1] + ": adicionado (" + str(len(theme_bytes)) + " bytes)")

print()
print("Gravado: " + str(OUT.name) + " (" + str(OUT.stat().st_size // 1024) + " KB)")
print("Pronto!")
