import { useEffect, useState } from "react";
import {
  Box,
  Flex,
  Heading,
  Text,
  VStack,
  Divider,
  useToast,
} from "@chakra-ui/react";
import MapComponent from "../components/MapComponent";
import Controls from "../components/Controls";
import NavBar from "../components/NavBar";

export default function Home() {
  const [simState, setSimState] = useState(null);
  const [geminiSuggestions, setGeminiSuggestions] = useState({});
  const [orchestrateMessage, setOrchestrateMessage] = useState("");
  const [isOrchestrating, setIsOrchestrating] = useState(false);
  const [multipliers, setMultipliers] = useState({
    infectionMultiplier: 1,
    economicMultiplier: 1,
  });

  const toast = useToast();

  const fetchSimState = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/simulate");
      const data = await res.json();
      setSimState(data);
    } catch (error) {
      console.error("Error fetching simulation state:", error);
    }
  };

  const fetchGemini = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/gemini-suggestions");
      const data = await res.json();
      setGeminiSuggestions(data);
    } catch (error) {
      console.error("Error fetching gemini suggestions:", error);
    }
  };

  useEffect(() => {
    fetchSimState();
    fetchGemini();
    const intervalId = setInterval(() => {
      fetchSimState();
      fetchGemini();
    }, 1000);
    return () => clearInterval(intervalId);
  }, []);

  const handleReset = async () => {
    try {
      await fetch("http://localhost:5000/api/reset", { method: "POST" });
    } catch (error) {
      console.error("Error resetting simulation:", error);
    }
  };

  const handleStep = async () => {
    try {
      await fetch("http://localhost:5000/api/step", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
    } catch (error) {
      console.error("Error advancing simulation:", error);
    }
  };

  const handleOrchestrate = async () => {
    if (isOrchestrating) return;
    setIsOrchestrating(true);
    setOrchestrateMessage("");
    let iterations = 120; // simulation advances every 1 second for 2 minutes.
    const intervalId = setInterval(async () => {
      await handleStep();
      iterations--;
      if (iterations <= 0) {
        clearInterval(intervalId);
        setIsOrchestrating(false);
        setOrchestrateMessage(
          "Containment policy was finalised for simulation run"
        );
        toast({
          title: "Simulation Finished",
          description: "Containment policy was finalised for simulation run",
          status: "success",
          duration: 5000,
          isClosable: true,
        });
      }
    }, 1000);
  };

  // Update multipliers based on sidebar controls.
  const handleSetParameters = (params) => {
    setMultipliers({
      infectionMultiplier: parseFloat(params.infectionMultiplier),
      economicMultiplier: parseFloat(params.economicMultiplier),
    });
    alert(
      `Parameters set: Infection Multiplier = ${params.infectionMultiplier}, Economic Multiplier = ${params.economicMultiplier}`
    );
  };

  // Simulate Travel Restricted fluctuations every ~15 steps.
  const travelRestrictedDisplay =
    simState && simState.timeStep
      ? Math.floor(simState.timeStep / 15) % 2 === 0
        ? "Yes"
        : "No"
      : "No";

  return (
    <>
      <NavBar />
      <Flex height="calc(100vh - 64px)">
        <Box flex="3">
          {simState ? (
            <MapComponent simState={simState} multipliers={multipliers} />
          ) : (
            <Text color="white">Loading simulation...</Text>
          )}
        </Box>
        <Box flex="1" p={4} bg="gray.700" color="white" overflowY="auto">
          <Heading size="md" mb={4}>
            Simulation Controls
          </Heading>
          <Controls
            onReset={handleReset}
            onStep={handleStep}
            onSetParameters={handleSetParameters}
            onOrchestrate={handleOrchestrate}
            isOrchestrating={isOrchestrating}
          />
          <Divider my={4} />
          <VStack align="start">
            <Text>Time Step: {simState ? simState.timeStep : "--"}</Text>
            <Text>Travel Restricted: {travelRestrictedDisplay}</Text>
          </VStack>
          <Divider my={4} />
          {orchestrateMessage && (
            <Box p={2} bg="blue.500" borderRadius="md" my={1}>
              <Text fontSize="sm">{orchestrateMessage}</Text>
            </Box>
          )}
          <Heading size="sm" mt={4}>
            Gemini Suggestions:
          </Heading>
          {Object.entries(geminiSuggestions).map(([nb, suggestion]) => (
            <Box key={nb} p={2} bg="gray.600" borderRadius="md" my={1}>
              <Text fontSize="sm">{suggestion}</Text>
            </Box>
          ))}
        </Box>
      </Flex>
    </>
  );
}
