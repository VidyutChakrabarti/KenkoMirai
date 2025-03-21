import { useEffect, useState } from "react";
import { Box, Heading, VStack, Text } from "@chakra-ui/react";
import NavBar from "../components/NavBar";

export default function Timeline() {
  const [plan, setPlan] = useState([]);

  const fetchPlan = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/plan");
      const data = await res.json();
      setPlan(data.plan);
    } catch (error) {
      console.error("Error fetching plan:", error);
    }
  };

  useEffect(() => {
    fetchPlan();
  }, []);

  return (
    <>
      <NavBar />
      <Box p={6} bg="gray.800" minH="100vh" color="white">
        <Heading mb={4}>Containment Policy Timeline</Heading>
        <VStack spacing={4} align="stretch">
          {plan.length > 0 ? (
            plan.map((entry, idx) => (
              <Box key={idx} p={4} bg="gray.700" borderRadius="md">
                <Text>{entry}</Text>
              </Box>
            ))
          ) : (
            <Text>No plan data available. Please run the RL agent training.</Text>
          )}
        </VStack>
      </Box>
    </>
  );
}
