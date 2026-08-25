import fs from "node:fs";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "../..");
const errors = [];

function read(relativePath) {
  const absolutePath = path.join(root, relativePath);
  if (!fs.existsSync(absolutePath)) {
    errors.push(`missing deployment file: ${relativePath}`);
    return "";
  }
  return fs.readFileSync(absolutePath, "utf8");
}

const compose = read("infrastructure/docker-compose.yml");
for (const service of ["backend:", "frontend:", "trainer:"]) {
  if (!new RegExp(`^  ${service}`, "m").test(compose)) {
    errors.push(`docker compose is missing service ${service.slice(0, -1)}`);
  }
}
if (!compose.includes("profiles: [\"training\"]")) {
  errors.push("trainer must remain opt-in through the training profile");
}
if (!compose.includes("condition: service_healthy")) {
  errors.push("frontend must wait for the healthy backend service");
}

const backendDockerfile = read("backend/Dockerfile");
const frontendDockerfile = read("frontend/Dockerfile");
const mlDockerfile = read("ml/Dockerfile");
for (const [name, contents, required] of [
  ["backend", backendDockerfile, ["COPY backend/app ./app", "EXPOSE 8000"]],
  ["frontend", frontendDockerfile, ["npm run build --workspace @kenkomirai/frontend", "EXPOSE 3000"]],
  ["ml", mlDockerfile, ["COPY ml ./ml", "ENTRYPOINT"]],
]) {
  for (const fragment of required) {
    const normalized = contents.replace(/COPY --[^\n]+?\s+/g, "COPY ");
    if (!normalized.includes(fragment)) errors.push(`${name}/Dockerfile is missing ${fragment}`);
  }
}

if (errors.length > 0) {
  console.error("Deployment contract validation failed:");
  for (const error of errors) console.error(`- ${error}`);
  process.exitCode = 1;
} else {
  console.log("Validated Compose services and Dockerfile contracts without building images.");
}