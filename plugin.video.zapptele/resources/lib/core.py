"""Playlist parsing and credential-safe network/storage helpers (no Kodi dependency)."""
import os
import re
import tempfile
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen


def endpoint(host, username, password, guide=False):
    host = host.strip().rstrip('/')
    parsed = urlsplit(host)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.query or parsed.fragment or parsed.username:
        raise ValueError('Hôte invalide : utilisez http://serveur:port ou https://serveur.')
    if not username or not password:
        raise ValueError('Renseignez le nom d’utilisateur et le mot de passe dans les paramètres.')
    params = dict(username=username, password=password)
    if not guide:
        params.update(type='m3u_plus', output='ts')
    return host + ('/xmltv.php?' if guide else '/get.php?') + urlencode(params)


def fetch(url, limit):
    with urlopen(Request(url, headers={'User-Agent': 'Kodi-ZappTele/1.0', 'Accept-Encoding': 'identity'}), timeout=60) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Réponse trop volumineuse.')
    return data


def parse_m3u(text):
    lines = text.lstrip('\ufeff').splitlines()
    if not lines or not lines[0].startswith('#EXTM3U'):
        raise ValueError('Le serveur n’a pas retourné une liste M3U valide. Vérifiez votre compte.')
    records, block = [], []
    for line in lines[1:]:
        line = line.strip()
        if line.startswith('#EXTINF:'):
            block = [line]
        elif block:
            if not line:
                continue
            block.append(line)
            if not line.startswith('#'):
                match = re.search(r'group-title\s*=\s*([\"\'])(.*?)\1', block[0], re.I)
                group = match.group(2).strip() if match else ''
                if not group:
                    group = next((v[8:].strip() for v in block if v.startswith('#EXTGRP:')), '')
                name = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', block[0], maxsplit=1)[-1]
                logo = re.search(r'tvg-logo="([^"]*)"', block[0])
                records.append(dict(group=group or 'Sans groupe', name=name, url=line,
                                    logo=logo.group(1) if logo else '', lines=block))
                block = []
    if not records:
        raise ValueError('La liste ne contient aucune chaîne exploitable.')
    return records


def group_sort_key(name):
    priority = {'Locale': 0, 'Sports #tata': 1, 'Québec — Chaînes spécialisées': 2}
    return priority.get(name, 3), name.casefold()


def filtered(records, hidden):
    return '#EXTM3U\n' + ''.join('\n'.join(r['lines']) + '\n' for r in sorted(records, key=lambda item: group_sort_key(item['group'])) if r['group'] not in hidden)


def atomic(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix='.zapp-')
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data if isinstance(data, bytes) else data.encode('utf-8'))
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
