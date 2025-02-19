import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Header from '../components/Header';
import MapVisualization from '../components/MapVisualization';
import SimulationChart from '../components/SimulationChart';
import axios from 'axios';

export default function SimulationPage() {
    const [simulationResult, setSimulationResult] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get('http://localhost:8000/simulation?steps=50')
            .then(res => {
                setSimulationResult(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    if (loading) return <div>Loading simulation...</div>;
    if (!simulationResult) return <div>Error loading simulation data.</div>;

    const finalState = simulationResult.final;

    return (
        <div>
            <Head>
                <title>Simulation Details</title>
            </Head>
            <Header />
            <main>
                <h1>Simulation Results at Time {finalState.time}</h1>
                <p>Lockdown Status: {finalState.lockdown ? "Active" : "Not Active"}</p>
                <section>
                    <h2>Map Visualization</h2>
                    <MapVisualization agents={finalState.agents} />
                </section>
                <section>
                    <h2>Simulation Chart</h2>
                    <SimulationChart history={simulationResult.history} />
                </section>
            </main>
        </div>
    );
}
