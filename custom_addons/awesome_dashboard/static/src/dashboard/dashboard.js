/** @odoo-module **/

/**
 * Main AwesomeDashboard component — exercises 1–11.
 *
 * Ex 1:  Uses Layout for control panel + content area.
 * Ex 2:  Customers and Leads navigation buttons.
 * Ex 3:  Renders DashboardItem wrappers.
 * Ex 4:  Calls /awesome_dashboard/statistics via rpc in onWillStart.
 * Ex 5:  Delegates rpc + caching to the statistics service.
 * Ex 6:  Displays a PieChart card (via dashboard_items registry).
 * Ex 7:  useState on the reactive statistics object → auto-refresh.
 * Ex 8:  Registered to lazy_components; loaded via LazyComponent bundle.
 * Ex 9:  Iterates a list of item descriptors (NumberCard / PieChartCard).
 * Ex 10: Reads items from the "awesome_dashboard" registry.
 * Ex 11: Settings dialog lets users show/hide items; stored in localStorage.
 */

import { Component, useState, onWillStart } from "@odoo/owl";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { DashboardItem } from "./dashboard_item";
import { ConfigurationDialog } from "./configuration_dialog";

const STORAGE_KEY = "awesome_dashboard.hidden_ids";

export class AwesomeDashboard extends Component {
    static template = "awesome_dashboard.Dashboard";
    static components = { Layout, DashboardItem };

    setup() {
        // Exercise 2: action service for navigation buttons
        this.action = useService("action");

        // Exercise 11: dialog service for settings modal
        this.dialog = useService("dialog");

        // Exercises 5 + 7: statistics service returns a reactive object
        const statsService = useService("awesome_dashboard.statistics");
        this.statistics = useState(statsService.statistics);

        // Exercise 4 / 5: await the first load so the dashboard isn't empty
        onWillStart(() => statsService.loadStatistics());

        // Exercise 10: read all items from the registry
        this.allItems = registry.category("awesome_dashboard").getAll();

        // Exercise 11: persist hidden-item IDs in localStorage
        const savedHidden = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
        this.configState = useState({ hiddenIds: savedHidden });
    }

    /** Items currently shown (not hidden by the user). */
    get visibleItems() {
        return this.allItems.filter(
            (item) => !this.configState.hiddenIds.includes(item.id)
        );
    }

    // ── Exercise 2: navigation buttons ──────────────────────────────────────

    openCustomers() {
        // Opens a kanban view of all customers (res.partner with customer_rank > 0)
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Customers",
            res_model: "res.partner",
            views: [[false, "kanban"], [false, "list"], [false, "form"]],
            domain: [["customer_rank", ">", 0]],
        });
    }

    openLeads() {
        // Opens a list + form view on crm.lead (requires crm module)
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Leads",
            res_model: "crm.lead",
            views: [[false, "list"], [false, "form"]],
        });
    }

    // ── Exercise 11: settings dialog ────────────────────────────────────────

    openSettings() {
        this.dialog.add(ConfigurationDialog, {
            items: this.allItems,
            hiddenIds: [...this.configState.hiddenIds],
            onApply: (hiddenIds) => {
                this.configState.hiddenIds = hiddenIds;
                localStorage.setItem(STORAGE_KEY, JSON.stringify(hiddenIds));
            },
        });
    }
}

// Exercise 8: register to lazy_components so the LazyComponent wrapper can
// look it up by name after loading the bundle.
registry.category("lazy_components").add("AwesomeDashboard", AwesomeDashboard);
