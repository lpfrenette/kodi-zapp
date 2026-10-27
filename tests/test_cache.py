import importlib.util, json, os, sys, tempfile, time, types, unittest
from unittest.mock import patch
from pathlib import Path
import shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'plugin.video.zapptele'))
profile=tempfile.mkdtemp(prefix='zapp-cache-')
class Addon:
 def __init__(self,*a): pass
 def getAddonInfo(self,k): return profile
 def getSetting(self,k): return {'host':'http://zap444.com:8080','username':'test','password':'test','local_city':''}[k]
sys.modules['xbmcaddon']=types.SimpleNamespace(Addon=Addon)
sys.modules['xbmcvfs']=types.SimpleNamespace(translatePath=lambda p:p)
sys.modules['xbmc']=types.SimpleNamespace(log=lambda *a:None,LOGWARNING=1)
sys.modules['xbmcgui']=types.SimpleNamespace()
from resources.lib import app
class CacheTests(unittest.TestCase):
 def setUp(self):
  for f in os.listdir(profile): os.unlink(os.path.join(profile,f))
  app.atomic(app.path('source.m3u'),'#EXTM3U\n#EXTINF:-1 group-title="A",One\nhttp://example/1\n')
  app.atomic(app.path('guide.xml'),'<tv/>')
  app.atomic(app.path('channels.m3u'),'#EXTM3U\n')
  app.atomic(app.path('last_sync.json'),json.dumps(time.time()))
 def test_warm_cache_no_network_or_xml_parse(self):
  stamp=os.stat(app.path('guide.xml')).st_mtime_ns
  with patch.object(app,'fetch',side_effect=AssertionError('network')), patch.object(app.ET,'iterparse',side_effect=AssertionError('parse')):
   self.assertTrue(app.sync(False))
  self.assertEqual(os.stat(app.path('guide.xml')).st_mtime_ns,stamp)
 def test_playlist_expiry_does_not_reload_guide(self):
  app.atomic(app.path('last_sync.json'),json.dumps(time.time()-22000))
  with patch.object(app,'fetch',return_value=b'#EXTM3U\n#EXTINF:-1,One\nhttp://example/1\n') as fetch:
   self.assertTrue(app.sync(False)); self.assertEqual(fetch.call_count,1)
   self.assertIn('/get.php?',fetch.call_args.args[0])
 def test_failed_guide_preserves_cache(self):
  with patch.object(app,'fetch',side_effect=OSError('offline')):
   self.assertFalse(app.sync(False,force=True))
  self.assertEqual(Path(app.path('guide.xml')).read_text(),'<tv/>')
 def test_identical_download_keeps_xml_file(self):
  stamp=os.stat(app.path('guide.xml')).st_mtime_ns
  def download(url,limit):
   return b'<tv/>' if '/xmltv.php?' in url else b'#EXTM3U\n#EXTINF:-1,One\nhttp://example/1\n'
  with patch.object(app,'fetch',side_effect=download),patch.object(app.ET,'iterparse',side_effect=AssertionError('parse')):
   self.assertTrue(app.sync(False,force=True))
  self.assertEqual(os.stat(app.path('guide.xml')).st_mtime_ns,stamp)
try:
 unittest.main()
finally:
 shutil.rmtree(profile)
