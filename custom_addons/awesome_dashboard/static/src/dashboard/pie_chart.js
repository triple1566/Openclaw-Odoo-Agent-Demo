/** @odoo-module **/

/**
 * Exercise 6: PieChart component.
 *
 * Lazy-loads Chart.js (not part of the standard backend bundle) before
 * mounting, then draws a pie chart on a <canvas> element.
 */

import { Component, onWillStart, onMounted, useRef } from "@odoo/owl";
import { loadJS } from "@web/core/assets";

export class PieChart extends Component {
    static template = "awesome_dashboard.PieChart";
    static props = {
        // Plain object mapping label → numeric value, e.g. { S: 22, M: 48 }
        data: Object,
    };

    setup() {
        this.canvasRef = useRef("canvas");

        onWillStart(async () => {
            // Lazy-load Chart.js only when this component is first used.
            await loadJS("/web/static/lib/Chart/Chart.js");
        });

        onMounted(() => {
            const { data } = this.props;
            new Chart(this.canvasRef.el, {
                type: "pie",
                data: {
                    labels: Object.keys(data),
                    datasets: [
                        {
                            data: Object.values(data),
                            backgroundColor: [
                                "#FF6384",
                                "#36A2EB",
                                "#FFCE56",
                                "#4BC0C0",
                                "#9966FF",
                            ],
                        },
                    ],
                },
                options: {
                    responsive: true,
                    legend: { position: "bottom" },
                },
            });
        });
    }
}
