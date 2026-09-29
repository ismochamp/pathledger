from pathlib import Path
import json,urllib.request,urllib.error,unittest
BASE=Path(__file__).resolve().parents[1];CFG=json.loads((BASE/'app_config.json').read_text());URL='http://127.0.0.1:'+str(CFG['port'])
def request(route='/',body=None,origin=URL,host=None):
 headers={'Origin':origin,'Content-Type':'application/json'}
 if host:headers['Host']=host
 req=urllib.request.Request(URL+route,data=json.dumps(body).encode() if body is not None else None,headers=headers)
 try:
  with urllib.request.urlopen(req) as r:return r.status,r.read(),r.headers
 except urllib.error.HTTPError as e:
  result=(e.code,e.read(),e.headers);e.close();return result
class LiveHttpTests(unittest.TestCase):
 def test_health(self):self.assertEqual(request('/health')[0],200)
 def test_host_guard(self):self.assertEqual(request('/health',host='evil.example')[0],403)
 def test_origin_guard(self):self.assertEqual(request('/analyze',{'path':str(BASE/CFG['fixture'])},origin='https://evil.example')[0],403)
 def test_non_object_payload(self):self.assertEqual(request('/analyze',['wrong'])[0],400)
 def test_missing_input(self):self.assertEqual(request('/analyze',{'path':str(BASE/'does-not-exist')})[0],400)
 def test_real_engine_and_exports(self):
  status,body,_=request('/analyze',{'path':str(BASE/CFG['fixture'])});self.assertEqual(status,200);r=json.loads(body)
  if CFG['kind']=='paths':self.assertEqual(r['errors'],3)
  else:self.assertEqual(r['parsed'],13)
  for fmt in ('csv','json','html'):
   status,body,headers=request('/download/'+fmt);self.assertEqual(status,200);self.assertTrue(len(body)>100);self.assertIn('attachment',headers['Content-Disposition'])
if __name__=='__main__':unittest.main(verbosity=2)
