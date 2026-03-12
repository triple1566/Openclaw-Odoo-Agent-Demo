/** @odoo-module **/

/**
 * Exercise 3: Generic DashboardItem component.
 *
 * Wraps its default slot in a Bootstrap card-like container.
 * The width is derived from the optional `size` prop (default 1).
 * width = 18 * size rem.
 */

import { Component } from "@odoo/owl";

export class DashboardItem extends Component {
    static template = "awesome_dashboard.DashboardItem";
    static props = {
        size: { type: Number, optional: true },
        slots: Object,
    };
    static defaultProps = { size: 1 };

    get style() {
        return `width: ${18 * (this.props.size || 1)}rem;`;
    }
}
