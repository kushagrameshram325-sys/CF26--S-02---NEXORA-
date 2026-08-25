const API_BASE =
    window.EDGEPILOT_API ||
    "http://localhost:8000/api";


async function apiRequest(
    endpoint,
    options = {}
) {

    try {

        const response = await fetch(
            `${API_BASE}${endpoint}`,
            {
                ...options,

                headers: {
                    "Content-Type":
                        "application/json",

                    ...(options.headers || {})
                }
            }
        );


        if (!response.ok) {

            throw new Error(
                `API error: ${response.status}`
            );

        }


        return await response.json();

    } catch (error) {

        console.warn(
            "EdgePilot backend unavailable:",
            error.message
        );

        return null;
    }
}


const api = {

    getState() {
        return apiRequest("/state");
    },


    getNodes() {
        return apiRequest("/nodes");
    },


    getWorkloads() {
        return apiRequest("/workloads");
    },


    getMetrics() {
        return apiRequest("/metrics");
    },


    getDecisions() {
        return apiRequest("/decisions");
    },


    getEvents() {
        return apiRequest("/events");
    },


    startSimulation(
        scenario,
        targetNode,
        intensity
    ) {

        return apiRequest(
            "/simulation/start",
            {
                method: "POST",

                body: JSON.stringify({
                    scenario,
                    target_node: targetNode,
                    intensity
                })
            }
        );
    },


    stopSimulation() {

        return apiRequest(
            "/simulation/stop",
            {
                method: "POST"
            }
        );
    },


    resetSimulation() {

        return apiRequest(
            "/simulation/reset",
            {
                method: "POST"
            }
        );
    },


    injectFault(
        scenario,
        targetNode,
        intensity
    ) {

        return apiRequest(
            "/simulation/fault",
            {
                method: "POST",

                body: JSON.stringify({
                    scenario,
                    target_node: targetNode,
                    intensity
                })
            }
        );
    }

};