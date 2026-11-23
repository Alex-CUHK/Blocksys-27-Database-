import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from history_audit import check_boundary,PublicRPC
class HistoryChecks(unittest.TestCase):
 def test_boundary(self):
  check_boundary({'number':'0x1','timestamp':'0x9','hash':'a'},{'number':'0x2','timestamp':'0xa','parentHash':'a'},10)
 def test_same_timestamp_predecessor(self):
  with self.assertRaisesRegex(RuntimeError,'PREDECESSOR'):check_boundary({'timestamp':'0xa'},{'timestamp':'0xa'},10)
 def test_parent(self):
  with self.assertRaisesRegex(RuntimeError,'PARENT'):check_boundary({'timestamp':'0x9','hash':'b'},{'timestamp':'0xa','parentHash':'a'},10)
 def test_no_requests_over_budget(self):
  with self.assertRaisesRegex(RuntimeError,'BUDGET'):PublicRPC('https://example.org',[0]).call('eth_chainId',[])
 def test_pruned_lower_search(self):
  from history_audit import retained_lower_bound
  def fetch(n):
   if n<4:raise RuntimeError('RPC_ERROR_4444')
   return {'timestamp':hex(n*10)}
  self.assertEqual(retained_lower_bound(fetch,10,75),8)
  self.assertEqual(retained_lower_bound(fetch,10,20),4) # predecessor check must still reject
