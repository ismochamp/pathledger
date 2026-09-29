import hashlib,json,pathlib,subprocess,tempfile,unittest,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from generate_fixture import generate_fixture
BASE=pathlib.Path(__file__).resolve().parents[1];ENGINE=BASE/'runtime/pathledger'
def run(path,check=True):
 r=subprocess.run([str(ENGINE),str(path)],capture_output=True,text=True,check=check)
 return json.loads(r.stdout) if check else r
class PathLedgerTests(unittest.TestCase):
 def test_bundled_archive(self):
  r=run(generate_fixture());self.assertEqual(r['errors'],3);self.assertEqual(r['warnings'],1);self.assertEqual(r['reviews'],1);self.assertFalse(r['truncated'])
 def test_nonexistent(self):self.assertEqual(run(BASE/'does-not-exist',False).returncode,2)
 def test_file_rejected(self):self.assertEqual(run(BASE/'README.md',False).returncode,2)
 def test_empty_directory(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(run(d)['entries'],0)
 def test_symlink_boundary_and_unchanged_source(self):
  with tempfile.TemporaryDirectory() as d,tempfile.TemporaryDirectory() as outside:
   p=pathlib.Path(d);f=p/'safe.txt';f.write_text('original');before=hashlib.sha256(f.read_bytes()).hexdigest();(pathlib.Path(outside)/'CON').write_text('outside');(p/'external').symlink_to(outside,target_is_directory=True)
   r=run(p);self.assertEqual(r['files'],1);self.assertEqual(r['symlinks'],1);self.assertEqual(r['errors'],0);self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),before)
 def test_trim_collision_and_reserved_names(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)
   for name in ['data','data.','COM1.txt','lpt².txt']:(p/name).write_text('x')
   codes=[i['code'] for i in run(p)['issues']];self.assertIn('CASE_OR_TRIM_COLLISION',codes);self.assertEqual(codes.count('RESERVED_DEVICE_NAME'),2)
 def test_json_roundtrip_control_and_backslash(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);name='quote"line\nback\\file';(p/name).write_text('x');r=run(p);self.assertEqual(r['issues'][0]['path'],name);self.assertEqual(r['issues'][0]['code'],'INVALID_WINDOWS_CHARACTER')
 def test_unicode_retained(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);(p/'東京.txt').write_text('x');r=run(p);self.assertEqual(r['errors'],0);self.assertEqual(r['issues'][0]['path'],'東京.txt')
 def test_depth_limit(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)
   for _ in range(66):p=p/'a';p.mkdir()
   r=run(d);self.assertTrue(r['truncated']);self.assertIn('DEPTH_LIMIT',[i['code'] for i in r['issues']])
if __name__=='__main__':unittest.main(verbosity=2)
