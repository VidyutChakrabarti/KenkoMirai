import fs from "node:fs";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "../..");
const frontend = path.join(root, "frontend");

function readJson(relativePath) {
  const absolutePath = path.join(root, relativePath);
  return JSON.parse(fs.readFileSync(absolutePath, "utf8"));
}

const packageJson = readJson("frontend/package.json");
const lockJson = readJson("package-lock.json");
const rootPackageJson = readJson("package.json");
const errors = [];

if (packageJson.name !== "@kenkomirai/frontend") {
  errors.push("frontend/package.json must use the workspace package name");
}
if (lockJson.packages?.["frontend"]?.name !== packageJson.name) {
  errors.push("package-lock.json does not match the frontend package name");
}
if (lockJson.packages?.["frontend"]?.version !== packageJson.version) {
  errors.push("package-lock.json does not match the frontend package version");
}
if (!rootPackageJson.workspaces?.includes("frontend")) {
  errors.push("root package.json must declare the frontend workspace");
}

const requiredFiles = [
  "src/pages/api/backend/[...path].ts",
  "src/pages/simulation.tsx",
  "src/types/simulation.ts",
  "next.config.ts",
];
for (const relativePath of requiredFiles) {
  if (!fs.existsSync(path.join(frontend, relativePath))) {
    errors.push(`missing required frontend file: frontend/${relativePath}`);
  }
}

if (errors.length > 0) {
  console.error("Frontend contract validation failed:");
  for (const error of errors) console.error(`- ${error}`);
  process.exitCode = 1;
} else {
  console.log("Validated frontend package, lockfile, workspace, and required files.");
}