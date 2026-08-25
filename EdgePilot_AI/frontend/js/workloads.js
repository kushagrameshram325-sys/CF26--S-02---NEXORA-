function renderWorkloads(
    workloads = []
) {

    const container =
        document.getElementById(
            "workloadList"
        );


    if (!container) {
        return;
    }


    if (!workloads.length) {

        container.innerHTML = `

            <div class="empty-state">
                No workloads available.
            </div>

        `;

        return;
    }


    container.innerHTML =
        workloads.map(workload => {

            const status =
                workload.status ||
                "running";


            const statusClass =
                status.toLowerCase()
                    .replace(/\s+/g, "-");


            return `

                <div class="workload-row">

                    <div>

                        <strong>
                            ${workload.id}
                        </strong>

                        <span>
                            ${
                                workload.name ||
                                workload.type ||
                                "Edge workload"
                            }
                        </span>

                    </div>


                    <span
                        class="
                            workload-status
                            ${statusClass}
                        "
                    >
                        ${status}
                    </span>


                    <span>
                        ${
                            workload.node_id ||
                            workload.node ||
                            "Unassigned"
                        }
                    </span>

                </div>

            `;

        }).join("");
}


window.renderWorkloads =
    renderWorkloads;