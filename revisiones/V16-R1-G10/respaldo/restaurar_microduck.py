"""Restore or verify the Microduck V16 attachment set using only Python 3.11+."""
import argparse
import hashlib
import json
import os
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

BASE = 'https://github.com/MTNRS/microduck-v15/releases/download/'
TAG = 'v16-r1-g10'
INDEX = 'Indice_del_respaldo_V16.json'

def get_asset(url, cache):
    if not url.startswith(BASE):
        raise ValueError('Origen de archivo inesperado')
    name = url.rsplit('/', 1)[-1]
    if Path(name).name != name or not name:
        raise ValueError('Nombre de descarga no válido')
    path = cache / name
    if not path.is_file():
        with tempfile.NamedTemporaryFile(dir=cache, delete=False) as pending:
            tmp = Path(pending.name)
        try:
            with urllib.request.urlopen(url, timeout=180) as remote, tmp.open('wb') as dst:
                shutil.copyfileobj(remote, dst, 1024*1024)
            os.replace(tmp, path)
        finally:
            tmp.unlink(missing_ok=True)
    return path

def restore(args):
    cache = args.cache.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    index = json.loads(get_asset(BASE + TAG + '/' + INDEX, cache).read_text(encoding='utf8'))
    dest = args.destino.resolve()
    entries = index['contenido_por_sha256']
    archives = {}
    verified = set()
    count = 0
    try:
        for rel, info in index['archivos'].items():
            if args.prefijo and not rel.startswith(args.prefijo):
                continue
            path = (dest / PurePosixPath(rel)).resolve()
            if not path.is_relative_to(dest) or path == dest:
                raise ValueError('Ruta no válida')
            count += 1
            expected = info['sha256']
            if args.verificar and expected in verified:
                continue
            if path.exists() and not args.verificar:
                with path.open('rb') as src:
                    if hashlib.file_digest(src, 'sha256').hexdigest() != expected:
                        raise FileExistsError(f'Ya existe un archivo diferente en {rel}')
                continue
            entry = entries[expected]
            if 'url_directa' in entry:
                src = get_asset(entry['url_directa'], cache).open('rb')
            else:
                name = entry['archivo']
                if name not in archives:
                    archives[name] = zipfile.ZipFile(get_asset(BASE + TAG + '/' + name, cache))
                src = archives[name].open(entry['entrada'])
            digest = hashlib.sha256()
            size = 0
            temp = None
            try:
                if not args.verificar:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    temp = tempfile.NamedTemporaryFile(dir=path.parent, delete=False)
                with src:
                    while block := src.read(1024*1024):
                        digest.update(block)
                        size += len(block)
                        if temp: temp.write(block)
                if digest.hexdigest() != expected or size != info['bytes']:
                    raise ValueError(f'Fallo de integridad en {rel}')
                if temp:
                    temp.close()
                    os.replace(temp.name, path)
                verified.add(expected)
            finally:
                if temp:
                    temp.close()
                    Path(temp.name).unlink(missing_ok=True)
    finally:
        for archive in archives.values():
            archive.close()
    if not count:raise ValueError('El prefijo no coincide con ningún archivo')
    print(f'{count} rutas verificadas' if args.verificar else f'{count} rutas restauradas o ya correctas')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destino', type=Path)
    parser.add_argument('--cache', type=Path, default=Path('descargas_microduck'))
    parser.add_argument('--prefijo', default='', help='Por ejemplo, simulacion/')
    parser.add_argument('--verificar', action='store_true', help='Comprueba los bytes sin crear los archivos restaurados')
    restore(parser.parse_args())
