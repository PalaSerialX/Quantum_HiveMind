from tinydb import TinyDB, Query
import os


class QueenBeeTaskManager:
    def __init__(self):
        # Get the directory of this Python script
        dir_path = os.path.dirname(os.path.realpath(__file__))

        # Create the path for tasks.json relative to this directory
        db_path = os.path.join(dir_path, 'tasks.json')
        self.db = TinyDB(db_path)

    def add_task(self, task_id, description, priority="medium", status="pending"):
        self.db.insert({'_id': task_id, 'description': description, 'priority': priority, 'status': status})
        print(f"Task {task_id} added with priority {priority}! 🌼")

    def get_task(self, task_id):
        Task = Query()
        return self.db.search(Task._id == task_id)

    def get_tasks_by_status_and_type(self, status, task_type):
        Task = Query()
        status_filtered_tasks = self.db.search(Task.status == status)
        type_filtered_tasks = [task for task in status_filtered_tasks if
                               task.get('breakdown', {}).get('UnderstandingTask') == task_type]


        return type_filtered_tasks

    def update_task(self, task_id, updates):
        Task = Query()
        self.db.update(updates, Task._id == task_id)
        print(f"Task {task_id} updated! 🌟")

    def delete_task(self, task_id):
        Task = Query()
        self.db.remove(Task._id == task_id)
        print(f"Task {task_id} deleted! 🌹")

    def get_tasks_by_priority(self, priority):
        Task = Query()
        return self.db.search(Task.priority == priority)

    def get_tasks_by_status(self, status):
        Task = Query()
        return self.db.search(Task.status == status)




