/** @odoo-module **/

/**
 * Exercise 8: Lazy loader for the AwesomeDashboard.
 *
 * This thin wrapper lives in web.assets_backend (always loaded) and is
 * registered to the "actions" registry under the tag "awesome_dashboard".
 *
 * When Odoo navigates to the tag it renders this component, which triggers
 * LazyComponent to:
 *   1. Download the awesome_dashboard.dashboard_assets bundle (once only).
 *   2. Look up "AwesomeDashboard" in the lazy_components registry.
 *   3. Replace itself with the real AwesomeDashboard component.
 */

import { Component, xml } from "@odoo/owl";
import { LazyComponent } from "@web/core/assets";
import { registry } from "@web/core/registry";

class AwesomeDashboardAction extends Component {
    static components = { LazyComponent };
    static template = xml`
        <LazyComponent
            bundle="'awesome_dashboard.dashboard_assets'"
            Component="'AwesomeDashboard'"
        />
    `;
}

registry.category("actions").add("awesome_dashboard", AwesomeDashboardAction);
