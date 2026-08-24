import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const python = process.platform === "win32"
  ? path.join(root, "backend", "ai-service", ".venv", "Scripts", "python.exe")
  : path.join(root, "backend", "ai-service", ".venv", "bin", "python");

if (!existsSync(python)) {
  console.error(`[ClassBridge] Missing AI test interpreter: ${python}`);
  process.exit(1);
}

const result = spawnSync(
  python,
  ["-m", "unittest", "discover", "-s", "test/backend", "-p", "test_*.py"],
  { cwd: root, stdio: "inherit" },
);
process.exit(result.status ?? 1);
