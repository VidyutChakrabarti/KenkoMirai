import { useState } from "react";
import { Box, Button, FormControl, FormLabel, Input, VStack, HStack } from "@chakra-ui/react";

const Controls = ({ onReset, onStep, onSetParameters, onOrchestrate, isOrchestrating }) => {
  const [infectionMultiplier, setInfectionMultiplier] = useState(1);
  const [economicMultiplier, setEconomicMultiplier] = useState(1);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSetParameters({ infectionMultiplier, economicMultiplier });
  };

  return (
    <VStack spacing={4} align="stretch">
      <HStack spacing={4}>
        <Button colorScheme="red" onClick={onReset}>
          Reset Simulation
        </Button>
        <Button
          colorScheme="blue"
          onClick={onStep}
          isDisabled={isOrchestrating}
        >
          Advance Simulation Step
        </Button>
      </HStack>
      <Button
        colorScheme="purple"
        onClick={onOrchestrate}
        isDisabled={isOrchestrating}
      >
        {isOrchestrating ? "Simulation Running..." : "Orchestrate Simulation"}
      </Button>
      <Box as="form" onSubmit={handleSubmit}>
        <FormControl mb={3}>
          <FormLabel color="white">Infection Rate Multiplier</FormLabel>
          <Input
            type="number"
            step="0.1"
            value={infectionMultiplier}
            onChange={(e) => setInfectionMultiplier(e.target.value)}
          />
        </FormControl>
        <FormControl mb={3}>
          <FormLabel color="white">Economic Loss Multiplier</FormLabel>
          <Input
            type="number"
            step="0.1"
            value={economicMultiplier}
            onChange={(e) => setEconomicMultiplier(e.target.value)}
          />
        </FormControl>
        <Button type="submit" colorScheme="green">
          Set Parameters
        </Button>
      </Box>
    </VStack>
  );
};

export default Controls;
