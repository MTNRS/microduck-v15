"""Verifica una entrega local del Microduck con Python 3.10 o posterior."""
import argparse
import csv
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def sha256(file):
    digest = hashlib.sha256()
    with file.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check(condition, message):
    if not condition:
        raise ValueError(message)


def rows(file):
    with file.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=";"))


def verify(folder):
    for line in (folder / "SHA256SUMS.txt").read_text(encoding="utf8").splitlines():
        expected, relative = line.split("  ", 1)
        file = folder / relative
        check(file.is_file() and sha256(file) == expected, f"Archivo ausente o modificado: {relative}")

    catalog = rows(folder / "Indice_STL_y_placas.csv")
    stls = {}
    for part in catalog:
        file = folder / part["stl"].replace("\\", "/")
        check(file.is_file(), f"Falta {part['pieza']}")
        stls[part["pieza"]] = file
    check(len(stls) == len(catalog) == 86, "El catálogo debe identificar 86 piezas distintas.")
    check(set(stls.values()) == set((folder / "STL_POR_COLORES").rglob("*.stl")), "El catálogo y las carpetas STL difieren.")

    jobs = json.loads((folder / "Verificacion/Trabajos_laminados.json").read_text(encoding="utf8"))
    used = set()
    pauses = 0
    for name, job in sorted(jobs.items()):
        project = folder / "Placas_P2S_AMS2" / (name + ".3mf")
        toolpath = folder / "Para_la_P2S_laminado" / (name + ".gcode.3mf")
        check(sha256(toolpath) == job["sha256_3mf"], f"Paquete de máquina cambiado en {name}")
        with zipfile.ZipFile(project) as native:
            opts = json.loads(native.read("Metadata/project_settings.config"))
            check(opts["printer_model"] == "Bambu Lab P2S", f"Impresora distinta en {name}")
            tree = ET.fromstring(native.read("Metadata/model_settings.config"))
            ids = []
            for obj in tree.findall("object"):
                label = obj.find("metadata[@key='name']").get("value")
                ids.append("P" + Path(label).name[:2])
            check(sorted(ids) == sorted(job["piezas"]), f"Piezas del proyecto distintas en {name}")
        with zipfile.ZipFile(toolpath) as sliced:
            with sliced.open("Metadata/plate_1.gcode") as stream:
                digest = hashlib.sha256()
                heights = []
                z_height = None
                nozzle = False
                for line in stream:
                    digest.update(line)
                    if b"Bambu Lab P2S 0.4 nozzle" in line:
                        nozzle = True
                    if line.startswith(b"; Z_HEIGHT:"):
                        z_height = float(line.split(b":", 1)[1])
                    if line.strip() == b"M400 U1":
                        heights.append(z_height)
                check(nozzle, f"No se identifica la P2S de 0,4 mm en {name}")
                check(digest.hexdigest() == job["sha256_gcode"], f"G-code cambiado en {name}")
                check(heights == job["pausas_mm"], f"Pausas distintas en {name}: {heights}")
        check(not used.intersection(ids), f"Piezas repetidas en {name}")
        used.update(ids)
        pauses += len(heights)
    check(used == set(stls) and len(jobs) == 9, "Cobertura incompleta de las placas.")
    return f"{len(stls)} STL, {len(jobs)} placas P2S de 0,4 mm y {pauses} pausas verificadas."


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carpeta", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    try:
        print(verify(parser.parse_args().carpeta.resolve()))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        sys.exit(str(error))

