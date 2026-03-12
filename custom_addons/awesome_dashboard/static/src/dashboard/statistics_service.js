/** @odoo-module **/

/**
 * Exercise 5 / 7: Statistics service.
 *
 * - Exercise 5: uses memoize so the rpc is only fired once per navigation,
 *   regardless of how many components call loadStatistics().
 * - Exercise 7: a reactive object is returned so Dashboard can useState() on
 *   it and be automatically re-rendered whenever data refreshes.
 *   A setInterval reloads fresh data every 10 minutes (change to 10_000ms to
 *   test quickly).
 */

import { registry } from "@web/core/registry";
import { memoize } from "@web/core/utils/functions";
import { reactive } from "@odoo/owl";

const statisticsService = {
    dependencies: ["rpc"],

    start(env, { rpc }) {
        const statistics = reactive({});

        // memoize caches the promise so repeated calls skip the network hit.
        const loadStatistics = memoize(async () => {
            const data = await rpc("/awesome_dashboard/statistics");
            Object.assign(statistics, data);
        });

        // Fire the first load immediately; catch so a network error during
        // app boot does not cause an unhandled rejection that crashes the
        // client in debug/assets-debug mode.
        loadStatistics().catch(console.error);

        // Exercise 7: refresh every 10 minutes.
        // Set to 10_000 (10 s) while developing so you can observe it.
        setInterval(() => {
            rpc("/awesome_dashboard/statistics")
                .then((data) => Object.assign(statistics, data))
                .catch(console.error);
        }, 10 * 60 * 1000);

        return { statistics, loadStatistics };
    },
};

registry.category("services").add("awesome_dashboard.statistics", statisticsService);
