let simulationRunning = false;


function setupSimulation() {

    const intensity =
        document.getElementById(
            "intensity"
        );


    const intensityValue =
        document.getElementById(
            "intensityValue"
        );


    if (intensity && intensityValue) {

        intensity.addEventListener(
            "input",
            () => {

                intensityValue.textContent =
                    `${intensity.value}%`;

            }
        );

    }


    const start =
        document.getElementById(
            "startSimulation"
        );


    if (start) {

        start.addEventListener(
            "click",
            startSimulation
        );

    }


    const pause =
        document.getElementById(
            "pauseSimulation"
        );


    if (pause) {

        pause.addEventListener(
            "click",
            pauseSimulation
        );

    }


    const reset =
        document.getElementById(
            "resetSimulation"
        );


    if (reset) {

        reset.addEventListener(
            "click",
            resetSimulation
        );

    }

}


async function startSimulation() {

    const scenario =
        document.getElementById(
            "scenario"
        )?.value;


    const targetNode =
        document.getElementById(
            "targetNode"
        )?.value;


    const intensity =
        Number(
            document.getElementById(
                "intensity"
            )?.value || 50
        );


    simulationRunning = true;


    setSimulationStatus(
        "Starting simulation..."
    );


    const response =
        await api.startSimulation(
            scenario,
            targetNode,
            intensity
        );


    setSimulationStatus(
        response?.message ||
        `Simulation started: ${scenario}`
    );


    loadSimulationData();

}


async function pauseSimulation() {

    simulationRunning = false;


    const response =
        await api.stopSimulation();


    setSimulationStatus(
        response?.message ||
        "Simulation paused."
    );

}


async function resetSimulation() {

    simulationRunning = false;


    const response =
        await api.resetSimulation();


    setSimulationStatus(
        response?.message ||
        "Simulation reset."
    );


    loadSimulationData();

}


function setSimulationStatus(
    message
) {

    const element =
        document.getElementById(
            "simulationStatus"
        );


    if (element) {

        element.textContent =
            message;

    }

}


async function loadSimulationData() {

    const events =
        await api.getEvents();


    const container =
        document.getElementById(
            "simulationEvents"
        );


    if (
        !container ||
        !events
    ) {
        return;
    }


    container.innerHTML =
        events.map(
            event => `

                <div class="event-row">

                    <span class="event-time">
                        ${
                            event.time ||
                            "--"
                        }
                    </span>

                    <div class="event-icon ${
                        event.level === "warning"
                            ? "warning"
                            : "success"
                    }">
                        ${
                            event.level === "warning"
                                ? "!"
                                : "✓"
                        }
                    </div>

                    <div class="event-content">

                        <strong>
                            ${
                                event.message ||
                                event.event ||
                                "System event"
                            }
                        </strong>

                    </div>

                </div>

            `
        ).join("");

}


function renderEvents(
    events = []
) {

    const container =
        document.getElementById(
            "events"
        );


    if (!container) {
        return;
    }


    container.innerHTML =
        events.slice(0, 8)
            .map(
                event => `

                    <div class="event-row">

                        <span class="event-time">
                            ${
                                event.time ||
                                "--"
                            }
                        </span>

                        <div class="event-icon ${
                            event.level === "warning"
                                ? "warning"
                                : "success"
                        }">
                            ${
                                event.level === "warning"
                                    ? "!"
                                    : "✓"
                            }
                        </div>

                        <div class="event-content">

                            <strong>
                                ${
                                    event.message ||
                                    event.event ||
                                    "System event"
                                }
                            </strong>

                            <span>
                                ${
                                    event.description ||
                                    ""
                                }
                            </span>

                        </div>

                    </div>

                `
            ).join("");

}


window.setupSimulation =
    setupSimulation;


window.renderEvents =
    renderEvents;