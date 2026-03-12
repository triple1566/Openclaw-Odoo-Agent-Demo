/** @odoo-module **/

/**
 * Exercise 9: PieChartCard — thin wrapper that pairs a heading with PieChart.
 */

import { Component } from "@odoo/owl";
import { PieChart } from "./pie_chart";

export class PieChartCard extends Component {
    static template = "awesome_dashboard.PieChartCard";
    static components = { PieChart };
    static props = {
        title: { type: String, optional: true },
        // data passed directly to PieChart: { label: value }
        data: Object,
    };
}
