import sys,unittest,tempfile,sqlite3,urllib.error
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import workload as w
class Checks(unittest.TestCase):
 def test_periods(self):
  self.assertEqual(w.stamp('2026-05-01'),w.stamp(w.PERIODS['P2'][1]))
  self.assertEqual(w.stamp('2024-03-01')-w.stamp('2024-02-28'),172800)
 def test_offset(self):
  self.assertEqual(w.stamp('2025-05-01T08:00:00+08:00'),w.stamp('2025-05-01'))
 def test_custom_disk_limit(self):
  with patch.object(w,'DISK_LIMIT_GB',0.001),patch.object(w,'size',return_value=2_000_000):
   with self.assertRaisesRegex(RuntimeError,'STOP'):w.guard()
 def test_duplicates(self):
  f=lambda n:{'timestamp':hex([10,20,20,20,30][n])}
  self.assertEqual(w.lower_bound(f,4,20),1);self.assertEqual(w.lower_bound(f,4,21),4);self.assertEqual(w.lower_bound(f,4,31),5)
 def test_budget(self):
  with self.assertRaisesRegex(RuntimeError,'BUDGET'):w.RPC('SECRET',0).call('x',[])
 def test_disk(self):
  with patch.object(w,'size',return_value=6*10**9):
   with self.assertRaisesRegex(RuntimeError,'STOP'):w.guard()
 def test_null(self):
  from unittest.mock import MagicMock
  response=MagicMock();response.__enter__.return_value.read.return_value=b'{"result":null}'
  with patch('urllib.request.urlopen',return_value=response):
   with self.assertRaisesRegex(RuntimeError,'RPC_NULL'):w.RPC('https://example.org').call('x',[])
 def test_secret_network(self):
  with patch('urllib.request.urlopen',side_effect=urllib.error.URLError('SECRET')):
   with self.assertRaisesRegex(RuntimeError,'^NETWORK_UNAVAILABLE$'):w.RPC('https://example.org/SECRET').call('x',[])
 def test_429(self):
  with patch('urllib.request.urlopen',side_effect=urllib.error.HTTPError('secret',429,'secret',{},None)),patch('time.sleep'):
   r=w.RPC('https://example.org',3)
   with self.assertRaisesRegex(RuntimeError,'HTTP_429'):r.call('x',[])
   self.assertEqual(r.calls,3)
 def test_resume(self):
  with tempfile.TemporaryDirectory() as d,patch.object(w,'ROOT',Path(d)):
   (Path(d)/'data').mkdir();a=w.fixture();b=w.fixture();self.assertEqual(a,b);self.assertEqual(a['hours'],576)
 def test_chain_mismatch(self):
  from argparse import Namespace
  with patch.dict('os.environ',{'ETH_RPC_URL':'https://secret'}),patch.object(w.RPC,'call',return_value='0xa'),patch.object(w,'csvwrite'):
   rows=w.sources(Namespace(max_requests=5,dry_run=False,confirm_free=True))['sources']
   self.assertEqual(rows[0]['reason'],'CHAIN_ID_MISMATCH')
if __name__=='__main__':unittest.main()
