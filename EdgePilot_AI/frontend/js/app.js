document.addEventListener(
    "DOMContentLoaded",
    async () => {

        initializeNavigation();

        await initializeDashboard();

        setupSimulationPage();

        setupSchedulerPage();

        startLiveUpdates();

    }
);


function initializeNavigation() {

    const currentPath =
        window.location.pathname;


    document
        .querySelectorAll(".nav-link")
        .forEach(link => {

            const href =
                link.getAttribute("href");


            if (
                currentPath.endsWith(
                    href.replace("../", "")
                )
            ) {

                link.classList.add(
                    "active"
                );

            }

        });

}


async function initializeDashboard() {

    const state =
        await api.getState();


    if (state) {

        updateDashboardMetrics(
            state
        );

    }


    const nodes =
        await api.getNodes();


    if (
        nodes &&
        typeof renderNodes ===
        "function"
    ) {

        renderNodes(nodes);

    }


    const decisions =
        await api.getDecisions();


    if (
        decisions &&
        typeof renderDecisions ===
        "function"
    ) {

        renderDecisions(
            decisions
        );

    }


    const events =
        await api.getEvents();


    if (
        events &&
        typeof renderEvents ===
        "function"
    ) {

        renderEvents(
            events
        );

    }


    const metrics =
        await api.getMetrics();


    if (
        metrics &&
        typeof renderMetrics ===
        "function"
    ) {

        renderMetrics(
            metrics
        );

    }


    if (
        typeof renderTopology ===
        "function"
    ) {

        renderTopology(
            nodes || []
        );

    }

}


function updateDashboardMetrics(
    state
) {

    const nodeCount =
        document.getElementById(
            "nodeCount"
        );


    const workloadCount =
        document.getElementById(
            "workloadCount"
        );


    const cpu =
        document.getElementById(
            "cpuUsage"
        );


    const latency =
        document.getElementById(
            "latency"
        );


    const faults =
        document.getElementById(
            "faultCount"
        );


    if (nodeCount) {

        nodeCount.textContent =
            state.node_count ??
            state.nodes?.length ??
            0;

    }


    if (workloadCount) {

        workloadCount.textContent =
            state.workload_count ??
            state.workloads?.length ??
            0;

    }


    if (cpu) {

        cpu.textContent =
            `${state.cpu ?? 0}%`;

    }


    if (latency) {

        latency.textContent =
            `${state.latency ?? 0} ms`;

    }


    if (faults) {

        faults.textContent =
            state.active_faults ??
            state.faults ??
            0;

    }

}


function setupSimulationPage() {

    if (
        typeof setupSimulation ===
        "function"
    ) {

        setupSimulation();

    }

}


function setupSchedulerPage() {

    const refresh =
        document.getElementById(
            "refreshDecisions"
        );


    if (!refresh) {
        return;
    }


    refresh.addEventListener(
        "click",
        async () => {

            const decisions =
                await api.getDecisions();


            if (
                typeof renderDecisionTable ===
                "function"
            ) {

                renderDecisionTable(
                    decisions || []
                );

            }

        }
    );

}


function startLiveUpdates() {

    setInterval(
        async () => {

            const state =
                await api.getState();


            if (state) {

                updateDashboardMetrics(
                    state
                );

            }


            const nodes =
                await api.getNodes();


            if (
                nodes &&
                typeof renderNodes ===
                "function"
            ) {

                renderNodes(nodes);

            }


            const decisions =
                await api.getDecisions();


            if (
                decisions &&
                typeof renderDecisions ===
                "function"
            ) {

                renderDecisions(
                    decisions
                );

            }

        },

        5000
    );

}


window.updateDashboardMetrics =
    updateDashboardMetrics;