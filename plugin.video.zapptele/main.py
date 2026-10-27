import os
import sys
from urllib.parse import parse_qs, urlencode
import xbmc
import xbmcgui
import xbmcplugin
from resources.lib import app

app.import_existing()
handle = int(sys.argv[1])
base = sys.argv[0]
params = parse_qs(sys.argv[2].lstrip('?'))
action = params.get('action', [''])[0]


def groups():
    if not os.path.exists(app.path('source.m3u')):
        app.start_sync()
        return
    app.choose_groups()


def setup():
    if os.path.exists(app.path('channels.m3u')) and os.path.exists(app.path('guide.xml')):
        app.configure_pvr()
        app.start_sync()
    else:
        app.start_sync(setup=True)


def menu():
    for label, command in [('Paramètres de connexion', 'settings'),
                           ('Télécharger les chaînes et le guide', 'sync'),
                           ('Afficher ou masquer les groupes', 'groups'),
                           ('Configurer la Télévision Kodi et le guide', 'pvr'),
                           ('Présélection Locale — choisir la ville', 'local'),
                           ('Parcourir les chaînes', 'browse')]:
        item = xbmcgui.ListItem(label)
        xbmcplugin.addDirectoryItem(handle, base + '?' + urlencode({'action': command}), item, True)
    xbmcplugin.endOfDirectory(handle)


def browse():
    items = app.records()
    hidden = set(app.read('hidden.json', []))
    group = params.get('group', [None])[0]
    if group is None:
        for name in sorted({i['group'] for i in items} - hidden, key=app.group_sort_key):
            xbmcplugin.addDirectoryItem(handle, base + '?' + urlencode({'action': 'browse', 'group': name}), xbmcgui.ListItem(name), True)
    elif group not in hidden:
        for channel in items:
            if channel['group'] != group:
                continue
            item = xbmcgui.ListItem(channel['name'])
            item.setArt({'thumb': channel['logo'], 'icon': channel['logo']})
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle, channel['url'], item, False)
    xbmcplugin.setContent(handle, 'videos')
    xbmcplugin.endOfDirectory(handle)


if action == 'settings':
    app.ADDON.openSettings()
elif action == 'sync':
    app.safe_action(lambda: app.start_sync(force=True))
elif action == 'local':
    app.safe_action(app.choose_local_city)
elif action == 'groups':
    app.safe_action(groups)
elif action == 'pvr':
    app.safe_action(setup)
elif action == 'browse':
    app.safe_action(browse)
else:
    menu()
