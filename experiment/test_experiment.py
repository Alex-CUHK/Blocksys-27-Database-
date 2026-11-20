import unittest,tempfile,pathlib,json
from experiment import matrix,cost,optimize,ingest
class Checks(unittest.TestCase):
 def test_conservation_and_direction(self):
  m=matrix([('stack','alu',32),('stack','alu',64),('alu','stack',32)])
  self.assertEqual(sum(map(sum,m)),128);self.assertEqual(m[1][2],96);self.assertEqual(m[2][1],32)
 def test_geometry(self):
  m=matrix([('dispatch','stack',10)])
  slots=[(0,0,0),(0,0,1)]+[(i,0,0) for i in range(2,8)]
  self.assertEqual(cost(m,slots,.25),2.5)
 def test_optimum_not_worse(self):
  m=matrix([('dispatch','stack',10)])
  slots=[(i,0,0) for i in range(8)]
  best,coords=optimize(m,slots,1)
  self.assertEqual(best,10);self.assertEqual(len(set(coords)),8)
 def test_missing_provenance_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'bad.json';p.write_text('{"events":[]}')
   with self.assertRaises(ValueError):ingest(p)
if __name__=='__main__':unittest.main()
