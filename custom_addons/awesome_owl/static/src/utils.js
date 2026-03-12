/** @odoo-module **/

import { useRef, onMounted } from "@odoo/owl";

/**
 * Exercise 10: Custom hook that auto-focuses a ref'd element on mount.
 * @param {string} refName - the t-ref name used in the template
 */
export function useAutofocus(refName) {
    const ref = useRef(refName);
    onMounted(() => {
        if (ref.el) {
            ref.el.focus();
        }
    });
}
