import fs from "node:fs";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "../..");
const workflowPath = path.join(root, ".github/workflows/ci.yml");
const workflow = fs.readFileSync(workflowPath, "utf8");
const errors = [];

for (const pattern of [/pip\s+install/i, /npm\s+(ci|install)/i, /docker\s+build/i]) {
  if (pattern.test(workflow)) errors.push(`forbidden dependency or image command: ${pattern}`);
}
for (const script of [
  "scripts/ci/validate_python.py",
  "scripts/ci/validate_frontend.mjs",
  "scripts/ci/validate_deployment.mjs",
]) {
  if (!fs.existsSync(path.join(root, script))) errors.push(`missing required CI check: ${script}`);
}

if (errors.length > 0) {
  console.error("CI policy validation failed:");
  for (const error of errors) console.error(`- ${error}`);
  process.exitCode = 1;
} else {
  console.log("CI policy forbids package installation and image builds as intended.");
}