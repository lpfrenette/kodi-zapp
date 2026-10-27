import xbmc
import xbmcaddon
from resources.lib import app

monitor = xbmc.Monitor()
if not monitor.waitForAbort(45):
    while not monitor.abortRequested():
        addon = xbmcaddon.Addon(app.ID)
        try:
            if addon.getSetting('automatic') == 'true' and addon.getSetting('username'):
                app.sync(interactive=False)
            app.apply_pending()
        except Exception as exc:
            xbmc.log('Zapp Télé: background update deferred ({})'.format(type(exc).__name__), xbmc.LOGWARNING)
        if monitor.waitForAbort(300):
            break
