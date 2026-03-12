/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class Card extends Component {
    static template = "awesome_owl.Card";
    // Exercise 5 / 13: props validation; content removed in ex-13, use slots instead
    static props = {
        title: String,
        slots: Object,
    };

    // Exercise 14: track open/closed state
    setup() {
        this.state = useState({ isOpen: true });
    }

    toggleOpen() {
        this.state.isOpen = !this.state.isOpen;
    }
}
