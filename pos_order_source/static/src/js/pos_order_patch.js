/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

patch(PosOrder.prototype, {
    setup(vals) {
        super.setup(...arguments);

        if (!this.order_from) {
            this.order_from = "offline";
        }
    },

    serializeForORM(opts = {}) {
        const data = super.serializeForORM(opts);
        data.order_from = this.order_from || "offline";
        return data;
    },

    get orderSourceLabel() {
        return this.order_from === "online" ? "Online" : "Offline";
    },

    get displayOrderSourceName() {
        const baseName =
            this.floating_order_name ||
            (this.tracking_number ? this.tracking_number.toString() : this.name || "/");

        const partnerName = this.getPartner()?.name;

        if (partnerName) {
            return `${baseName} - ${partnerName} (${this.orderSourceLabel})`;
        }

        return `${baseName} (${this.orderSourceLabel})`;
    },

    get floatingOrderName() {
        return this.displayOrderSourceName;
    },
});