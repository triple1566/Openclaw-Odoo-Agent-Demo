/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        const order = this.pos.getOrder();

        if (order && order.order_from === "online" && !order.getPartner()) {
            this.dialog.add(AlertDialog, {
                title: "Customer Required",
                body: "Please select a customer for Online orders.",
            });
            return;
        }

        return await super.validateOrder(isForceValidate);
    },
});