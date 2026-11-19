import os, tempfile, unittest
class AppTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();os.environ['LOCAL_DB_PATH']=os.path.join(self.tmp.name,'test.db');os.environ.pop('SUPABASE_URL',None);os.environ.pop('SUPABASE_SERVICE_ROLE_KEY',None)
  import app;app._supabase=None;self.client=app.app.test_client()
 def tearDown(self):self.tmp.cleanup()
 def test_health(self):self.assertEqual(self.client.get('/health').status_code,200)
 def test_dashboard(self):self.assertEqual(self.client.get('/').status_code,200)
 def test_task_lifecycle(self):
  r=self.client.post('/api/tasks',json={'title':'Test','subject':'Cloud','priority':'High'});self.assertEqual(r.status_code,201);tid=r.get_json()['task']['task_id']
  self.assertEqual(len(self.client.get('/api/tasks').get_json()['tasks']),1)
  self.assertTrue(self.client.patch(f'/api/tasks/{tid}/toggle').get_json()['is_completed'])
  self.assertEqual(self.client.put(f'/api/tasks/{tid}',json={'title':'Updated','subject':'Cloud','priority':'Low'}).status_code,200)
  self.assertEqual(self.client.delete(f'/api/tasks/{tid}').status_code,200)
 def test_validation(self):self.assertEqual(self.client.post('/api/tasks',json={'title':'  '}).status_code,400)
if __name__=='__main__':unittest.main()
