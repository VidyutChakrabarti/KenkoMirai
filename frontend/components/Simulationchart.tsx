import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

export default function SimulationChart({ history }) {
    const chartRef = useRef(null);

    useEffect(() => {
        if (!chartRef.current || history.length === 0) return;

        const ctx = chartRef.current.getContext('2d');
        const labels = history.map(step => `T${step.time}`);
        const susceptible = history.map(step => step.aggregate.S);
        const infected = history.map(step => step.aggregate.I);
        const recovered = history.map(step => step.aggregate.R);
        const deceased = history.map(step => step.aggregate.D);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    { label: 'Susceptible', data: susceptible, borderColor: 'blue', fill: false },
                    { label: 'Infected', data: infected, borderColor: 'red', fill: false },
                    { label: 'Recovered', data: recovered, borderColor: 'green', fill: false },
                    { label: 'Deceased', data: deceased, borderColor: 'black', fill: false }
                ]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true } }
            }
        });
    }, [history]);

    return <canvas ref={chartRef} />;
}
