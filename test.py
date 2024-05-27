import unittest
from models import User, Project, Task, TaskPriority, TaskStatus

class TestProjectManagement(unittest.TestCase):
    def test_user_creation(self):
        user = User('testuser', 'password123', 'testuser@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.is_active)

    def test_project_creation(self):
        owner = User('testuser', 'password123', 'testuser@example.com')
        project = Project('1', 'Test Project', owner.username)
        self.assertEqual(project.project_id, '1')
        self.assertEqual(project.title, 'Test Project')
        self.assertEqual(len(project.members), 1)
        self.assertEqual(project.members[0], owner.username)

    def test_task_creation(self):
        task = Task('Test Task', 'Description of the task')
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.description, 'Description of the task')
        self.assertEqual(task.priority, TaskPriority.LOW)
        self.assertEqual(task.status, TaskStatus.BACKLOG)

    def test_add_member_to_project(self):
        owner = User('testuser', 'password123', 'testuser@example.com')
        project = Project('1', 'Test Project', owner.username)
        user = User('newuser', 'password123', 'newuser@example.com')
        project.add_member(user.username)
        self.assertEqual(len(project.members), 2)
        self.assertEqual(project.members[1], 'newuser')

    def test_add_task_to_project(self):
        owner = User('testuser', 'password123', 'testuser@example.com')
        project = Project('1', 'Test Project', owner.username)
        task = Task('Test Task', 'Description of the task')
        project.add_task(task)
        self.assertEqual(len(project.tasks), 1)
        self.assertEqual(project.tasks[0].title, 'Test Task')

if __name__ == '__main__':
    unittest.main()