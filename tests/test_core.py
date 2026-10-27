import importlib.util
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
spec=importlib.util.spec_from_file_location('core',str(Path(__file__).resolve().parents[1] / 'plugin.video.zapptele/resources/lib/core.py'))
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
class Tests(unittest.TestCase):
 def test_encoding(self):
  q=parse_qs(urlsplit(c.endpoint('http://zap444.com:8080/', 'a+b&é','p?&=')).query)
  self.assertEqual(q['username'],['a+b&é']); self.assertEqual(q['password'],['p?&=']); self.assertEqual(q['output'],['ts'])
 def test_playlist(self):
  s='\ufeff#EXTM3U\n#EXTINF:-1 tvg-id="1" group-title="Québec, FR",Télé 1\n#KODIPROP:test=value\nhttp://example/1\n#EXTINF:-1,Deux\n#EXTGRP:Sports\nhttp://example/2\n'
  r=c.parse_m3u(s); self.assertEqual(r[0]['name'],'Télé 1'); self.assertEqual(r[1]['group'],'Sports')
  filtered=c.filtered(r,{'Sports'}); self.assertIn('#KODIPROP:test=value',filtered); self.assertNotIn('http://example/2',filtered)
  self.assertEqual(c.filtered(r,{'Sports','Québec, FR'}),'#EXTM3U\n')
 def test_reject(self):
  for s in ('<html>Erreur</html>','#EXTM3U\n'):
   with self.assertRaises(ValueError): c.parse_m3u(s)
  with self.assertRaises(ValueError): c.endpoint('file:///etc/passwd','u','p')
unittest.main()
