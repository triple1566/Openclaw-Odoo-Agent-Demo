/** @odoo-module **/

/**
 * Exercises 9 / 10: Dashboard item registry.
 *
 * Each entry is registered to the "awesome_dashboard" registry category.
 * The Dashboard component reads this registry at runtime, so other Odoo
 * addons can add items simply by registering here.
 *
 * Item shape:
 *   id          – unique string key
 *   description – human-readable label shown in the config dialog
 *   Component   – Owl component to render inside a DashboardItem
 *   size        – (optional) number, passed as DashboardItem's `size` prop
 *   props       – (optional) (statistics) => propsObject
 *                 If omitted the full statistics object is passed as `data`.
 */

import { registry } from "@web/core/registry";
import { NumberCard } from "./number_card";
import { PieChartCard } from "./pie_chart_card";

const dashboardRegistry = registry.category("awesome_dashboard");

dashboardRegistry.add("new_orders_count", {
    id: "new_orders_count",
    description: "New Orders This Month",
    Component: NumberCard,
    props: (data) => ({
        title: "New Orders This Month",
        value: data.new_orders_count ?? "—",
    }),
});

dashboardRegistry.add("new_orders_amount", {
    id: "new_orders_amount",
    description: "Total Amount of New Orders",
    Component: NumberCard,
    props: (data) => ({
        title: "Total Amount of New Orders",
        value: data.new_orders_amount != null
            ? `$ ${data.new_orders_amount.toFixed(2)}`
            : "—",
    }),
});

dashboardRegistry.add("average_quantity", {
    id: "average_quantity",
    description: "Average T-Shirts per Order",
    Component: NumberCard,
    props: (data) => ({
        title: "Average T-Shirts per Order",
        value: data.average_quantity != null
            ? data.average_quantity.toFixed(1)
            : "—",
    }),
});

dashboardRegistry.add("cancelled_orders", {
    id: "cancelled_orders",
    description: "Cancelled Orders This Month",
    Component: NumberCard,
    props: (data) => ({
        title: "Cancelled Orders This Month",
        value: data.cancelled_orders ?? "—",
    }),
});

dashboardRegistry.add("average_time", {
    id: "average_time",
    description: "Average Processing Time (days)",
    Component: NumberCard,
    props: (data) => ({
        title: "Avg. Processing Time (days)",
        value: data.average_time != null ? data.average_time.toFixed(1) : "—",
    }),
});

dashboardRegistry.add("orders_by_size", {
    id: "orders_by_size",
    description: "T-Shirt Orders by Size (pie chart)",
    Component: PieChartCard,
    size: 2,
    props: (data) => ({
        title: "T-Shirt Orders by Size",
        data: data.orders_by_size || {},
    }),
});
