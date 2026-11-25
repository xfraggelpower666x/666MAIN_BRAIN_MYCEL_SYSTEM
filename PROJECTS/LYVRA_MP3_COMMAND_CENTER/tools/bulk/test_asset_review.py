import unittest,tempfile,zipfile
from pathlib import Path
from asset_review import inspect,blob
class Review(unittest.TestCase):
 def test_log_hold(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d); (p/'mp3').mkdir(); b=b'C:\\Users\\example\\file'; (p/'mp3/a.log').write_bytes(b)
   with zipfile.ZipFile(p/'a.zip','w') as z:z.writestr('a.log',b)
   args=(p,{'mp3/a.log':blob(b)},{'mp3':p/'a.zip'},['mp3/a.log'])
   x=inspect(*args)['mp3/a.log'];self.assertTrue(x['windows_path']);self.assertFalse(x['public_release']);self.assertEqual(x['privacy_review'],'HOLD')
   (p/'mp3/a.log').write_bytes(b'changed');self.assertRaises(ValueError,inspect,*args)
if __name__=='__main__':unittest.main()
