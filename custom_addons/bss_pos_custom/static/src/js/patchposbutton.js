/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

patch(ProductScreen.prototype, {
    setup() {
        super.setup(...arguments);
        const order = this.pos.getOrder();
        if (order && !this.showOnlineButton()) {
            order.order_from = "offline";
        }
    },

    onClickOnlineButton() {
        const order = this.pos.getOrder();
        if (!order || !this.showOnlineButton()) {
            return;
        }
        order.order_from = this.getOrderSource(order) === "online" ? "offline" : "online";
        this.render();
    },

    showOnlineButton() {
        return !!this.pos?.config?.show_order_button;
    },

    getOrderSource(order) {
        if (!this.showOnlineButton()) {
            if (order) {
                order.order_from = "offline";
            }
            return "offline";
        }
        return order?.order_from === "online" ? "online" : "offline";
    },

    getOnlineButtonStyle() {
        const order = this.pos.getOrder();
        return this.getOrderSource(order) === "online" ? "color:red;" : "";
    },

    getOrderTopLabel() {
        const order = this.pos.getOrder();
        if (!order) {
            return "";
        }

        const sourceLabel = this.getOrderSource(order) === "online" ? "Online" : "Offline";
        const orderName = order.getName ? order.getName() : order.name || "";
        const partnerName = order.getPartner ? order.getPartner()?.name : "";

        if (partnerName) {
            return `${orderName} - ${partnerName} (${sourceLabel})`;
        }
        return `${orderName} (${sourceLabel})`;
    },

});