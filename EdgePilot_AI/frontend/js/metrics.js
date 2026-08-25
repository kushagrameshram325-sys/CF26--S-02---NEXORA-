let metricsChart = null;


function drawMetricsChart(
    metrics = {}
) {

    const canvas =
        document.getElementById(
            "metricsChart"
        );


    if (!canvas) {
        return;
    }


    const rect =
        canvas.getBoundingClientRect();


    const ratio =
        window.devicePixelRatio || 1;


    canvas.width =
        rect.width * ratio;


    canvas.height =
        rect.height * ratio;


    const ctx =
        canvas.getContext("2d");


    ctx.scale(ratio, ratio);


    const width = rect.width;
    const height = rect.height;


    ctx.clearRect(
        0,
        0,
        width,
        height
    );


    const latency =
        metrics.latency_series ||
        [38, 34, 31, 29, 25, 27, 22, 24, 19, 21];


    const utilization =
        metrics.cpu_series ||
        [51, 56, 58, 62, 59, 64, 61, 66, 63, 64];


    const maxLatency =
        Math.max(...latency) * 1.2;


    const maxCPU = 100;


    function drawGrid() {

        ctx.strokeStyle =
            "#182b3f";

        ctx.lineWidth = 1;


        for (
            let i = 0;
            i < 5;
            i++
        ) {

            const y =
                20 +
                i *
                ((height - 40) / 4);


            ctx.beginPath();

            ctx.moveTo(
                0,
                y
            );

            ctx.lineTo(
                width,
                y
            );

            ctx.stroke();

        }

    }


    function drawLine(
        data,
        max,
        stroke
    ) {

        ctx.strokeStyle =
            stroke;

        ctx.lineWidth = 2.5;

        ctx.beginPath();


        data.forEach(
            (value, index) => {

                const x =
                    index *
                    (width /
                    (data.length - 1));


                const y =
                    height -
                    20 -
                    (
                        value / max
                    ) *
                    (
                        height - 40
                    );


                if (index === 0) {

                    ctx.moveTo(
                        x,
                        y
                    );

                } else {

                    ctx.lineTo(
                        x,
                        y
                    );

                }

            }
        );


        ctx.stroke();

    }


    drawGrid();


    drawLine(
        latency,
        maxLatency,
        "#55e0ba"
    );


    drawLine(
        utilization,
        maxCPU,
        "#6ca8ff"
    );

}


function renderMetrics(
    metrics = {}
) {

    drawMetricsChart(metrics);

}


window.renderMetrics =
    renderMetrics;


window.addEventListener(
    "resize",
    () => {

        drawMetricsChart();

    }
);