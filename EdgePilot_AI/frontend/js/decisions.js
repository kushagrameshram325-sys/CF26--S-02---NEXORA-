function renderDecisions(
    decisions = []
) {

    const container =
        document.getElementById(
            "decisionList"
        );


    if (!container) {
        return;
    }


    if (!decisions.length) {

        container.innerHTML = `

            <div class="empty-state">
                No scheduler decisions available.
            </div>

        `;

        return;
    }


    container.innerHTML =
        decisions.slice(0, 10)
            .map(decision => {

                const status =
                    decision.status ||
                    "success";


                const icon =
                    status === "warning"
                        ? "!"
                        : status === "critical"
                            ? "×"
                            : "✓";


                return `

                    <div class="decision-row">

                        <div
                            class="
                                decision-status
                                ${status}
                            "
                        >
                            ${icon}
                        </div>


                        <div class="decision-body">

                            <strong>
                                ${
                                    decision.workload ||
                                    decision.workload_id ||
                                    "Workload"
                                }
                            </strong>

                            <span>
                                ${
                                    decision.reason ||
                                    `Selected ${
                                        decision.node ||
                                        decision.selected_node ||
                                        "node"
                                    }`
                                }
                            </span>

                        </div>


                        <div class="decision-score">

                            ${
                                decision.score ??
                                "--"
                            }

                        </div>

                    </div>

                `;

            }).join("");
}


function renderDecisionTable(
    decisions = []
) {

    const table =
        document.getElementById(
            "decisionTable"
        );


    if (!table) {
        return;
    }


    table.innerHTML =
        decisions.map(
            decision => `

                <tr>

                    <td>
                        ${
                            decision.time ||
                            "--"
                        }
                    </td>

                    <td>
                        ${
                            decision.workload ||
                            decision.workload_id ||
                            "--"
                        }
                    </td>

                    <td>
                        ${
                            decision.node ||
                            decision.selected_node ||
                            "--"
                        }
                    </td>

                    <td>
                        ${
                            decision.score ??
                            "--"
                        }
                    </td>

                    <td>
                        ${
                            decision.risk ??
                            "--"
                        }
                    </td>

                    <td>
                        ${
                            decision.action ||
                            "Scheduled"
                        }
                    </td>

                </tr>

            `
        ).join("");


    if (!decisions.length) {

        table.innerHTML = `

            <tr>

                <td
                    colspan="6"
                    class="empty-state"
                >
                    No decisions available.
                </td>

            </tr>

        `;

    }

}


window.renderDecisions =
    renderDecisions;


window.renderDecisionTable =
    renderDecisionTable;