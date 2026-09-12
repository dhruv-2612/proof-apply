"""Install Pango DLLs from official MSYS2 packages into .tools, without system changes."""
import io, json, tarfile, urllib.request, hashlib
from pathlib import Path
import zstandard
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / '.tools' / 'msys'
URL = 'https://repo.msys2.org/mingw/ucrt64/'
def fetch(name):
    with urllib.request.urlopen(URL + name, timeout=120) as response: return response.read()
raw = fetch('ucrt64.db')
if raw[:4] == bytes.fromhex('28b52ffd'): raw = zstandard.ZstdDecompressor().stream_reader(io.BytesIO(raw)).read()
packages = {}
with tarfile.open(fileobj=io.BytesIO(raw), mode='r:*') as archive:
    for entry in archive:
        if entry.name.endswith('/desc'):
            fields = {}
            for block in archive.extractfile(entry).read().decode().split('\n\n'):
                lines = block.strip().splitlines()
                if lines: fields[lines[0].strip('%')] = lines[1:]
            if 'NAME' in fields: packages[fields['NAME'][0]] = fields
import re
for package in list(packages.values()):
    for alias in package.get('PROVIDES', []): packages.setdefault(re.split('[<>=]',alias)[0],package)
pending = ['mingw-w64-ucrt-x86_64-pango']
seen = set()
manifest = []
while pending:
    name = pending.pop()
    if name in seen: continue
    seen.add(name)
    package = packages.get(name)
    if not package: continue
    for dependency in package.get('DEPENDS', []):
        import re
        pending.append(re.split('[<>=]', dependency)[0])
    filename = package['FILENAME'][0]
    print('Installing', name, flush=True)
    cache = ROOT / '.tools' / 'msys-packages' / filename
    cache.parent.mkdir(parents=True, exist_ok=True)
    data = cache.read_bytes() if cache.exists() else fetch(filename)
    cache.write_bytes(data)
    expected = package['SHA256SUM'][0]
    if hashlib.sha256(data).hexdigest() != expected: raise ValueError('Package checksum mismatch')
    manifest.append({'filename': filename, 'sha256': expected})
    with zstandard.ZstdDecompressor().stream_reader(io.BytesIO(data)) as stream:
        with tarfile.open(fileobj=stream, mode='r|') as archive:
            for entry in archive:
                # Only runtime DLLs and font configuration, never scripts/install hooks.
                if entry.isfile() and (entry.name.endswith('.dll') or entry.name.startswith('ucrt64/etc/fonts/') or entry.name.startswith('ucrt64/share/fontconfig/')):
                    target = (DEST / entry.name).resolve()
                    if not target.is_relative_to(DEST.resolve()): raise ValueError('Unsafe archive path')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.extractfile(entry).read())
DEST.mkdir(parents=True, exist_ok=True)
(DEST / 'packages.json').write_text(json.dumps(manifest, indent=2))
print('Pango runtime ready:', DEST)
