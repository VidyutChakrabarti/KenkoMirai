import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix default icon paths for Leaflet in Next.js
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: '/marker-icon-2x.png',
    iconUrl: '/marker-icon.png',
    shadowUrl: '/marker-shadow.png',
});

export default function MapVisualization({ agents }) {
    // Centered roughly on Los Angeles
    const center = [34.05, -118.25];

    return (
        <MapContainer center={center} zoom={12} style={{ height: "400px", width: "100%" }}>
            <TileLayer
                attribution='&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {agents.map(agent => (
                <Marker key={agent.id} position={[agent.lat, agent.lng]}>
                    <Popup>
                        <strong>ID:</strong> {agent.id}<br />
                        <strong>State:</strong> {agent.state}<br />
                        <strong>Age:</strong> {agent.age}<br />
                        <strong>Occupation:</strong> {agent.occupation}
                    </Popup>
                </Marker>
            ))}
        </MapContainer>
    );
}
