from pathlib import Path
import csv,json,re,shutil
from zipfile import ZipFile,ZIP_DEFLATED
from urllib.parse import urlsplit,unquote
from auditar_impresion import ROOT,V15,sha
from preparar_v16 import OUT,WORK,read,write

def adapt(path,text):
    if path.suffix.lower()=='.md':
        text=text.replace('../fabricacion/','../')
        text=text.replace('LISTA_IMPRESION_V15.csv','LISTA_IMPRESION_V16.csv')
        text=text.replace('PAUSAS_OBLIGATORIAS_TUERCAS_V15.csv','PAUSAS_OBLIGATORIAS_TUERCAS_V16.csv')
        text=text.replace('../DOCUMENTACION/GUIA_IMPRESION_Y_MONTAJE_V15.html','../GUIA_V16.md')
        text=text.replace('GUIA_IMPRESION_Y_MONTAJE_V15.html','../GUIA_V16.md')
        text=text.replace('Microduck V15 R2','Microduck V16')
        text=text.replace('](04-puesta-en-marcha.md','](https://github.com/MTNRS/microduck-v15/blob/f3f1e2f52184c79bc06244fd9417a5fb969a3eab/docs/04-puesta-en-marcha.md')
        text=text.replace('P45 y P65 llevan tres capas de balsa','P33, P36, P45 y P65 llevan tres capas de balsa')
        text=text.replace('El perfil verificado usa boquilla de 0,4 mm y capas de 0,20 mm, incluida la primera.',
                          'El diagnóstico usa boquilla de 0,4 mm. Aplica a cada pieza la capa y la primera capa indicadas en LISTA_IMPRESION_V16.csv.')
    return text

def setup_docs():
    for folder in ('STL_POR_COLORES','PROYECTOS_PRUSA_PAUSAS'):
        assert (OUT/folder).is_dir()
    for folder in ('PROBETAS_PRIMERO','ACCESORIOS_LLAVE'):
        shutil.copytree(V15/folder,OUT/folder,dirs_exist_ok=True)
    for f in (V15/'DOCUMENTACION').rglob('*'):
        if not f.is_file():continue
        rel=f.relative_to(V15)
        if 'VERIFICACIONES' in rel.parts or f.name in ('GUIA_IMPRESION_Y_MONTAJE_V15.html','GUIA_IMPRESION_Y_MONTAJE_V15.txt'):continue
        dest=OUT/rel;dest.parent.mkdir(exist_ok=True,parents=True)
        if f.suffix=='.md':dest.write_text(adapt(rel,f.read_text(encoding='utf-8-sig')),encoding='utf-8')
        else:shutil.copyfile(f,dest)
    d=OUT/'docs';d.mkdir(exist_ok=True)
    for name in ('01-materiales.md','02-montaje.md','03-electricidad.md'):
        source=V15.parent/'docs'/name
        (d/name).write_text(adapt(Path(name),source.read_text(encoding='utf-8-sig')),encoding='utf-8')
    shutil.copyfile(V15/'PAUSAS_OBLIGATORIAS_TUERCAS_V15.csv',OUT/'PAUSAS_OBLIGATORIAS_TUERCAS_V16.csv')
    (OUT/'LICENSE-MODELS.md').write_text((V15.parent/'LICENSE-MODELS.md').read_text(encoding='utf-8-sig').replace('SOURCES.md','FUENTES.md'),encoding='utf-8')
    shutil.copytree(V15.parent/'third_party',OUT/'third_party',dirs_exist_ok=True)
    (OUT/'FUENTES.md').write_text(
        '# Procedencia\n\nV16 deriva del diseño V15 publicado con 80 piezas imprimibles. Consulta el inventario de fuentes y licencias de la revisión base. [Microduck V15 R2](https://github.com/MTNRS/microduck-v15/blob/f3f1e2f52184c79bc06244fd9417a5fb969a3eab/SOURCES.md)\n\n'
        'Las adaptaciones que incorporan mallas de Pollen Robotics mantienen la licencia CC BY-NC-SA 4.0. [Licencia de modelos](LICENSE-MODELS.md)\n',encoding='utf-8')

def numbers_and_guide():
    manifest=read(OUT/'MANIFIESTO_STL_V16.json')
    verdict=read(OUT/'VERIFICACION_LAMINADO_V16.json')
    baseline={r['id']:r for r in read(WORK/'auditoria-v15/V15_GEOMETRIA_Y_TRAYECTORIAS.json')}
    result={r['id']:r for r in verdict['parts']}
    assert verdict['passed']==verdict['total']==len(manifest['parts'])==80
    passages=read(OUT/'VERIFICACION_CORREDORES_V16.json')
    assert passages['checked']==passages['clear']==26
    assert read(WORK/'BLENDER_V16_R1.json')['reopened_verified']
    total=sum(len(x['pause_actual']) for x in verdict['parts']);assert total==12
    assert sum(bool(x['pause_actual']) for x in verdict['parts'])==9
    assert len(list((OUT/'PROYECTOS_PRUSA_PAUSAS').glob('*.3mf')))==9
    change=[]
    for r in manifest['parts']:
        actual=result[r['id']];prior=baseline[r['id']]
        assert actual['stl_sha256']==r['sha256']==sha(OUT/r['file'])
        if r['motivo']=='Misma superficie en STL binario':continue
        change.append({
            'id':r['id'],'motivo':r['motivo'],
            'altura_V15_mm':round(prior['max_z_mm']-prior['minimum_z_mm'],4),
            'altura_V16_mm':round(r['max_z_mm']-r['minimum_z_mm'],4),
            'soporte_V15_cm3':round(prior['support_extrusion_mm3']/1000,3),
            'soporte_V16_cm3':round(actual['support_extrusion_mm3']/1000,3),
            'capas_V15':prior['model_layers'],'capas_V16':actual['model_layers'],
        })
    with (OUT/'COMPARATIVA_V15_V16.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(change[0]));writer.writeheader();writer.writerows(change)
    rows={x['id']:x for x in manifest['parts']};p44=rows['P44']
    fine=', '.join(r['id'] for r in rows.values() if r['process']['layer_height_mm']==.1)
    raft=', '.join(r['id'] for r in rows.values() if r['process']['raft_layers']==3)
    rot=sum(r['rotation_and_translation_from_v15_stl']!=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]] for r in rows.values())
    p44_lines=(
        f'**P44 es la carcasa azul del pecho.** {p44["motivo"]}. El laminado conserva la inserción de ocho tuercas '
        'en dos paradas. Usa las piezas de esta carpeta para el piloto y comprueba el borde de CAP06 en la vista previa.\n\n'
        'En P44, pausa al acabar la capa 225 (Z45 mm) y de nuevo al acabar la capa 230 (Z46 mm). '
        'Son cuatro tuercas por parada. Los marcadores del 3MF están al comenzar las capas 226 y 231. '
        'Conserva la primera capa y las siguientes a 0,20 mm, sin balsa ni altura variable. Activa soporte sólo desde la cama y omite soporte de puentes.'
    )
    guide=f"""# Microduck V16 · revisión de impresión

{p44_lines}

1. Importa en milímetros, escala 100 %. Conserva la orientación del STL. Si el laminador no apoya la pieza en la cama automáticamente, bájala en Z sin girarla. Aplica los ajustes de su fila. [Lista de impresión](LISTA_IMPRESION_V16.csv) · [STL por colores](STL_POR_COLORES/)
2. Usa boquilla de 0,4 mm y Arachne. La capa general es 0,20 mm. Usa primera capa y capas de **0,10 mm** en **{fine}**. Usa tres capas de balsa en **{raft}**. El diagnóstico aplicó brim de 5 mm y separación superior de soporte de 0,25 mm. PETG usa 4 perímetros y 40 % de relleno giroide, TPU 95A usa 3 perímetros y 20 %. Selecciona temperaturas y velocidades de tu máquina y filamento.
3. Los nueve 3MF con pausas incluyen la pieza y los eventos. Comprueba que tu laminador conserva las 12 paradas y deja libres los 26 alojamientos antes de imprimir. Configura y prueba la función de pausa de tu impresora. [Proyectos PrusaSlicer](PROYECTOS_PRUSA_PAUSAS/) · [CSV de pausas](PAUSAS_OBLIGATORIAS_TUERCAS_V16.csv)
4. Imprime las probetas y un P44 de prueba. Inserta las ocho tuercas durante sus pausas y presenta las tapas P20/P28 del cuello. Comprueba acceso de los tornillos, asiento del rodamiento y retirada de soporte. Monta un pie piloto y comprueba los finales de carrera P56/P58. Limpia las zonas de encaje del pack P61 y del conector P66 antes de comprobar con una galga o pieza real. [Probetas](PROBETAS_PRIMERO/) · [Materiales](docs/01-materiales.md) · [Montaje](docs/02-montaje.md) · [Electricidad](docs/03-electricidad.md)

V16 contiene **80 STL binarios** y **{rot} orientaciones revisadas**. Las superficies se conservan salvo los cambios registrados en el manifiesto. En P44 el bisel retira la lámina que el laminador omitía. La comparación conserva pequeñas desviaciones de huella en una zona vecina y localiza la única desviación nueva de 0,021 mm. [Comparación de 900 puntos de P44](verificacion/P44_COMPARACION_MISMOS_900_TESTIGOS.json) P45 elimina dos microcavidades internas, conserva el exterior y usa la capa de 0,10 mm para el borde de la escotilla. P33/P34 reducen altura y soporte respecto a V15. [Comparación de impresión](COMPARATIVA_V15_V16.csv) · [Manifiesto](MANIFIESTO_STL_V16.json)

PrusaSlicer 2.9.6 leyó las 80 piezas sin repararlas y laminó las 80 con los ajustes indicados. Se comprobaron las 12 pausas y los 26 corredores de inserción de tuercas. La primera impresión de P44 debe confirmar el acabado y el encaje con el lote y la impresora reales. [Verificación de laminado](VERIFICACION_LAMINADO_V16.json) · [Corredores de tuercas](VERIFICACION_CORREDORES_V16.json)

La mandíbula del kit conserva los anclajes fijos. El estudio para una futura pinza de tela identifica qué hace falta para moverla. [Estudio de mandíbula](docs/mandibula.md) · [Control y programación](https://github.com/MTNRS/microduck-v15#microduck-v15-r2)
"""
    (OUT/'GUIA_V16.md').write_text(guide,encoding='utf-8')

def jaw_doc():
    doc=read(WORK/'mandibula/BARRIDO_HIPOTETICO_MANDIBULA_V16.json')
    a=next(r for r in doc['angles'] if r['degrees']==2)
    w=max(a['collisions_over_point01_mm3'],key=lambda r:r['mm3'])
    (OUT/'docs/mandibula.md').write_text(f"""# Mandíbula y agarre de tela

La mandíbula P36 va fijada a la cabeza por dos cierres M2. El MG09 está en su alojamiento y el canal PCA 14 está reservado. La versión de impresión conserva el montaje fijo y el canal deshabilitado.

Al simular el giro alrededor del eje de la mandíbula original, con los dos cierres retirados del modelo, aparece una intersección de {w['mm3']:.2f} mm³ con P34 al abrir 2°. Se necesita rediseñar el acoplamiento del brazo OEM, añadir el apoyo coaxial del lado opuesto y dar despeje al arco de giro. [Barrido de CAD](../verificacion/BARRIDO_HIPOTETICO_MANDIBULA_V16.json)

Para un piloto de agarre, montar la cabeza en banco, probar el arco con el mecanismo descargado y calibrar el servo con medidas propias. La boca requiere contacto blando y tope para no comprimir el calcetín contra plástico rígido. Medir fuerza de retención, corriente de pico y corriente durante el agarre. Después hay que comprobar que el robot alcanza el suelo con una postura estable y puede levantar el objeto manteniendo el agarre.
""",encoding='utf-8')

def verify_links():
    bad=[]
    for p in [OUT/'GUIA_V16.md',*list((OUT/'docs').glob('*.md'))]:
        for target in re.findall(r'\]\(([^)\s]+)\)',p.read_text(encoding='utf-8')):
            uri=urlsplit(target)
            if not uri.scheme and uri.path and not (p.parent/unquote(uri.path)).exists():bad.append((str(p),target))
    if bad:raise ValueError(bad)

def pack():
    setup_docs();numbers_and_guide();jaw_doc()
    v=OUT/'verificacion';v.mkdir(exist_ok=True)
    for src in (WORK/'mandibula/BARRIDO_HIPOTETICO_MANDIBULA_V16.json',
                WORK/'carcasa/P45_CONTROL_020.json',WORK/'carcasa/P45_PRUEBA_010.json',
                WORK/'orientaciones-cabeza/ORIENTACIONES_CABEZA_RECOMENDADAS_V16.json',
                WORK/'orientaciones-electronica/ORIENTACIONES_ELECTRONICA_V16.json',
                WORK/'carcasa/P45_V16_010_VALIDACION.json',
                WORK/'carcasa/P44_CAP06_BISEL/P44_ALIVIO_CAP06_QA.json',
                WORK/'carcasa/P44_CAP06_BISEL/P44_MAPA_BORDE_CAP06_BISEL.json',
                WORK/'carcasa/P44_CAP06_BISEL/P44_COMPARACION_MISMOS_900_TESTIGOS.json',
                WORK/'pausas/P44_98e1c9a9002a_PASOS_TUERCAS.json',
                WORK/'BLENDER_V16_R1.json'):
        if src.exists():shutil.copyfile(src,v/src.name)
    assert (v/'P44_98e1c9a9002a_PASOS_TUERCAS.json').is_file()
    assert (v/'P44_MAPA_BORDE_CAP06_BISEL.json').is_file()
    assert (v/'P44_COMPARACION_MISMOS_900_TESTIGOS.json').is_file()
    verify_links()
    files=sorted(x for x in OUT.rglob('*') if x.is_file() and x.name!='SHA256SUMS.txt')
    assert all(x.suffix.lower() not in ('.gcode','.bgcode','.blend','.npz') for x in files)
    hashes={x.relative_to(OUT).as_posix():sha(x) for x in files}
    sums=OUT/'SHA256SUMS.txt';sums.write_text(''.join(f'{v}  {k}\n' for k,v in hashes.items()),encoding='utf-8')
    target=ROOT/'Microduck_V16_Kit_Impresion.zip'
    temp=target.with_suffix('.zip.tmp')
    with ZipFile(temp,'w',ZIP_DEFLATED,compresslevel=5) as z:
        for f in [*files,sums]:z.write(f,f.relative_to(OUT).as_posix())
    with ZipFile(temp) as z:
        assert set(z.namelist())==set(hashes)|{'SHA256SUMS.txt'}
        import hashlib
        for name,h in hashes.items():
            with z.open(name) as f:
                digest=hashlib.sha256()
                for block in iter(lambda:f.read(1<<20),b''):digest.update(block)
            assert digest.hexdigest()==h,name
    temp.replace(target)
    print('ZIP',target,len(files)+1,'files',target.stat().st_size,'bytes',sha(target),flush=True)
if __name__=='__main__':pack()
