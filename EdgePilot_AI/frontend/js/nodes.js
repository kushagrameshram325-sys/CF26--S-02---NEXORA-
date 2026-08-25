function renderTopology(nodes = []) {

    const container =
        document.getElementById(
            "topologyContainer"
        );


    if (!container) {
        return;
    }


    const defaultNodes = [

        {
            id: "N-01",
            cpu: 42,
            status: "healthy"
        },

        {
            id: "N-02",
            cpu: 57,
            status: "healthy"
        },

        {
            id: "N-03",
            cpu: 82,
            status: "warning"
        },

        {
            id: "N-04",
            cpu: 37,
            status: "healthy"
        },

        {
            id: "N-05",
            cpu: 51,
            status: "healthy"
        }

    ];


    const data =
        nodes.length
            ? nodes
            : defaultNodes;


    const positions = [

        ["10%", "14%"],
        ["calc(50% - 40px)", "37%"],
        ["82%", "14%"],
        ["10%", "78%"],
        ["82%", "78%"]

    ];


    let html = `

        <div class="topology-wrapper">

            <div class="topology-grid">

                <div class="topology-lines">

                    <svg
                        viewBox="0 0 800 400"
                        preserveAspectRatio="none">

                        <line
                            x1="130"
                            y1="100"
                            x2="400"
                            y2="200">
                        </line>

                        <line
                            x1="400"
                            y1="200"
                            x2="670"
                            y2="100">
                        </line>

                        <line
                            x1="130"
                            y1="100"
                            x2="400"
                            y2="330">
                        </line>

                        <line
                            x1="400"
                            y1="200"
                            x2="670"
                            y2="330">
                        </line>

                    </svg>

                </div>

    `;


    data.slice(0, 5).forEach(
        (node, index) => {

            const position =
                positions[index];


            const warning =
                node.status === "warning" ||
                Number(node.cpu) >= 80;


            html += `

                <div
                    class="
                        topology-node
                        ${warning ? "warning-node" : ""}
                    "
                    style="
                        left:${position[0]};
                        top:${position[1]};
                    "
                >

                    <div class="node-icon">
                        ${node.id || `N-0${index + 1}`}
                    </div>

                    <strong>
                        ${node.id || `N-0${index + 1}`}
                    </strong>

                    <span>
                        ${node.cpu ?? 0}% CPU
                    </span>

                </div>

            `;

        }
    );


    html += `

            </div>

        </div>

    `;


    container.innerHTML = html;
}


window.renderTopology =
    renderTopology;