/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        const order = this.pos.getOrder();
        if (!order) {
            return super.validateOrder(isForceValidate);
        }

        if (!this.pos?.config?.show_order_button) {
            order.order_from = "offline";
            return super.validateOrder(isForceValidate);
        }

        const source = order.order_from === "online" ? "online" : "offline";
        if (source === "online" && !order.getPartner()) {
            this.dialog.add(AlertDialog, {
                title: "Warning",
                body: "Please select a customer for Online orders.",
            });
            return;
        }

        return super.validateOrder(isForceValidate);
    },
});
