/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";

patch(ControlButtons.prototype, {
    onClickOrderSource() {
        const order = this.pos.getOrder();

        if (!order) {
            alert("No current order found");
            return;
        }

        const current = order.order_from || "offline";
        order.order_from = current === "online" ? "offline" : "online";
        this.render();
    },

    isOrderSourceOnline() {
        const order = this.pos.getOrder();
        return !!order && (order.order_from || "offline") === "online";
    },

    getOrderSourceLabel() {
        const order = this.pos.getOrder();
        if (!order) {
            return "OFFLINE";
        }
        return (order.order_from || "offline") === "online" ? "ONLINE" : "OFFLINE";
    },

    shouldShowOrderSourceButton() {
        return !!this.pos?.config?.show_order_source_button;
    },
});