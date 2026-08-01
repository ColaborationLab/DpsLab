import os,tempfile,unittest
from pathlib import Path
from dpslab.new_artifact_transaction import NewArtifactTransaction,NewArtifactTransactionError
class TransactionTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve();self.a=self.root/"a.bin";self.b=self.root/"b.bin"
    def tearDown(self):self.tmp.cleanup()
    def test_01_commit_one(self):NewArtifactTransaction().commit_new({self.a:b"a"});self.assertEqual(self.a.read_bytes(),b"a")
    def test_02_commit_multiple(self):NewArtifactTransaction().commit_new({self.a:b"a",self.b:b"b"});self.assertEqual((self.a.read_bytes(),self.b.read_bytes()),(b"a",b"b"))
    def test_03_existing_refused(self):self.a.write_bytes(b"old");self.assertRaises(NewArtifactTransactionError,NewArtifactTransaction().commit_new,{self.a:b"new"});self.assertEqual(self.a.read_bytes(),b"old")
    def test_04_missing_parent_refused(self):self.assertRaises(NewArtifactTransactionError,NewArtifactTransaction().commit_new,{self.root/"missing"/"x":b"x"})
    def test_05_relative_path_refused(self):self.assertRaises(NewArtifactTransactionError,NewArtifactTransaction().commit_new,{Path("x"):b"x"})
    def test_06_empty_bytes_refused(self):self.assertRaises(NewArtifactTransactionError,NewArtifactTransaction().commit_new,{self.a:b""})
    def test_07_text_refused(self):self.assertRaises(NewArtifactTransactionError,NewArtifactTransaction().commit_new,{self.a:"secret"})
    def test_08_empty_mapping_refused(self):self.assertRaises(NewArtifactTransactionError,NewArtifactTransaction().commit_new,{})
    def test_09_stage_is_removed(self):NewArtifactTransaction().commit_new({self.a:b"a"});self.assertEqual(list(self.root.glob(".*.dpslab-stage-*")),[])
    def test_10_failure_rolls_back_first_commit(self):
        calls=[]
        def replace(src,dst):
            calls.append(dst)
            if len(calls)==2:raise OSError("synthetic")
            os.replace(src,dst)
        self.assertRaises(NewArtifactTransactionError,NewArtifactTransaction(replace).commit_new,{self.a:b"a",self.b:b"b"});self.assertFalse(self.a.exists());self.assertFalse(self.b.exists())
    def test_11_failure_removes_stages(self):
        def fail(src,dst):raise OSError("synthetic")
        self.assertRaises(NewArtifactTransactionError,NewArtifactTransaction(fail).commit_new,{self.a:b"a"});self.assertEqual(list(self.root.iterdir()),[])
    def test_12_does_not_create_parent(self):p=self.root/"new"/"x";self.assertRaises(NewArtifactTransactionError,NewArtifactTransaction().commit_new,{p:b"x"});self.assertFalse(p.parent.exists())
    def test_13_bytes_preserved_exactly(self):data=b"\x00\r\n\xff";NewArtifactTransaction().commit_new({self.a:data});self.assertEqual(self.a.read_bytes(),data)
    def test_14_no_overwrite_on_second_call(self):NewArtifactTransaction().commit_new({self.a:b"a"});self.assertRaises(NewArtifactTransactionError,NewArtifactTransaction().commit_new,{self.a:b"b"})
