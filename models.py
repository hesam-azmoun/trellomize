from datetime import datetime, timedelta
import uuid
from enum import Enum


class User:
    """create the user object"""
    def __init__(self, username: str, password: str, email: str, is_active=True):
        self.username = username
        self.password = password
        self.email = email
        self.is_active = is_active


class TaskStatus(Enum):
    """a class that represents the status of the task"""
    BACKLOG = 0
    TODO = 1
    DOING = 2
    DONE = 3
    ARCHIVED = 4


class TaskPriority(Enum):
    """"a class that represents the priority of the task"""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class Task:
    """a class that represents the task"""
    def __init__(self, title='', description='', assignees=None, priority=TaskPriority.LOW.name,
                 status=TaskStatus.BACKLOG.name):
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

    def set_id(self, task_id: str) -> None:
        """"set the task id"""
        self.task_id = task_id

    def get_id(self) -> str:
        """"get the task id """
        return self.task_id

    def add_history(self, change: str, user: str, time: str) -> None:

        self.history.append({'change': change, 'user': user, 'time': time})

    def already_history(self, list_history=None):
        if list_history is None:
            list_history = []
        self.history = list_history

    def already_comment(self, list_comment=None) -> None:
        if list_comment is None:
            list_comment = []
        self.comments = list_comment

    def add_comment(self, username: str, content: str) -> None:
        self.comments.append({
            'username': username,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })

    def update_status(self, status):
        self.status = status
        # self.history.append({
        #     'user': username,
        #     'timestamp': datetime.now().isoformat(),
        #     'action': f"Status updated to {status}"
        # })

    def update_priority(self, priority):
        self.priority = priority
        # self.history.append({
        #     'user': username,
        #     'timestamp': datetime.now().isoformat(),
        #     'action': f"Priority updated to {priority}"
        # })

    def assign_user(self, username: str) -> None:
        if username not in self.assignees:
            self.assignees.append(username)

    def unassign_user(self, username: str) -> None:
        if username in self.assignees:
            self.assignees.remove(username)

    def update_title(self, title: str) -> None:
        self.title = title

    def update_description(self, description: str) -> None:

        self.description = description


class Project:
    """"a class that represents the project"""
    def __init__(self, project_id: str, title: str, owner: str):
        self.project_id = project_id
        self.title = title
        self.owner = owner
        self.members = [owner]
        self.tasks = []

    def add_member(self, user: str) -> None:
        """"add a member to the project"""
        if user not in self.members:
            self.members.append(user)

    def remove_member(self, user: str) -> None:
        """"remove a member from the project"""
        if user in self.members:
            self.members.remove(user)

    def add_task(self, task: dict) -> None:
        """"add a task to the project"""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """"remove a task from the project"""
        self.tasks = [task for task in self.tasks if task.task_id != task_id]
