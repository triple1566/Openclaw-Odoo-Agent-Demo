/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useAutofocus } from "../utils";

// Exercise 7 / 8 / 11 / 12: TodoItem sub-component
export class TodoItem extends Component {
    static template = "awesome_owl.TodoItem";
    // Exercise 7 / 11 / 12: props validation
    static props = {
        todo: {
            type: Object,
            shape: {
                id: Number,
                description: String,
                isCompleted: Boolean,
            },
        },
        toggleState: Function,  // Exercise 11
        removeTodo: Function,   // Exercise 12
    };

    // Exercise 11: called when checkbox changes
    onToggle() {
        this.props.toggleState(this.props.todo.id);
    }

    // Exercise 12: called when remove icon is clicked
    onRemove() {
        this.props.removeTodo(this.props.todo.id);
    }
}

// Exercise 7 / 9 / 10 / 11 / 12: TodoList parent component
export class TodoList extends Component {
    static template = "awesome_owl.TodoList";
    static components = { TodoItem };

    setup() {
        // Exercise 9: start with an empty list
        this.todos = useState([]);
        this.nextId = 1;
        // Exercise 10: auto-focus the input on mount via the useAutofocus hook
        useAutofocus("input");
    }

    // Exercise 9: add a todo on Enter key
    addTodo(ev) {
        if (ev.keyCode === 13 && ev.target.value.trim()) {
            this.todos.push({
                id: this.nextId++,
                description: ev.target.value.trim(),
                isCompleted: false,
            });
            ev.target.value = "";
        }
    }

    // Exercise 11: toggle isCompleted for a given id
    toggleState(todoId) {
        const todo = this.todos.find((t) => t.id === todoId);
        if (todo) {
            todo.isCompleted = !todo.isCompleted;
        }
    }

    // Exercise 12: remove a todo by id
    removeTodo(todoId) {
        const index = this.todos.findIndex((t) => t.id === todoId);
        if (index >= 0) {
            this.todos.splice(index, 1);
        }
    }
}
