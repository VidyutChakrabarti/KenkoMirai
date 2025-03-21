import dynamic from "next/dynamic";
import { Box } from "@chakra-ui/react";

const LeafletMap = dynamic(() => import("./LeafletMap"), { ssr: false });

const MapComponent = ({ simState }) => {
  return (
    <Box w="100%" h="100%">
      <LeafletMap simState={simState} />
    </Box>
  );
};

export default MapComponent;
