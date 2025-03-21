import { useState, useEffect } from "react";
import {
  Box,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Heading,
  VStack,
  Text,
  Divider,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
} from "@chakra-ui/react";
import NavBar from "../components/NavBar";

export default function ShareInfo() {
  // Form field states
  const [patientName, setPatientName] = useState("");
  const [patientId, setPatientId] = useState("");
  const [documentContent, setDocumentContent] = useState("");

  // State for shared patient records
  const [records, setRecords] = useState([]);

  // State used to store a record for which full info will be shown
  const [selectedRecord, setSelectedRecord] = useState(null);

  // Fetch records from the backend API
  const fetchRecords = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/patient_info");
      const data = await res.json();
      setRecords(data);
    } catch (error) {
      console.error("Error fetching patient records:", error);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  // Handle form submission – send POST request and refresh record list
  const handleSubmit = async (e) => {
    e.preventDefault();
    const info = {
      patientName,
      patientId,
      documentContent,
      timestamp: new Date().toISOString(),
    };

    try {
      const res = await fetch("http://localhost:5000/api/share_info", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(info),
      });
      const data = await res.json();
      alert("Information shared successfully!");
      // Clear the form fields
      setPatientName("");
      setPatientId("");
      setDocumentContent("");
      // Refresh records list so the new record is visible
      fetchRecords();
    } catch (error) {
      console.error("Error sharing info:", error);
    }
  };

  // Define a maximum length for the truncated document content
  const truncLength = 100; // characters

  return (
    <>
      <NavBar />
      <Flex direction="column" p={6} bg="gray.800" minH="100vh" color="white">
        <Heading mb={4}>Share Patient &amp; Critical Information</Heading>
        <Box
          as="form"
          onSubmit={handleSubmit}
          maxW="600px"
          mb={8}
          p={4}
          bg="gray.700"
          borderRadius="md"
        >
          <FormControl mb={4}>
            <FormLabel>Patient Name</FormLabel>
            <Input
              value={patientName}
              onChange={(e) => setPatientName(e.target.value)}
              placeholder="Enter patient name"
            />
          </FormControl>
          <FormControl mb={4}>
            <FormLabel>Patient ID</FormLabel>
            <Input
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              placeholder="Enter patient ID"
            />
          </FormControl>
          <FormControl mb={4}>
            <FormLabel>Document / Critical Information</FormLabel>
            <Textarea
              value={documentContent}
              onChange={(e) => setDocumentContent(e.target.value)}
              placeholder="Enter details here"
            />
          </FormControl>
          <Button type="submit" colorScheme="teal">
            Share Information
          </Button>
        </Box>

        <Heading mb={4}>Shared Patient Records</Heading>
        <VStack spacing={4} align="stretch">
          {records.length > 0 ? (
            records.map((record, idx) => (
              <Box
                key={record.patientId + idx}
                p={4}
                bg="gray.700"
                borderRadius="md"
              >
                <Text fontWeight="bold">
                  Patient Name: {record.patientName}
                </Text>
                <Text>Patient ID: {record.patientId}</Text>
                <Text>
                  Details:{" "}
                  {record.documentContent.length > truncLength
                    ? record.documentContent.substring(0, truncLength) + "..."
                    : record.documentContent}
                </Text>
                {record.documentContent.length > truncLength && (
                  <Button
                    mt={2}
                    size="sm"
                    colorScheme="teal"
                    onClick={() => setSelectedRecord(record)}
                  >
                    Show Full Info
                  </Button>
                )}
                <Text fontSize="sm" color="gray.300" mt={2}>
                  Timestamp: {record.timestamp}
                </Text>
              </Box>
            ))
          ) : (
            <Text>No patient records available.</Text>
          )}
        </VStack>
        <Divider my={4} />
      </Flex>

      {/* Modal to display full information */}
      <Modal
        isOpen={selectedRecord !== null}
        onClose={() => setSelectedRecord(null)}
        isCentered
      >
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Patient Full Information</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {selectedRecord && (
              <Box>
                <Text fontWeight="bold">
                  Patient Name: {selectedRecord.patientName}
                </Text>
                <Text>Patient ID: {selectedRecord.patientId}</Text>
                <Text mt={2}>Details: {selectedRecord.documentContent}</Text>
                <Text mt={2} fontSize="sm" color="gray.500">
                  Timestamp: {selectedRecord.timestamp}
                </Text>
              </Box>
            )}
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" onClick={() => setSelectedRecord(null)}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
}
