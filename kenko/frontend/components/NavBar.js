import NextLink from "next/link";
import { Flex, Link, Spacer, Button } from "@chakra-ui/react";

const NavBar = () => {
  return (
    <Flex bg="gray.800" p={4} align="center">
      <NextLink href="/" passHref legacyBehavior>
        <Link color="white" fontWeight="bold" mr={4}>
          Dashboard
        </Link>
      </NextLink>
      <NextLink href="/timeline" passHref legacyBehavior>
        <Link color="white" mr={4}>
          Containment Timeline
        </Link>
      </NextLink>
      <NextLink href="/hospital_stats" passHref legacyBehavior>
        <Link color="white" mr={4}>
          Hospital Stats
        </Link>
      </NextLink>
      <NextLink href="/share_info" passHref legacyBehavior>
        <Link color="white" mr={4}>
          Share Info
        </Link>
      </NextLink>
      <Spacer />
      <Button colorScheme="teal" variant="outline">
        LA COVID Sim
      </Button>
    </Flex>
  );
};

export default NavBar;
