from flask import Flask, render_template, request, session, redirect
import json
import re
import uuid


app = Flask(__name__)
app.secret_key = "5c8fce510fa3c5f9bb251cd1b13fd6eb"

todos = []

def load_saved_todos():
    # Call global todos list to load json to
    global todos
    # Try to open existing file or catch exception and create it
    try:
        with open('todos.json') as f:
            todos = json.load(f)
    except (OSError, IOError):
        with open('todos.json', 'w') as f:
            json.dump(todos, f)


# Call the load_saved_todos method
load_saved_todos()

# Index route
@app.route('/')
def index():
    return render_template("todoapp.html",
                           todos=todos,
                           errors=session.pop("errors", None),
                           alert=session.pop("alert", None)
                           )

# Submit route
@app.route("/submit", methods=["POST"])
def submit():
    def validate():
        """Function to validate the to-do data."""
        # Dictionary to store error messages and original input in
        validation_errors = {"messages": {}, "input": {}}

        # Validate task input field
        if (request.form["task"].strip() == ""):
            validation_errors["messages"].update(
                {"task": "Task is a required field."})

        # Validate email input field with regex
        if not re.search(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$',
                         request.form["email"]):
            validation_errors["messages"].update(
                {"email": "A valid email address is required."})

        # Validate priority input field is an option in list
        if request.form["priority"] not in ["Low", "Medium", "High"]:
            validation_errors["messages"].update(
                {"priority": "Please select a priority from the list."})

        # If there are messages in the dictionary, add the original input
        if validation_errors["messages"]:
            validation_errors.update({"input": dict(request.form)})
        # Otherwise reset the dictionary to empty
        else:
            validation_errors = {}

        # Return the dictionary
        return validation_errors

    # Call the validate function and store the return value in a variable
    validation = validate()

    # If the dictionary is empty, append the to-do to the global todos list
    if not validation:
        # Generate a unique ID for the to-do, used for deleting to-dos
        todo_id = str(uuid.uuid4())
        # Append the to-do to the global todos list
        todos.append({
            "id": todo_id,
            "task": request.form["task"],
            "email": request.form["email"],
            "priority": request.form["priority"]
        })

        # Add an alert message to the session to be displayed on the page
        session["alert"] = {
            "level": "success",
            "message": "To-Do item added, make sure you save your changes!"
        }

        # Redirect back to the index and scroll to the new to-do item
        return redirect("/#todo-"+todo_id)
    # Otherwise redirect back and display the error messages
    else:
        # Add the errors to be displayed to the session
        session["errors"] = validation
        # Redirect back to the index and scroll to the add-todo element
        return redirect("/#add-todo")

# Clear route
@app.route("/clear", methods=["POST"])
def clear():
    """Function to clear the todos list."""
    # Call global todos list
    global todos

    # Check if the todos list has to-dos, if it does clear the list
    if len(todos) > 0:
        todos = []
        # Add an alert message to the session to be displayed on the page
        session["alert"] = {
            "level": "info",
            "message": "To-Do list cleared!"
        }
    # Otherwise add an alert message to the session to be displayed on the
    # page letting the user know there were no to-dos to clear
    else:
        session["alert"] = {
            "level": "info",
            "message": "To-Do list already empty, nothing to clear!"
        }

    # Redirect back to the index
    return redirect("/")

# Save route
@app.route("/save", methods=["POST"])
def save():
    """Function to save the todos list to todos.json."""
    # Open todos.json in write mode and dump the todos into it
    with open('todos.json', 'w') as f:
        json.dump(todos, f)

    # Add an alert message to the session to be displayed on the page
    session["alert"] = {
        "level": "success",
        "message": "To-Do list saved!"
    }

    # Redirect back to the index
    return redirect("/")

# Delete route
@app.route("/delete/<todo_id>")
def delete(todo_id):
    """Function to delete a to-do from the todos list."""
    # Call global todos list
    global todos

    # Filter the todos list to return to-dos that don't match the todo_id
    todos = list(
        filter(lambda todo, todo_id=todo_id: todo["id"] != todo_id, todos))

    # Add an alert message to the session to be displayed on the page
    session["alert"] = {
        "level": "info",
        "message": "To-Do deleted!"
    }

    # Redirect back to the index
    return redirect("/")


if __name__ == '__main__':
    app.run()