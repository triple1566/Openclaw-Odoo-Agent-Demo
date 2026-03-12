/** @odoo-module **/

/**
 * Exercise 9: NumberCard — displays a single statistic as a title + value pair.
 */

import { Component } from "@odoo/owl";

export class NumberCard extends Component {
    static template = "awesome_dashboard.NumberCard";
    static props = {
        title: String,
        value: [String, Number],
    };
}
