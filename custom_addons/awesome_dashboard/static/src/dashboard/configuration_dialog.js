/** @odoo-module **/

/**
 * Exercise 11: ConfigurationDialog
 *
 * Lists every registered dashboard item with a checkbox.
 * The user can uncheck items to hide them.
 * Clicking Apply saves the hidden-id list to localStorage.
 */

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class ConfigurationDialog extends Component {
    static template = "awesome_dashboard.ConfigurationDialog";
    static components = { Dialog };
    static props = {
        items: Array,
        hiddenIds: Array,
        onApply: Function,
        // 'close' is injected automatically by the dialog service
        close: Function,
    };

    setup() {
        // Work with a local copy so the user can cancel without side-effects.
        this.state = useState({
            hiddenIds: [...this.props.hiddenIds],
        });
    }

    isVisible(itemId) {
        return !this.state.hiddenIds.includes(itemId);
    }

    toggleItem(itemId) {
        const idx = this.state.hiddenIds.indexOf(itemId);
        if (idx >= 0) {
            this.state.hiddenIds.splice(idx, 1);
        } else {
            this.state.hiddenIds.push(itemId);
        }
    }

    apply() {
        this.props.onApply([...this.state.hiddenIds]);
        this.props.close();
    }
}
