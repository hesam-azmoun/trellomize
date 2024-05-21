import hashlib
from models import User, Project, Task, TaskPriority, TaskStatus
import storage
from logger import log
from utils import hash_password, validate_email
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

current_user = None

def create_user(username, password, email):
    users = storage.load_users()
    if username in users or any(user['email'] == email for user in users.values()):
        console.print("Error: Username or email already exists.", style="bold red")
        return

    if not validate_email(email):
        console.print("Error: Invalid email format.", style="bold red")
        return

    users[username] = {
        'password': hash_password(password),
        'email': email,
        'is_active': True
    }
    storage.save_users(users)
    log(f"User created: {username}")
    console.print("User created successfully.", style="bold green")

def authenticate(username, password):
    users = storage.load_users()
    if username not in users or users[username]['password'] != hash_password(password):
        return False
    if not users[username]['is_active']:
        console.print("Error: Account is inactive.", style="bold red")
        return False
    global current_user
    current_user = username
    return True

def deactivate_user(username):
    users = storage.load_users()
    if username in users:
        users[username]['is_active'] = False
        storage.save_users(users)
        log(f"User deactivated: {username}")
        console.print(f"User {username} deactivated.", style="bold green")

def create_project(project_id, title):
    projects = storage.load_projects()
    users = storage.load_users()

    if project_id in projects:
        console.print("Error: Project ID already exists.", style="bold red")
        return

    owner = users[current_user]
    project = Project(project_id, title, current_user)
    projects[project_id] = {
        'title': title,
        'owner': current_user,
        'members': [current_user],
        'tasks': []
    }
    storage.save_projects(projects)
    log(f"Project created: {project_id} by {current_user}")
    console.print("Project created successfully.", style="bold green")

def add_member_to_project(project_id, username):
    projects = storage.load_projects()
    users = storage.load_users()

    if project_id not in projects:
        console.print("Error: Project not found.", style="bold red")
        return

    if username not in users:
        console.print("Error: User not found.", style="bold red")
        return

    project = projects[project_id]
    if current_user != project['owner']:
        console.print("Error: Only the project owner can add members.", style="bold red")
        return

    if username not in project['members']:
        project['members'].append(username)
        storage.save_projects(projects)
        log(f"User {username} added to project {project_id}")
        console.print("Member added successfully.", style="bold green")

def remove_member_from_project(project_id, username):
    projects = storage.load_projects()
    
    if project_id not in projects:
        console.print("Error: Project not found.", style="bold red")
        return

    project = projects[project_id]
    if current_user != project['owner']:
        console.print("Error: Only the project owner can remove members.", style="bold red")
        return

    if username in project['members']:
        project['members'].remove(username)
        storage.save_projects(projects)
        log(f"User {username} removed from project {project_id}")
        console.print("Member removed successfully.", style="bold green")

def add_task_to_project(project_id, title, description, assignees):
    projects = storage.load_projects()
    users = storage.load_users()

    if project_id not in projects:
        console.print("Error: Project not found.", style="bold red")
        return

    project = projects[project_id]
    if not set(assignees).issubset(set(project['members'])):
        console.print("Error: All assignees must be project members.", style="bold red")
        return

    task = Task(title, description, assignees)
    project['tasks'].append({
        'task_id': task.task_id,
        'title': task.title,
        'description': task.description,
        'start_time': task.start_time.isoformat(),
        'end_time': task.end_time.isoformat(),
        'assignees': task.assignees,
        'priority': task.priority,
        'status': task.status,
        'history': task.history,
        'comments': task.comments
    })
    storage.save_projects(projects)
    log(f"Task '{title}' added to project '{project_id}'")
    console.print("Task added successfully.", style="bold green")

def view_project_tasks(project_id):
    projects = storage.load_projects()
    
    if project_id not in projects:
        console.print("Error: Project not found.", style="bold red")
        return

    project = projects[project_id]
    tasks = project['tasks']

    table = Table(title=f"Tasks for Project {project_id}")
    table.add_column("Task ID", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Description")
    table.add_column("Start Time")
    table.add_column("End Time")
    table.add_column("Assignees")
    table.add_column("Priority")
    table.add_column("Status")

    for task in tasks:
        table.add_row(
            task['task_id'],
            task['title'],
            task['description'],
            task['start_time'],
            task['end_time'],
            ", ".join(task['assignees']),
            task['priority'],
            task['status']
        )

    console.print(table)

def main_menu():
    while True:
        console.print(f"\nWelcome {current_user}!", style="bold blue")
        console.print("1. Create Project")
        console.print("2. Add Member to Project")
        console.print("3. Remove Member from Project")
        console.print("4. Add Task to Project")
        console.print("5. View Project Tasks")
        console.print("6. Logout")
        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6"])

        if choice == "1":
            project_id = Prompt.ask("Enter project ID")
            title = Prompt.ask("Enter project title")
            create_project(project_id, title)
        elif choice == "2":
            project_id = Prompt.ask("Enter project ID")
            username = Prompt.ask("Enter username to add")
            add_member_to_project(project_id, username)
        elif choice == "3":
            project_id = Prompt.ask("Enter project ID")
            username = Prompt.ask("Enter username to remove")
            remove_member_from_project(project_id, username)
        elif choice == "4":
            project_id = Prompt.ask("Enter project ID")
            title = Prompt.ask("Enter task title")
            description = Prompt.ask("Enter task description")
            assignees = Prompt.ask("Enter assignees (comma separated)").split(", ")
            add_task_to_project(project_id, title, description, assignees)
        elif choice == "5":
            project_id = Prompt.ask("Enter project ID")
            view_project_tasks(project_id)
        elif choice == "6":
            break

def login():
    global current_user
    while True:
        console.print("\n1. Register")
        console.print("2. Login")
        choice = Prompt.ask("Select an option", choices=["1", "2"])

        if choice == "1":
            username = Prompt.ask("Enter username")
            password = Prompt.ask("Enter password", password=True)
            email = Prompt.ask("Enter email")
            create_user(username, password, email)
        elif choice == "2":
            username = Prompt.ask("Enter username")
            password = Prompt.ask("Enter password", password=True)
            if authenticate(username, password):
                main_menu()
                current_user = None
                break
            else:
                console.print("Error: Invalid username or password.", style="bold red")

if __name__ == "__main__":
    login()
