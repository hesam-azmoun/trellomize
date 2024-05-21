from datetime import datetime, timedelta
import uuid

class User:
    def __init__(self, username, password, email, is_active=True):
        self.username = username
        self.password = password
        self.email = email
        self.is_active = is_active

class TaskStatus:
    BACKLOG = "BACKLOG"
    TODO = "TODO"
    DOING = "DOING"
    DONE = "DONE"
    ARCHIVED = "ARCHIVED"

class TaskPriority:
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class Task:
    def __init__(self, title='', description='', assignees=None, priority=TaskPriority.LOW, status=TaskStatus.BACKLOG):
        if assignees is None:
            assignees = []
        self.task_id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=24)
        self.assignees = assignees
        self.priority = priority
        self.status = status
        self.history = []
        self.comments = []

    def add_comment(self, username, content):
        self.comments.append({
            'username': username,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })

    def update_status(self, status, username):
        self.status = status
        self.history.append({
            'user': username,
            'timestamp': datetime.now().isoformat(),
            'action': f"Status updated to {status}"
        })

    def update_priority(self, priority, username):
        self.priority = priority
        self.history.append({
            'user': username,
            'timestamp': datetime.now().isoformat(),
            'action': f"Priority updated to {priority}"
        })

    def assign_user(self, username):
        if username not in self.assignees:
            self.assignees.append(username)

    def unassign_user(self, username):
        if username in self.assignees:
            self.assignees.remove(username)

class Project:
    def __init__(self, project_id, title, owner):
        self.project_id = project_id
        self.title = title
        self.owner = owner
        self.members = [owner]
        self.tasks = []

    def add_member(self, user):
        if user not in self.members:
            self.members.append(user)

    def remove_member(self, user):
        if user in self.members:
            self.members.remove(user)

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task_id):
        self.tasks = [task for task in self.tasks if task.task_id != task_id]
