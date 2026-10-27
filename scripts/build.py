"""Build a Kodi-installable ZIP using only tracked add-on sources and assets."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
addon = root / 'plugin.video.zapptele'
manifest = ET.parse(addon / 'addon.xml').getroot()
out = root / 'dist' / ('{}-{}.zip'.format(manifest.get('id'), manifest.get('version')))
out.parent.mkdir(exist_ok=True)
with ZipFile(out, 'w', ZIP_DEFLATED) as archive:
    for file in sorted(addon.rglob('*')):
        if file.is_file() and '__pycache__' not in file.parts and not file.name.startswith(('.', '._')) and file.suffix != '.pyc':
            archive.write(file, file.relative_to(root))
print(out)
