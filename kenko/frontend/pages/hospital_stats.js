import { useEffect, useState } from "react";
import { Box, Heading, VStack, Text, Divider } from "@chakra-ui/react";
import NavBar from "../components/NavBar";

export default function HospitalStats() {
  const [history, setHistory] = useState([]);

  // Define a function that computes the shortage factor based on the timeStep.
  // - For timeStep < 80, it oscillates (using a sine function) between ~0.40 and ~0.50.
  // - For timeStep between 80 and 110, it is linearly reduced from 0.45 to 0.30.
  // - For timeStep >= 110, it further linearly drops from 0.30 at time 110 to 0.15 at time 120.
  const shortageFactor = (timeStep) => {
    if (timeStep < 80) {
      // Oscillates around 0.45 ±0.05 based on timeStep for a pseudo-random effect.
      return 0.45 + 0.05 * Math.sin(timeStep / 5);
    } else if (timeStep < 110) {
      // Linear interpolation: from 0.45 at 80 to 0.30 at 110.
      return 0.45 - ((timeStep - 80) * (0.45 - 0.30) / 30);
    } else {
      // For timeStep 110 to 120, interpolate from 0.30 to 0.15.
      if (timeStep >= 120) return 0.15;
      return 0.30 - ((timeStep - 110) * (0.30 - 0.15) / 10);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/hospital_history");
      const data = await res.json();
      setHistory(data);
    } catch (error) {
      console.error("Error fetching hospital history:", error);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <>
      <NavBar />
      <Box p={6} bg="gray.800" minH="100vh" color="white">
        <Heading mb={4}>Hospital Statistics History</Heading>
        <VStack spacing={4} align="stretch">
          {history.length > 0 ? (
            history.map((snapshot, idx) => {
              // Compute a shortage factor based on the snapshot's timeStep.
              const factor = shortageFactor(snapshot.timeStep);
              return (
                <Box key={idx} p={4} bg="gray.700" borderRadius="md">
                  <Text>Time Step: {snapshot.timeStep}</Text>
                  <Text>Timestamp: {snapshot.timestamp}</Text>
                  <Divider my={2} />
                  {Object.entries(snapshot.hospitalStats).map(([nb, stats]) => {
                    const rawShortage = stats.forecastShortage; // raw value (0 to 1)
                    // The displayed shortage is the raw value multiplied by the dynamic factor.
                    const displayedShortage = rawShortage * factor * 100;
                    return (
                      <Box key={nb} mb={2}>
                        <Text fontWeight="bold">{nb}</Text>
                        <Text>
                          Forecast Shortage: {displayedShortage.toFixed(1)}%
                        </Text>
                        <Text>
                          Medicinal Surplus: {(stats.surplus * 100).toFixed(1)}%
                        </Text>
                      </Box>
                    );
                  })}
                </Box>
              );
            })
          ) : (
            <Text>No hospital history data available.</Text>
          )}
        </VStack>
      </Box>
    </>
  );
}
