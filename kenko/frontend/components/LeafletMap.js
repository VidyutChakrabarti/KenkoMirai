import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polygon,
  CircleMarker,
} from "react-leaflet";
import L from "leaflet";
import { useState, useEffect } from "react";
import "leaflet/dist/leaflet.css";
import {
  Box,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  Button,
  Flex,
} from "@chakra-ui/react";

// Fix default marker icon paths for Leaflet.
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png",
});

const LeafletMap = ({ simState, multipliers }) => {
  const { infectionMultiplier = 1, economicMultiplier = 1 } = multipliers || {};

  const [isClient, setIsClient] = useState(false);
  const [selectedHospital, setSelectedHospital] = useState(null);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient || !simState) {
    return <Box>Loading map...</Box>;
  }

  const center = [34.05, -118.25];

  // --------------------------------------------------------------------------------
  // computeTileColor
  // This function uses a local oscillatory value (localVal) between 0 (red) and 1 (green)
  // then pulls that value toward red based on severity.
  // Severity = (infection×infectionMultiplier + economicLoss×economicMultiplier) / 10
  // (Using 10 as divisor means even infection rate = 1 gives moderate severity.)
  // Finally, after timeStep ≥ 110, the tile gradually converges to green.
  // --------------------------------------------------------------------------------
  const computeTileColor = (neighborhoodId, timeStep) => {
    const period = 20;
    const idNum = parseInt(neighborhoodId.split("_")[1]);
    const offset = idNum * 3;
    const localVal =
      (Math.sin(((timeStep + offset) * 2 * Math.PI) / period) + 1) / 2;
    const infection = simState.infectionRates[neighborhoodId] || 0;
    const economicLoss = simState.economicLoss[neighborhoodId] || 0;
    const effInfection = infection * infectionMultiplier;
    const effEconomic = economicLoss * economicMultiplier;
    let severity = (effInfection + effEconomic) / 10;
    if (severity > 1) severity = 1;
    const effectiveVal = localVal * (1 - severity);
    const R = Math.round(255 * (1 - effectiveVal));
    const G = Math.round(255 * effectiveVal);
    const finalThreshold = 110;
    const finalTransitionPeriod = 10;
    let progress = 0;
    if (timeStep >= finalThreshold) {
      progress = Math.min((timeStep - finalThreshold) / finalTransitionPeriod, 1);
    }
    const redFinal = Math.round((1 - progress) * R);
    const greenFinal = Math.round((1 - progress) * G + progress * 255);
    return `rgb(${redFinal},${greenFinal},0)`;
  };
  // --------------------------------------------------------------------------------

  // For final-transition adjustments.
  const finalThreshold = 110;
  const finalTransitionPeriod = 10;
  let progress = 0;
  if (simState.timeStep >= finalThreshold) {
    progress = Math.min((simState.timeStep - finalThreshold) / finalTransitionPeriod, 1);
  }

  // Compute neighborhood polygons.
  const neighborhoodPolygons = Object.entries(simState.neighborhoods).map(
    ([n_id, bounds]) => {
      const { lat_min, lat_max, lon_min, lon_max } = bounds;
      return {
        id: n_id,
        positions: [
          [lat_min, lon_min],
          [lat_min, lon_max],
          [lat_max, lon_max],
          [lat_max, lon_min],
        ],
      };
    }
  );

  // Predetermined offsets for hospital markers.
  const hospitalOffsets = {
    "Neighborhood_1": { lat: 0.3, lon: 0.4 },
    "Neighborhood_2": { lat: 0.6, lon: 0.3 },
    "Neighborhood_3": { lat: 0.2, lon: 0.8 },
    "Neighborhood_4": { lat: 0.75, lon: 0.5 },
    "Neighborhood_5": { lat: 0.5, lon: 0.25 },
    "Neighborhood_6": { lat: 0.8, lon: 0.7 },
    "Neighborhood_7": { lat: 0.4, lon: 0.6 },
    "Neighborhood_8": { lat: 0.65, lon: 0.2 },
  };

  // Predefined hospital names.
  const hospitalNames = {
    "Neighborhood_1": "Downtown Hospital",
    "Neighborhood_2": "Hollywood Hospital",
    "Neighborhood_3": "Beverly Hills Hospital",
    "Neighborhood_4": "Santa Monica Hospital",
    "Neighborhood_5": "Westwood Hospital",
    "Neighborhood_6": "Pasadena Hospital",
    "Neighborhood_7": "Venice Hospital",
    "Neighborhood_8": "Echo Park Hospital",
  };

  // Compute hospital markers.
  const hospitalMarkers = Object.entries(simState.hospitalStats).map(
    ([n_id, stats]) => {
      const bounds = simState.neighborhoods[n_id];
      const { lat_min, lat_max, lon_min, lon_max } = bounds;
      const offset = hospitalOffsets[n_id] || { lat: 0.5, lon: 0.5 };
      const lat = lat_min + offset.lat * (lat_max - lat_min);
      const lon = lon_min + offset.lon * (lon_max - lon_min);
      return {
        id: n_id,
        position: [lat, lon],
        stats,
        name: hospitalNames[n_id] || `${n_id} Hospital`,
      };
    }
  );

  const handleHospitalClick = (hospital) => {
    setSelectedHospital(hospital);
  };

  const handleModalClose = () => {
    setSelectedHospital(null);
  };

  return (
    <>
      <MapContainer center={center} zoom={13} style={{ height: "100%", width: "100%" }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {/* Render neighborhood polygons with up-to-date infection rates in their Popup */}
        {neighborhoodPolygons.map((neighborhood) => {
          const tileColor = computeTileColor(neighborhood.id, simState.timeStep);
          // Compute displayed infection rate
          const rawInfection = simState.infectionRates[neighborhood.id] || 0;
          const minInfection = 0.2; // minimum value to display
          let displayedInfection = rawInfection;
          if (simState.timeStep >= finalThreshold && rawInfection > minInfection) {
            displayedInfection = rawInfection - (rawInfection - minInfection) * progress;
          }
          return (
            <Polygon
              key={neighborhood.id}
              positions={neighborhood.positions}
              pathOptions={{
                color: tileColor,
                fillColor: tileColor,
                fillOpacity: 0.2,
              }}
            >
              <Popup>
                <Box>
                  <strong>{neighborhood.id}</strong>
                  <p>
                    Infection Rate: {(displayedInfection * 100).toFixed(1)}%
                  </p>
                  <p>(Color: {tileColor})</p>
                </Box>
              </Popup>
            </Polygon>
          );
        })}

        {/* Render people markers as blue CircleMarkers (radius 4) */}
        {simState.people.map((person) => (
          <CircleMarker
            key={person.id}
            center={[person.position[0], person.position[1]]}
            radius={4}
            color="blue"
            fillColor="blue"
            fillOpacity={0.6}
            stroke={false}
          >
            <Popup>
              <Box>
                <p>Person ID: {person.id}</p>
                <p>Neighborhood: {person.neighborhood}</p>
              </Box>
            </Popup>
          </CircleMarker>
        ))}

        {/* Render hospital markers */}
        {hospitalMarkers.map((hospital) => (
          <Marker
            key={hospital.id}
            position={hospital.position}
            eventHandlers={{
              click: () => handleHospitalClick(hospital),
            }}
            icon={new L.Icon({
              iconUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon.png",
              iconSize: [25, 41],
              iconAnchor: [12, 41],
              popupAnchor: [1, -34],
              shadowUrl:
                "https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png",
              shadowSize: [41, 41],
            })}
          >
            <Popup>
              <Box>
                <strong>{hospital.name}</strong>
                <p>Click for details</p>
              </Box>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {selectedHospital && (
        <Modal isOpen={true} onClose={handleModalClose} isCentered>
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Hospital Details - {selectedHospital.name}</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <Box>
                {(() => {
                  const rawShortage = selectedHospital.stats.forecastShortage;
                  const MIN_SHORTAGE_FACTOR = 0.2;
                  // Adjust shortage only partially so that a minimal shortage remains.
                  const adjustedShortage =
                    rawShortage *
                    (MIN_SHORTAGE_FACTOR + (1 - progress) * (1 - MIN_SHORTAGE_FACTOR));
                  return (
                    <p>
                      <strong>Forecast Shortage:</strong> {adjustedShortage.toFixed(2)}
                    </p>
                  );
                })()}
                <p>
                  <strong>Surplus:</strong> {selectedHospital.stats.surplus.toFixed(2)}
                </p>
                <Box mt={4}>
                  <p>Forecast Shortage Chart:</p>
                  <Flex align="center">
                    {(() => {
                      const rawShortage = selectedHospital.stats.forecastShortage;
                      const MIN_SHORTAGE_FACTOR = 0.2;
                      const adjustedShortage =
                        rawShortage *
                        (MIN_SHORTAGE_FACTOR + (1 - progress) * (1 - MIN_SHORTAGE_FACTOR));
                      return (
                        <Box bg="red.500" height="20px" width={`${adjustedShortage * 100}%`} />
                      );
                    })()}
                    <Box ml={2}>
                      {(() => {
                        const rawShortage = selectedHospital.stats.forecastShortage;
                        const MIN_SHORTAGE_FACTOR = 0.2;
                        const adjustedShortage =
                          rawShortage *
                          (MIN_SHORTAGE_FACTOR + (1 - progress) * (1 - MIN_SHORTAGE_FACTOR));
                        return (adjustedShortage * 100).toFixed(0);
                      })()}
                      %
                    </Box>
                  </Flex>
                </Box>
                <Box mt={4}>
                  <p>Surplus Chart:</p>
                  <Flex align="center">
                    <Box bg="green.500" height="20px" width={`${selectedHospital.stats.surplus * 100}%`} />
                    <Box ml={2}>
                      {(selectedHospital.stats.surplus * 100).toFixed(0)}%
                    </Box>
                  </Flex>
                </Box>
              </Box>
            </ModalBody>
            <ModalFooter>
              <Button colorScheme="blue" onClick={handleModalClose}>
                Close
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      )}

      {/* Global CSS for smooth transitions on Leaflet elements */}
      <style jsx global>{`
        .leaflet-interactive {
          transition: stroke 1s ease, fill 1s ease;
        }
      `}</style>
    </>
  );
};

export default LeafletMap;
