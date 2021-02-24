import asyncio
import dashborg

class TodoModel:
    def __init__(self):
        self.todo_list = []
        self.next_id = 1

    async def root_handler(self, req):
        await req.set_html_from_file("demo.html")
        return

    async def add_todo(self, req):
        # Clear Errors and Todos
        req.set_data("$.data.errors", None)
        req.set_data("$.data.newtodo", None)

        # Validate
        todotype = req.panel_state.get("todotype")
        if todotype is None or todotype == "":
            req.set_data("$.data.errors", "Please select a Todo Type")
            return
        item = req.panel_state.get("item")
        if item is None or item == "":
            req.set_data("$.data.errors", "Please enter a Todo Item")
            return

        # Create a new Todo Item
        new_todo = {"id": self.next_id, "type": todotype, "item": item, "done": False}
        self.todo_list.append(new_todo)
        self.next_id += 1

        # Invalidate the Todo List to force a re-fetch
        req.invalidate_data("/get-todo-list")
        return

    async def get_todo_list(self, datareq):
        return self.todo_list

    async def mark_todo_done(self, req):
        if req.data is None:
            return
        todo_id = int(req.data)
        for t in self.todo_list:
            if t["id"] == todo_id:
                t["done"] = True
        req.invalidate_data("/get-todo-list")
        return

    async def remove_todo(self, req):
        if req.data is None:
            return
        todo_id = int(req.data)
        self.todo_list = [t for t in self.todo_list if t["id"] != todo_id]
        req.invalidate_data("/get-todo-list")
        return

async def main():
    config = dashborg.Config(proc_name="demo", anon_acc=True, auto_keygen=True)
    await dashborg.start_proc_client(config)
    model = TodoModel()
    await dashborg.register_panel_handler("default", "/", model.root_handler)
    await dashborg.register_panel_handler("default", "/add-todo", model.add_todo)
    await dashborg.register_data_handler("default", "/get-todo-list", model.get_todo_list)
    await dashborg.register_panel_handler("default", "/mark-todo-done", model.mark_todo_done)
    await dashborg.register_panel_handler("default", "/remove-todo", model.remove_todo)
    while True:
        await asyncio.sleep(1)

asyncio.run(main())