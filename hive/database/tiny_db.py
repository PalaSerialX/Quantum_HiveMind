from tinydb import TinyDB, Query
import os
import json


class QueenBeeTaskManager:
    def __init__(self):
        # Get the directory of this Python script
        dir_path = os.path.dirname(os.path.realpath(__file__))

        # Create the path for tasks.json relative to this directory
        db_path = os.path.join(dir_path, 'tasks.json')
        self.db = TinyDB(db_path)

    def add_task(self, task_id, description, priority="medium", status="pending", unique_task_id=None, **kwargs):
        task_data = {'_id': task_id, 'description': description, 'priority': priority, 'status': status}
        if unique_task_id:
            task_data['unique_task_id'] = unique_task_id
        # Add any additional keyword arguments to the task data
        task_data.update(kwargs)
        self.db.insert(task_data)
        print(f"Task {task_id} added with priority {priority}! 🌼")

    def get_task(self, task_id):
        task = Query()
        return self.db.search(task._id == task_id)

    def get_tasks_by_status_and_type(self, status, task_type):
        task = Query()
        status_filtered_tasks = self.db.search(task.status == status)

        type_filtered_tasks = [
            task for task in status_filtered_tasks
            if task.get('category') == task_type  # Changed 'breakdown' and 'UnderstandingTask' to 'category'
        ]
        return type_filtered_tasks

    def update_task(self, task_id, updates):
        task = Query()
        # Convert any dictionaries in 'updates' to a readable JSON string
        for key, value in updates.items():
            if isinstance(value, dict):
                updates[key] = json.dumps(value, indent=4)
        self.db.update(updates, task._id == task_id)
        print(f"Task {task_id} updated in a readable format! 🌟")

    def delete_task(self, task_id):
        task = Query()
        self.db.remove(task._id == task_id)
        print(f"Task {task_id} deleted! 🌹")

    def get_tasks_by_priority(self, priority):
        task = Query()
        return self.db.search(task.priority == priority)

    def get_tasks_by_status(self, status):
        task = Query()
        return self.db.search(task.status == status)




