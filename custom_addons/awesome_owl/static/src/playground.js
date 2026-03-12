/** @odoo-module **/

import { Component, useState, markup } from "@odoo/owl";
// Exercise 2: Counter moved to its own folder
import { Counter } from "./counter/counter";
// Exercise 3 / 13 / 14: Card component
import { Card } from "./card/card";
// Exercise 7–12: Todo list
import { TodoList } from "./todo_list/todo_list";

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = { Counter, Card, TodoList };

    setup() {
        // Exercise 6: track sum of counter values, initially 2
        this.state = useState({ sum: 2 });
        // Exercise 4: markup demo – one safe (markup), one escaped (raw string)
        this.html = markup("<strong>Some <em>html</em> content</strong>");
        this.rawHtml = "<strong>This will be escaped</strong>";
    }

    // Exercise 6: called by each Counter via onChange prop
    incrementSum() {
        this.state.sum++;
    }
}
