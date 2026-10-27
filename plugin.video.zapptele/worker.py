import sys
from resources.lib import app

command = sys.argv[1] if len(sys.argv) > 1 else 'sync'
try:
    success = app.sync(interactive=True, force=command == 'force')
    if command == 'setup' and success:
        app.configure_pvr()
    app.apply_pending()
except Exception as exc:
    import xbmc
    xbmc.log('Zapp Télé: worker failed ({})'.format(type(exc).__name__), xbmc.LOGWARNING)
    app.notice('Synchronisation indisponible. Le cache existant est conservé.')
