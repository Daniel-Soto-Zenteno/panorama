"""Create a source delivery with an explicit allowlist, without local data or secrets."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root=Path(__file__).resolve().parents[1]
files=[]
for folder in ['backend','frontend','tools','docs']:
    for file in (root/folder).rglob('*'):
        if not file.is_file():
            continue
        rel=file.relative_to(root)
        if '__pycache__' in rel.parts or 'qa' in rel.parts:
            continue
        if file.suffix in ['.sqlite3','.pyc'] or file.name in ['.env','manifiesto-sha256.json']:
            continue
        files.append(file)
files += [root/name for name in ['README.md','.env.example','.gitignore']]
manifest={str(f.relative_to(root)).replace('\\','/'):{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for f in sorted(files)}
mf=root/'docs/evidencias/manifiesto-sha256.json'
mf.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
out=root/'Panorama_Entrega_Evaluacion_3.zip'
with ZipFile(out,'w',compression=ZIP_DEFLATED) as z:
    for f in files+[mf]:
        z.write(f,str(f.relative_to(root)).replace('\\','/'))
with ZipFile(out) as z:
    assert z.testzip() is None
    assert all(not any(x in name.split('/') for x in ['.env','.demo-credentials.txt','.git','.venv','.local']) for name in z.namelist())
    for name,meta in manifest.items():
        assert hashlib.sha256(z.read(name)).hexdigest()==meta['sha256']
    # Check the locally generated demo passwords are absent without printing them.
    private=root/'.demo-credentials.txt'
    if private.exists():
        secrets=[line.split(': ',1)[1].encode() for line in private.read_text(encoding='utf-8-sig').splitlines() if line.startswith(('demo_vecina: ','demo_moderador: '))]
        assert all(secret not in z.read(name) for name in z.namelist() for secret in secrets)
print(f'Paquete verificado: {len(files)+1} archivos; {out.stat().st_size} bytes. Sin datos ni claves locales.')
