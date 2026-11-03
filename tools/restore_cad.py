"""Restore the exact editable Blender file with Python's standard library."""

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / 'cad'
RAW_NAME = 'Microduck_V15_R2_PUBLICO.blend'
RAW_BYTES = 133472984
RAW_SHA256 = 'a465c42346cfdcfb609c7b509ed14e586b0315916f60b3d3c4202c541da85174'
BUFFER = 1 << 20


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as f:
        for data in iter(lambda: f.read(BUFFER), b''):
            digest.update(data)
    return digest.hexdigest()


def verify_parts():
    manifest = json.loads((CAD / 'manifest.json').read_text(encoding='utf-8'))
    if (manifest['schema'], manifest['file'], manifest['bytes'], manifest['sha256']) != (
            'microduck-cad-gzip-parts/1', RAW_NAME, RAW_BYTES, RAW_SHA256):
        raise ValueError('Manifiesto CAD distinto de V15 R2')
    parts = manifest['parts']
    if not 1 <= len(parts) <= 20:
        raise ValueError('Número de partes CAD incorrecto')
    result = []
    for i, entry in enumerate(parts, 1):
        name = f'microduck-v15.blend.gz.{i:03d}'
        part = CAD / name
        if entry['file'] != name or not part.resolve().is_relative_to(CAD.resolve()) or not 0 < entry['bytes'] <= 40 * BUFFER:
            raise ValueError(f'Parte CAD no válida: {name}')
        if part.stat().st_size != entry['bytes'] or sha(part) != entry['sha256']:
            raise ValueError(f'Parte CAD dañada: {name}')
        result.append(part)
    return result


def restore(output):
    parts = verify_parts()
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        if output.is_file() and output.stat().st_size == RAW_BYTES and sha(output) == RAW_SHA256:
            return output
        raise FileExistsError(f'Ya existe un archivo distinto: {output}; usa --output con otra ruta')
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.TemporaryFile(dir=output.parent) as joined:
            for part in parts:
                with part.open('rb') as f:
                    shutil.copyfileobj(f, joined, BUFFER)
            joined.seek(0)
            digest, size = hashlib.sha256(), 0
            with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.restore.tmp', delete=False) as f:
                temp = Path(f.name)
                with gzip.GzipFile(fileobj=joined) as archive:
                    for data in iter(lambda: archive.read(BUFFER), b''):
                        size += len(data)
                        if size > RAW_BYTES:
                            raise ValueError('CAD descomprimido excede el tamaño esperado')
                        digest.update(data)
                        f.write(data)
            if size != RAW_BYTES or digest.hexdigest() != RAW_SHA256:
                raise ValueError('El CAD reconstruido no coincide con el archivo publicado')
        try:
            os.link(temp, output)  # Publish without overwriting any existing file.
        except FileExistsError:
            raise
        except OSError:
            with output.open('xb') as f:
                try:
                    with temp.open('rb') as src:
                        shutil.copyfileobj(src, f, BUFFER)
                except BaseException:
                    f.close()
                    output.unlink()
                    raise
        return output
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser(description='Reconstruye el Blender de la edición pública de Microduck V15 R2')
    p.add_argument('--output', type=Path, default=CAD / RAW_NAME)
    args = p.parse_args()
    try:
        out = restore(args.output)
        print(f'{out}\nSHA-256 {RAW_SHA256}')
        return 0
    except (OSError, ValueError, KeyError) as exc:
        p.exit(2, f'CAD: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
