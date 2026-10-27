import contextlib
import gzip
import hashlib
import json
import os
import time
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs, urlsplit
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
from resources.lib.core import atomic, endpoint, fetch, parse_m3u, filtered, group_sort_key
from resources.lib.local_channels import CITIES, with_local_group
from resources.lib.sports_channels import with_sports_group
from resources.lib.quebec_channels import with_quebec_group

ID = 'plugin.video.zapptele'
ADDON = xbmcaddon.Addon(ID)
PROFILE = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
os.makedirs(PROFILE, exist_ok=True)


def path(name):
    return os.path.join(PROFILE, name)


def read(name, default):
    try:
        with open(path(name), encoding='utf-8') as stream:
            return json.load(stream)
    except (OSError, ValueError):
        return default


def rpc(method, params):
    return json.loads(xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0', id=1, method=method, params=params))))


def notice(message):
    xbmcgui.Dialog().notification('Zapp Télé', message, time=5000)


@contextlib.contextmanager
def lock():
    import fcntl
    with open(path('sync.lock'), 'a') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Une synchronisation est déjà en cours.')
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def import_existing():
    if ADDON.getSetting('username'):
        return
    folder = xbmcvfs.translatePath('special://profile/addon_data/pvr.iptvsimple/')
    if not os.path.isdir(folder):
        return
    for name in sorted(os.listdir(folder)):
        if not name.startswith('instance-settings-') or not name.endswith('.xml'):
            continue
        try:
            root = ET.parse(os.path.join(folder, name)).getroot()
            values = {s.get('id'): s.text or '' for s in root.findall('setting')}
            url = urlsplit(values.get('m3uUrl', ''))
            if url.hostname != 'zap444.com':
                continue
            query = parse_qs(url.query)
            username, password = query['username'][0], query['password'][0]
            ADDON.setSetting('host', '{}://{}'.format(url.scheme, url.netloc))
            ADDON.setSetting('username', username)
            ADDON.setSetting('password', password)
            atomic(path('instance.json'), json.dumps(name))
            notice('Compte Zapp existant repris dans les paramètres.')
            return
        except (OSError, ET.ParseError, KeyError, IndexError, ValueError):
            continue


def refresh_pvr():
    if xbmc.Player().isPlaying():
        notice('Fichiers prêts. Redémarrez Kodi après votre lecture pour actualiser la TV.')
        return
    result = rpc('Addons.SetAddonEnabled', {'addonid': 'pvr.iptvsimple', 'enabled': False})
    if 'error' in result:
        raise ValueError('Impossible de recharger IPTV Simple Client. Redémarrez Kodi.')
    xbmc.sleep(800)
    result = rpc('Addons.SetAddonEnabled', {'addonid': 'pvr.iptvsimple', 'enabled': True})
    if 'error' in result:
        raise ValueError('Activez IPTV Simple Client dans les extensions Kodi.')


def configure_pvr():
    try:
        xbmcaddon.Addon('pvr.iptvsimple')
    except RuntimeError:
        raise ValueError('Installez IPTV Simple Client depuis le dépôt LibreELEC, puis réessayez.')
    if not os.path.exists(path('channels.m3u')) or not os.path.exists(path('guide.xml')):
        raise ValueError('Téléchargez d’abord les chaînes et le guide.')
    folder = xbmcvfs.translatePath('special://profile/addon_data/pvr.iptvsimple/')
    name = read('instance.json', 'instance-settings-734277.xml')
    if not name.startswith('instance-settings-') or '/' in name:
        raise ValueError('Nom d’instance invalide.')
    target = os.path.join(folder, name)
    if os.path.exists(target):
        with open(target, 'rb') as stream:
            old = stream.read()
        if not os.path.exists(path('pvr-original.xml')):
            atomic(path('pvr-original.xml'), old)
        root = ET.fromstring(old)
    else:
        root = ET.Element('settings', version='2')
    values = {'kodi_addon_instance_name': 'Zapp Télé', 'kodi_addon_instance_enabled': 'true',
              'm3uPathType': '0', 'm3uPath': path('channels.m3u'), 'm3uUrl': '',
              'epgPathType': '0', 'epgPath': path('guide.xml'), 'epgUrl': '',
              'm3uRefreshMode': '1', 'm3uRefreshIntervalMins': '30',
              'tvGroupMode': '0', 'radioGroupMode': '0', 'tvChannelGroupsOnly': 'false',
              'radioChannelGroupsOnly': 'false'}
    for key, value in values.items():
        item = root.find("setting[@id='%s']" % key)
        if item is None:
            item = ET.SubElement(root, 'setting', id=key)
        item.attrib.pop('default', None)
        item.text = value
    atomic(target, ET.tostring(root, encoding='utf-8', xml_declaration=True))
    atomic(path('pvr.json'), 'true')
    refresh_pvr()


def changed_file(name, data):
    data = data if isinstance(data, bytes) else data.encode('utf-8')
    digest = hashlib.sha256(data).hexdigest()
    if read(name + '.sha256.json', '') == digest and os.path.exists(path(name)):
        return False
    if os.path.exists(path(name)):
        with open(path(name), 'rb') as stream:
            same = hashlib.sha256(stream.read()).hexdigest() == digest
        if same:
            atomic(path(name + '.sha256.json'), json.dumps(digest))
            return False
    atomic(path(name), data)
    atomic(path(name + '.sha256.json'), json.dumps(digest))
    return True


def start_sync(force=False, setup=False):
    command = 'setup' if setup else ('force' if force else 'sync')
    xbmc.executebuiltin('RunScript(special://home/addons/plugin.video.zapptele/worker.py,{})'.format(command))
    notice('Synchronisation en arrière-plan ; cache disponible pendant la mise à jour.')


def sync(interactive=True, force=False):
    with lock():
        addon = xbmcaddon.Addon(ID)
        host, username, password = [addon.getSetting(k) for k in ('host', 'username', 'password')]
        playlist_url = endpoint(host, username, password)
        guide_url = endpoint(host, username, password, True)
        now = time.time()
        identity = hashlib.sha256(playlist_url.encode('utf-8')).hexdigest()
        state = read('cache.json', {})
        # Adopt files created by v1.0 without downloading the XML again.
        if not state and os.path.exists(path('guide.xml')):
            state = {'identity': identity, 'playlist': read('last_sync.json', 0),
                     'guide': os.path.getmtime(path('guide.xml'))}
        new_account = state.get('identity') != identity
        playlist_due = (force or new_account or not os.path.exists(path('source.m3u'))
                        or now - state.get('playlist', 0) >= 21600)
        guide_due = (force or new_account or not os.path.exists(path('guide.xml'))
                     or now - state.get('guide', 0) >= 86400)
        changed = False
        errors = []
        if playlist_due:
            try:
                raw = fetch(playlist_url, 100 * 1024 * 1024)
                items = with_quebec_group(with_sports_group(with_local_group(parse_m3u(raw.decode('utf-8-sig', errors='replace')), addon.getSetting('local_city'))))
                changed_file('source.m3u', raw)
                changed = changed_file('channels.m3u', filtered(items, set(read('hidden.json', [])))) or changed
                state['playlist'] = now
                atomic(path('last_sync.json'), json.dumps(now))
            except Exception as exc:
                errors.append(type(exc).__name__)
        if guide_due:
            try:
                guide = fetch(guide_url, 200 * 1024 * 1024)
                if guide.startswith(b'\x1f\x8b'):
                    import io
                    with gzip.GzipFile(fileobj=io.BytesIO(guide)) as stream:
                        guide = stream.read(200 * 1024 * 1024 + 1)
                    if len(guide) > 200 * 1024 * 1024:
                        raise ValueError('Guide décompressé trop volumineux.')
                # Skip parsing and replacement for an identical guide.
                same = False
                if os.path.exists(path('guide.xml')):
                    with open(path('guide.xml'), 'rb') as stream:
                        same = hashlib.sha256(stream.read()).digest() == hashlib.sha256(guide).digest()
                if not same:
                    import io
                    root_tag = None
                    for event, elem in ET.iterparse(io.BytesIO(guide), events=('start', 'end')):
                        if root_tag is None:
                            root_tag = elem.tag
                        if event == 'end':
                            elem.clear()
                    if root_tag != 'tv':
                        raise ValueError('Guide XMLTV invalide.')
                    changed = changed_file('guide.xml', guide) or changed
                state['guide'] = now
            except Exception as exc:
                errors.append(type(exc).__name__)
        # On account changes, retry both resources until both belong to that account.
        if not new_account or not errors:
            state['identity'] = identity
        state['last_check'] = now
        state['errors'] = errors
        atomic(path('cache.json'), json.dumps(state))
        if changed and read('pvr.json', False):
            atomic(path('pvr_pending.json'), 'true')
        if errors:
            xbmc.log('Zapp Télé: sync failed ({})'.format(', '.join(errors)), xbmc.LOGWARNING)
            if interactive:
                notice('Mise à jour incomplète. Cache conservé ; nouvel essai ultérieur.')
        elif interactive:
            notice('Cache à jour : chaînes et guide disponibles.')
        return not errors


def apply_pending():
    if read('pvr_pending.json', False) and not xbmc.Player().isPlaying():
        refresh_pvr()
        atomic(path('pvr_pending.json'), 'false')


def records():
    if not os.path.exists(path('source.m3u')):
        start_sync()
        raise ValueError('Premier téléchargement en arrière-plan. Revenez dans quelques instants.')
    with open(path('source.m3u'), encoding='utf-8-sig', errors='replace') as stream:
        return with_quebec_group(with_sports_group(with_local_group(parse_m3u(stream.read()), xbmcaddon.Addon(ID).getSetting('local_city'))))


def choose_local_city():
    current = ADDON.getSetting('local_city')
    options = ['Désactiver'] + CITIES
    selected = xbmcgui.Dialog().select('Ville pour la présélection Locale', options,
                                      preselect=options.index(current) if current in options else 0)
    if selected < 0:
        return
    set_local_city(options[selected] if selected else '')


def set_local_city(city):
    if city and city not in CITIES:
        raise ValueError('Ville non prise en charge.')
    with lock():
        ADDON.setSetting('local_city', city)
        items = records()
        hidden = set(read('hidden.json', []))
        hidden.discard('Locale')
        atomic(path('hidden.json'), json.dumps(sorted(hidden), ensure_ascii=False))
        changed_file('channels.m3u', filtered(items, hidden))
        if read('pvr.json', False):
            atomic(path('pvr_pending.json'), 'true')
    apply_pending()
    count = sum(i['group'] == 'Locale' for i in items)
    notice('{} : {} chaînes dans Locale.'.format(city, count) if city else 'Présélection Locale désactivée.')


def choose_groups():
    items = records()
    counts = {}
    for item in items:
        counts[item['group']] = counts.get(item['group'], 0) + 1
    groups = sorted(counts, key=group_sort_key)
    hidden = set(read('hidden.json', []))
    from resources.lib.group_dialog import select_groups
    chosen = select_groups(ADDON.getAddonInfo('path'), groups, counts,
                           [i for i, g in enumerate(groups) if g not in hidden])
    if chosen is None:
        return
    with lock():
        # Use the newest playlist if a background refresh completed during the dialog.
        items = records()
        hidden = (hidden - set(groups)) | (set(groups) - {groups[i] for i in chosen})
        atomic(path('hidden.json'), json.dumps(sorted(hidden), ensure_ascii=False))
        changed_file('channels.m3u', filtered(items, hidden))
        if read('pvr.json', False):
            atomic(path('pvr_pending.json'), 'true')
    apply_pending()
    notice('{} groupes visibles sur {}.'.format(len(chosen), len(groups)))


def safe_action(action):
    try:
        action()
    except Exception as exc:
        # Never log exception text: urllib errors can contain credential-bearing URLs.
        xbmc.log('Zapp Télé: operation failed ({})'.format(type(exc).__name__), xbmc.LOGERROR)
        message = str(exc) if isinstance(exc, ValueError) else 'Échec de connexion ou de lecture. Vérifiez le serveur, le compte et le réseau, puis réessayez.'
        xbmcgui.Dialog().ok('Zapp Télé', message)
