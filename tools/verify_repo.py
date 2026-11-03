"""Offline verification of the exact manufacturing kit and editable CAD chunks."""

import argparse
import json
from pathlib import Path, PurePosixPath

from restore_cad import ROOT, RAW_SHA256, restore, sha, verify_parts


def verify_kit():
    root = ROOT / 'fabricacion'
    manifest = root / 'SHA256SUMS.txt'
    if sha(manifest) != '5b6c557be48d3a2ee7c4265281241ee9a81be44da612a2bc34679810ccd201bc':
        raise ValueError('El manifiesto no es el del kit V15 R2')
    records = {}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        digest, name = line.split('  ', 1)
        p = PurePosixPath(name)
        if p.is_absolute() or not p.parts or any(x in ('.', '..') or ':' in x or '\\' in x for x in p.parts) or name in records:
            raise ValueError(f'Ruta de kit no válida: {name}')
        src = root.joinpath(*p.parts)
        if not src.resolve().is_relative_to(root.resolve()) or sha(src) != digest:
            raise ValueError(f'Archivo del kit modificado: {name}')
        records[name] = digest
    files = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    # Runtime Python bytecode is never a delivery file or printer payload.
    files = {n for n in files if '/__pycache__/' not in n}
    if len(records) != 179 or files != set(records) | {'SHA256SUMS.txt'}:
        raise ValueError('Inventario exacto del kit incompleto o con archivos extra')
    if any(Path(p).suffix.lower() in ('.gcode', '.bgcode') for p in files):
        raise ValueError('El kit no debe contener G-code de impresora')
    stls = json.loads((root / 'STL_MANIFIESTO_V15.json').read_text(encoding='utf-8'))
    inventory = {r['file'].replace('\\', '/'): r['sha256'] for r in stls['parts'] if r['quantity'] == 1}
    if (stls['units'], len(inventory), stls['all_STL_coordinate_topology_pass'], stls['all_float32_stable']) != ('mm', 80, True, True):
        raise ValueError('Manifiesto de impresión inválido')
    if inventory != {p: v for p, v in records.items() if p.startswith('STL_POR_COLORES/') and p.endswith('.stl')}:
        raise ValueError('STL por colores distintos del manifiesto')
    if sum(p.startswith('PROYECTOS_PRUSA_PAUSAS/') and p.endswith('.3mf') for p in files) != 9:
        raise ValueError('Faltan proyectos de pausas')
    return len(records)


def main():
    p = argparse.ArgumentParser(description='Comprueba el kit y los datos CAD locales')
    p.add_argument('--restore-to', type=Path, help='también reconstruye y verifica el Blender en esa ruta')
    args = p.parse_args()
    try:
        count = verify_kit()
        parts = verify_parts()
        if args.restore_to:
            out = restore(args.restore_to)
            if sha(out) != RAW_SHA256:
                raise ValueError('SHA-256 del Blender reconstruido incorrecto')
        print(f'Kit: {count} archivos íntegros, 80 STL, 9 proyectos. CAD: {len(parts)} partes íntegras.')
        return 0
    except (OSError, ValueError, KeyError) as exc:
        p.exit(2, f'Verificación: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
