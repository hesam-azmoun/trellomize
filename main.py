import hashlib
from models import User, Project, Task, TaskPriority, TaskStatus
from storage import Storage
from logger import log1
from utils import Utils
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from datetime import datetime, timedelta

console = Console()

current_user = None
loop_task_def = None


def create_user(username: str, password: str, email: str) -> None:
    """A user builds and stores the information in the users.json ."""
    users = Storage.load_users()
    if username in users or any(user['email'] == email for user in users.values()):
        console.print("Error: Username or email already exists.", style="bold red")
        return

    if not Utils.validate_email(email):
        console.print("Error: Invalid email format.", style="bold red")
        return

    if not Utils.validate_username(username):
        console.print("Error: Invalid username format.", style="bold red")
        return

    users[username] = {
        'password': Utils.hash_password(password),
        'email': email,
        'is_active': True
    }
    Storage.save_users(users)
    if email == "admin@gmail.com":

        log1.info(f"Admin created: {username}")
    else:

        log1.info(f"User created: {username}")
        console.print("User created successfully.", style="bold green")


def authenticate(username: str, password: str) -> bool:
    """Check the validity of a username and password."""
    users = Storage.load_users()
    if username not in users or users[username]['password'] != Utils.hash_password(password):
        return False
    if not users[username]['is_active']:
        console.print("Error: Account is inactive.", style="bold red")
        return False
    global current_user
    current_user = username
    return True


def deactivate_user(username: str) -> None:
    """"Disables the user selected by the leader"""
    users = Storage.load_users()
    admin = Storage.load_admin()

    if current_user != admin["username"]:
        console.print("Error: Only the leader can deactivate members.", style="bold red")
        return
    if username not in users:
        console.print("Error: User not found.", style="bold red")
        return

    users[username]['is_active'] = False
    Storage.save_users(users)

    log1.info(f"User deactivated: {username}")
    console.print(f"User {username} deactivated.", style="bold green")


def create_project(project_id: str, title: str) -> None:
    """It stores the information in the projects.json ."""
    projects = Storage.load_projects()
    users = Storage.load_users()

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
    Storage.save_projects(projects)
    log1.info(f"Project created: {project_id} by {current_user}")
    console.print("Project created successfully.", style="bold green")


def remove_project(project_id: str) -> None:
    """removes a project from the projects.json file by leader."""
    projects = Storage.load_projects()
    if project_id not in projects:
        console.print("Error: Project not found.", style="bold red")
        return
    project = projects[project_id]
    if current_user != project['owner']:
        console.print("Error: Only the project owner can remove project.", style="bold red")
        return
    projects.pop(project_id)
    Storage.save_projects(projects)
    log1.info(f"User {current_user} removed from project {project_id}")
    console.print("Project removed successfully.", style="bold green")


def add_member_to_project(project_id: str, username: str) -> None:
    """adds a member to a project by leader."""
    projects = Storage.load_projects()
    users = Storage.load_users()

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
        Storage.save_projects(projects)
        log1.info(f"User {username} added to project {project_id}")
        console.print("Member added successfully.", style="bold green")


def remove_member_from_project(project_id: str, username: str) -> None:
    """removes a member from a project by leader."""
    projects = Storage.load_projects()

    if project_id not in projects:
        console.print("Error: Project not found.", style="bold red")
        return

    project = projects[project_id]
    if current_user != project['owner']:
        console.print("Error: Only the project owner can remove members.", style="bold red")
        return

    if username in project['members']:
        project['members'].remove(username)
        Storage.save_projects(projects)
        log1.info(f"User {username} removed from project {project_id}")
        console.print("Member removed successfully.", style="bold green")
    elif username not in project['members']:
        console.print(f"{username} not member in project {project_id}")


def add_task_to_project(project_id: str, title: str, description: str, assignees: list) -> None:
    """adds a task to a project by leader."""
    projects = Storage.load_projects()
    users = Storage.load_users()

    if project_id not in projects:
        console.print("Error: Project not found.", style="bold red")
        return

    project = projects[project_id]
    if current_user != project['owner']:
        console.print("Error: Only the project owner can remove project.", style="bold red")
        return
    if not set(assignees).issubset(set(project['members'] + [""])):
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
    Storage.save_projects(projects)
    log1.info(f"Task '{title}' added to project '{project_id}'")
    console.print("Task added successfully.", style="bold green")


def list_project() -> None:
    """Shows the projects list."""
    leader = []
    member = []
    projects = Storage.load_projects()
    for key, value in projects.items():
        if value['owner'] == current_user:
            leader.append(key)
        else:
            if current_user in value['members']:
                member.append(key)
    table = Table(title='[red]list project', style="bold blue")
    table.add_column("owner", style="yellow")
    table.add_column("member", style="green")
    table.add_row('\n'.join(leader), '\n'.join(member))
    console.print(table)


def edit_task(project_id: str, projects: dict, loop_task: int, location: str, location_task_id: str) -> None:
    """Apply the desired changes to the selected task."""
    project = projects[project_id]
    tasks = project['tasks']
    task_id = location_task_id

    if location == "edit Task":
        task_id = Prompt.ask("Enter task id")
    selected_task = {}
    temp = 0
    for i in tasks:
        if i["task_id"] == task_id:
            selected_task = tasks.pop(temp)
        temp += 1
    while loop_task == 0:
        if selected_task == {}:
            console.print("Error: Task not found.", style="bold red")
            log1.error(f"task {task_id} not found")
            break
        if current_user not in selected_task["assignees"]:
            console.print("Error: only assignees can edited")
            break
        my_task = Task(selected_task["title"], selected_task["description"], selected_task["assignees"],
                       selected_task["priority"], selected_task["status"])
        # show menu
        console.print("1. modify title")
        console.print("2. modify description")
        console.print("3. modify end_time")
        console.print("4. modify priority ")
        console.print("5. modify status")
        console.print("6. add comment")
        console.print("7. remove member from task")
        console.print("8. add user to the task")
        console.print("9. remove task")
        console.print("10. back")
        console.print("11. logout")
        choice = Prompt.ask("Select an option",
                            choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"])
        if choice == "1":
            title = Prompt.ask("Enter task title")
            my_task.update_title(title)
            my_task.set_id(task_id)
            log1.info(f"{current_user} changed title the task {task_id} in the project {project_id}")
            my_task.already_history(selected_task["history"])
            my_task.add_history("title", current_user, datetime.now().isoformat())
            project['tasks'].append({
                'task_id': my_task.get_id(),
                'title': my_task.title,
                'description': my_task.description,
                'start_time': selected_task["start_time"],
                'end_time': selected_task['end_time'],
                'assignees': my_task.assignees,
                'priority': selected_task["priority"],
                'status': selected_task["status"],
                'history': my_task.history,
                'comments': selected_task["comments"]
            })
            Storage.save_projects(projects)
        elif choice == "2":
            description = Prompt.ask("Enter task description")
            my_task.update_description(description)
            my_task.set_id(task_id)
            log1.info(f"{current_user} changed description the task {task_id} in the project {project_id}")
            my_task.already_history(selected_task["history"])
            my_task.add_history("description", current_user, datetime.now().isoformat())
            project['tasks'].append({
                'task_id': my_task.get_id(),
                'title': my_task.title,
                'description': my_task.description,
                'start_time': selected_task["start_time"],
                'end_time': selected_task['end_time'],
                'assignees': my_task.assignees,
                'priority': selected_task["priority"],
                'status': selected_task["status"],
                'history': my_task.history,
                'comments': selected_task["comments"]
            })
            Storage.save_projects(projects)
        elif choice == "3":
            my_task.set_id(task_id)
            log1.info(f"{current_user} changed end_time the task {task_id} in the project {project_id}")
            my_task.already_history(selected_task["history"])
            my_task.add_history("end time", current_user, datetime.now().isoformat())
            project['tasks'].append({
                'task_id': my_task.get_id(),
                'title': my_task.title,
                'description': my_task.description,
                'start_time': selected_task["start_time"],
                'end_time': datetime.now().isoformat(),
                'assignees': my_task.assignees,
                'priority': selected_task["priority"],
                'status': selected_task["status"],
                'history': my_task.history,
                'comments': selected_task["comments"]
            })
            Storage.save_projects(projects)
        elif choice == "4":
            console.print(f"[blue]Changing priority from [green]{selected_task['priority']}[blue] to ...")
            console.print("1. LOW")
            console.print("2. MEDIUM")
            console.print("3. HIGH")
            console.print("4. CRITICAL")
            choice_priority = Prompt.ask("Select an option", choices=["1", "2", "3", "4"])
            my_task.set_id(task_id)
            my_task.already_history(selected_task["history"])
            log1.info(f"{current_user} changed priority the task {task_id} in the project {project_id}")
            if choice_priority == "1":
                my_task.update_priority(TaskPriority.LOW.name)
            elif choice_priority == "2":
                my_task.update_priority(TaskPriority.MEDIUM.name)
            elif choice_priority == "3":
                my_task.update_priority(TaskPriority.HIGH.name)
            elif choice_priority == "4":
                my_task.update_priority(TaskPriority.CRITICAL.name)
            my_task.add_history(f"priority update to {my_task.priority}", current_user, datetime.now().isoformat())

            project['tasks'].append({
                'task_id': my_task.get_id(),
                'title': my_task.title,
                'description': my_task.description,
                'start_time': selected_task["start_time"],
                'end_time': selected_task['end_time'],
                'assignees': my_task.assignees,
                'priority': my_task.priority,
                'status': selected_task["status"],
                'history': my_task.history,
                'comments': selected_task["comments"]
            })
            Storage.save_projects(projects)
        elif choice == "5":
            console.print(f"[blue]Changing status from [green]{selected_task["status"]}[blue] to ...")
            console.print("1. BACKLOG")
            console.print("2. TODO")
            console.print("3. DOING")
            console.print("4. DONE")
            console.print("5. ARCHIVED")
            choice_status = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"])
            my_task.set_id(task_id)
            my_task.already_history(selected_task["history"])
            log1.info(f"{current_user} changed status the task {task_id} in the project {project_id}")
            if choice_status == "1":
                my_task.update_status(TaskStatus.BACKLOG.name)
            elif choice_status == "2":
                my_task.update_status(TaskStatus.TODO.name)
            elif choice_status == "3":
                my_task.update_status(TaskStatus.DOING.name)
            elif choice_status == "4":
                my_task.update_status(TaskStatus.DONE.name)
            elif choice_status == "5":
                my_task.update_status(TaskStatus.ARCHIVED.name)
            my_task.add_history(f"status update to {my_task.status}", current_user, datetime.now().isoformat())

            project['tasks'].append({
                'task_id': my_task.get_id(),
                'title': my_task.title,
                'description': my_task.description,
                'start_time': selected_task["start_time"],
                'end_time': selected_task['end_time'],
                'assignees': my_task.assignees,
                'priority': selected_task["priority"],
                'status': my_task.status,
                'history': my_task.history,
                'comments': selected_task["comments"]
            })
            Storage.save_projects(projects)
        elif choice == "6":
            my_task.set_id(task_id)
            my_task.already_comment(selected_task["comments"])
            content = Prompt.ask("Enter comment")
            my_task.add_comment(current_user, content)
            log1.info(f"{current_user} add comment the task {task_id} in the project {project_id}")
            my_task.already_history(selected_task["history"])
            my_task.add_history("comment", current_user, datetime.now().isoformat())
            project['tasks'].append({
                'task_id': my_task.get_id(),
                'title': my_task.title,
                'description': my_task.description,
                'start_time': selected_task["start_time"],
                'end_time': selected_task['end_time'],
                'assignees': my_task.assignees,
                'priority': selected_task["priority"],
                'status': selected_task["status"],
                'history': my_task.history,
                'comments': my_task.comments
            })
            Storage.save_projects(projects)
        elif choice == "7":
            if current_user != project['owner']:
                console.print("Error: Only the project owner can remove member from task.", style="bold red")
                log1.error(f"{current_user} cant remove member from task {task_id}")
                return
            my_task.set_id(task_id)

            member_removed = Prompt.ask("Enter username")
            if member_removed not in project['members'] + [""]:
                console.print("Error: All assignees must be project members.", style="bold red")
                log1.info(f"{current_user} can not remove member in the task {task_id} in the project {project_id}")

            if member_removed == current_user:
                return
            my_task.unassign_user(member_removed)
            log1.info(f"{current_user} remove member from task {task_id} in the project {project_id}")
            my_task.already_history(selected_task["history"])
            my_task.add_history("remove member", current_user, datetime.now().isoformat())
            project['tasks'].append({
                'task_id': my_task.get_id(),
                'title': my_task.title,
                'description': my_task.description,
                'start_time': selected_task["start_time"],
                'end_time': selected_task['end_time'],
                'assignees': my_task.assignees,
                'priority': selected_task["priority"],
                'status': selected_task["status"],
                'history': my_task.history,
                'comments': selected_task["comments"]
            })
            Storage.save_projects(projects)
        elif choice == "8":
            if current_user != project['owner']:
                console.print("Error: Only the project owner can add member in the task.", style="bold red")
                log1.error(f"{current_user} cant add member in the task {task_id}")
                return
            my_task.set_id(task_id)

            member_add = Prompt.ask("Enter username")
            if member_add not in project['members'] + [""]:
                console.print("Error: All assignees must be project members.", style="bold red")
                log1.info(f"{current_user} can not add member in the task {task_id} in the project {project_id}")

            if member_add == current_user:
                return
            my_task.assign_user(member_add)
            log1.info(f"{current_user} add member in the task {task_id} in the project {project_id}")
            my_task.already_history(selected_task["history"])
            my_task.add_history("add member", current_user, datetime.now().isoformat())
            project['tasks'].append({
                'task_id': my_task.get_id(),
                'title': my_task.title,
                'description': my_task.description,
                'start_time': selected_task["start_time"],
                'end_time': selected_task['end_time'],
                'assignees': my_task.assignees,
                'priority': selected_task["priority"],
                'status': selected_task["status"],
                'history': my_task.history,
                'comments': selected_task["comments"]
            })
            Storage.save_projects(projects)
        elif choice == "9":
            Storage.save_projects(projects)
            log1.info(f"task {task_id} removed")
        elif choice == "10":
            global loop_task_def
            loop_task = 1
            loop_task_def = loop_task
        elif choice == "11":
            # global loop_task_def
            loop_task = 2
            loop_task_def = loop_task


def view_project_tasks(project_id: str) -> None:
    """"Shows a list of tasks for a project"""
    projects = Storage.load_projects()

    if project_id not in projects:
        console.print("Error: Project not found.", style="bold red")
        return

    project = projects[project_id]
    tasks = project['tasks']

    table = Table(title=f"Tasks for Project {project_id}", style="bold blue")
    table.add_column('BACKLOG')
    table.add_column('TODO')
    table.add_column('DOING')
    table.add_column('DONE')
    table.add_column('ARCHIVED')
    BACKLOG = []
    TODO = []
    DOING = []
    DONE = []
    ARCHIVED = []

    for task in tasks:
        if task['status'] == 'BACKLOG':
            BACKLOG.append(task['task_id'])
        elif task['status'] == 'TODO':
            TODO.append(task['task_id'])
        elif task['status'] == 'DOING':
            DOING.append(task['task_id'])
        elif task['status'] == 'DONE':
            DONE.append(task['task_id'])
        elif task['status'] == 'ARCHIVED':
            ARCHIVED.append(task.status)

    table.add_row('\n'.join(BACKLOG), '\n'.join(TODO), '\n'.join(DOING), '\n'.join(DONE), '\n'.join(ARCHIVED))
    console.print(table)

    input_task_id = Prompt.ask("Enter task id")
    tasks = project['tasks']
    temp = 0
    select_task = {}
    for i in tasks:
        if i["task_id"] == input_task_id:
            select_task = tasks.pop(temp)
        temp += 1
    table_task = Table(title=f"Task {input_task_id}")
    table_task.add_column("Task ID", style="cyan")
    table_task.add_column("Title", style="green")
    table_task.add_column("Description")
    table_task.add_column("Start Time")
    table_task.add_column("End Time")
    table_task.add_column("Assignees")
    table_task.add_column("Priority")
    table_task.add_column("Status")

    table_task.add_row(
        select_task['task_id'],
        select_task['title'],
        select_task['description'],
        select_task['start_time'],
        select_task['end_time'],
        ", ".join(select_task['assignees']),
        select_task['priority'],
        select_task['status']
    )
    if current_user not in select_task['assignees']:
        if not ("" in select_task['assignees'] and len(select_task["assignees"]) == 1):
            console.print("if the tasks are empty or you are not member ,you can not see the task details",
                          style="bold red")
            log1.error(f"{current_user} can not see task details")
            return
    console.print(table_task)
    project['tasks'].append({
        'task_id': select_task['task_id'],
        'title': select_task['title'],
        'description': select_task['description'],
        'start_time': select_task['start_time'],
        'end_time': select_task['end_time'],
        'assignees': select_task['assignees'],
        'priority': select_task["priority"],
        'status': select_task["status"],
        'history': select_task["history"],
        'comments': select_task["comments"]
    })
    # if "" in select_task["assignees"] and len(select_task["assignees"]) == 1:
    #     return
    loop_task = 0
    edit_task(project_id, projects, loop_task, "View Project Tasks", input_task_id)


def main_menu() -> None:
    while True:
        # show menu
        console.print(f"\nWelcome {current_user}!", style="bold blue")
        console.print("1. Create Project")
        console.print("2. Project items")
        console.print("3. deactivate members")
        console.print("4. projects list ")
        console.print("5. Logout")
        choice1 = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"])

        if choice1 == "1":
            project_id = Prompt.ask("Enter project ID")
            title = Prompt.ask("Enter project title")
            create_project(project_id, title)
        elif choice1 == "2":
            loop_project = 0
            project_id = Prompt.ask("Enter project ID")

            while loop_project == 0:
                projects = Storage.load_projects()

                if project_id not in projects:
                    console.print("Error: Project not found.", style="bold red")
                    break
                check_member_project = projects[project_id]
                if current_user not in check_member_project['members']:
                    console.print("Error: Project items are only available to its members.", style="bold red")
                    log1.error(f"{current_user} could not access the project {project_id}")
                    break
                # show manage project
                console.print(f"\nManage project {project_id}", style="bold blue")
                console.print("1. Add Member to Project")
                console.print("2. Remove Member from Project")
                console.print("3. Add Task to Project")
                console.print("4. View Project Tasks")
                console.print("5. remove project")
                console.print("6. edit task")
                console.print("7. edit basic project info")
                console.print("8. back")
                console.print("9. logout")
                choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"])
                if choice == "1":
                    username = Prompt.ask("Enter username to add")
                    add_member_to_project(project_id, username)
                elif choice == "2":
                    username = Prompt.ask("Enter username to remove")
                    remove_member_from_project(project_id, username)
                elif choice == "3":
                    title = Prompt.ask("Enter task title")
                    description = Prompt.ask("Enter task description")
                    assignees = Prompt.ask("Enter assignees (comma separated)").split(", ")
                    add_task_to_project(project_id, title, description, assignees)
                elif choice == "4":
                    view_project_tasks(project_id)

                elif choice == "5":
                    remove_project(project_id)

                elif choice == "6":
                    loop_task = 0

                    edit_task(project_id, projects, loop_task, "edit Task", "")
                    if loop_task_def == 2:
                        loop_project = 2
                elif choice == "7":
                    console.print("1. edit title")
                    projects = Storage.load_projects()
                    users = Storage.load_users()
                    project = projects[project_id]
                    if current_user != project['owner']:
                        console.print("Error: Only the project owner can edited basic info", style="bold red")
                        break
                    edit_title = Prompt.ask("Enter project title")
                    project["title"] = edit_title
                    Storage.save_projects(projects)
                    log1.info(f"User {current_user} changed the title of project {project_id}")


                elif choice == "8":
                    loop_project = 1
                elif choice == "9":
                    loop_project = 2
            if loop_project == 2:
                break
        elif choice1 == "3":
            username = Prompt.ask("Enter the username to disable")
            deactivate_user(username)
        elif choice1 == "4":
            list_project()
        elif choice1 == "5":
            break


def login() -> None:
    global current_user
    while True:
        console.print("\n1. Register")
        console.print("2. Login")
        choice = Prompt.ask("Select an option", choices=["1", "2"])

        if choice == "1":
            username = Prompt.ask("Enter username")
            password = Prompt.ask("Enter password", password=False)
            email = Prompt.ask("Enter email")
            create_user(username, password, email)
        elif choice == "2":
            username = Prompt.ask("Enter username")
            password = Prompt.ask("Enter password")
            if authenticate(username, password):
                main_menu()
                current_user = None
                break
            else:
                console.print("Error: Invalid username or password.", style="bold red")


if __name__ == "__main__":
    login()
