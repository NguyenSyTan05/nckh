import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const aiDirectory = path.join(root, "..", "backend", "ai-service");
const python = process.platform === "win32"
  ? path.join(aiDirectory, ".venv", "Scripts", "python.exe")
  : path.join(aiDirectory, ".venv", "bin", "python");
const mode = process.argv[2] ?? "dev";
const forwardedArguments = process.argv.slice(3);
const healthUrl = "http://127.0.0.1:8000/health";

if (!existsSync(python)) {
  console.error(`[ClassBridge] Không tìm thấy Python AI tại ${python}`);
  console.error("Hãy tạo ai-service/.venv và cài ai-service/requirements.txt trước.");
  process.exit(1);
}

if (mode === "--check") {
  console.log(JSON.stringify({ root, aiDirectory, python, healthUrl }));
  process.exit(0);
}

if (!new Set(["dev", "start"]).has(mode)) {
  console.error("Cách dùng: node scripts/run-local.mjs [dev|start|--check]");
  process.exit(1);
}

let stopping = false;
let aiProcess = null;
let restartTimer = null;

async function aiIsHealthy() {
  try {
    const response = await fetch(healthUrl, {
      signal: AbortSignal.timeout(2_000),
    });
    return response.ok;
  } catch {
    return false;
  }
}

function scheduleAiRestart() {
  if (stopping || restartTimer) return;
  restartTimer = setTimeout(() => {
    restartTimer = null;
    void ensureAi();
  }, 2_000);
}

function launchAi() {
  if (stopping || aiProcess) return;
  console.log("[ClassBridge] Đang nạp dịch vụ AI từ ổ D (cổng 8000)…");
  aiProcess = spawn(
    python,
    [
      "-m", "uvicorn", "main:app",
      "--app-dir", aiDirectory,
      "--host", process.env.AI_HOST || "0.0.0.0",
      "--port", "8000",
    ],
    {
      cwd: aiDirectory,
      stdio: "inherit",
      env: {
        ...process.env,
        PYTHONIOENCODING: process.env.PYTHONIOENCODING || "utf-8",
        PYTHONUTF8: process.env.PYTHONUTF8 || "1",
        WHISPER_CPU_THREADS:
          process.env.WHISPER_CPU_THREADS || "4",
        WHISPER_ACCURATE_WORKERS:
          process.env.WHISPER_ACCURATE_WORKERS || "1",
        TRANSLATION_CPU_THREADS:
          process.env.TRANSLATION_CPU_THREADS || "3",
        TRANSLATION_NUM_WORKERS:
          process.env.TRANSLATION_NUM_WORKERS || "3",
        TRANSLATION_MAX_NEW_TOKENS:
          process.env.TRANSLATION_MAX_NEW_TOKENS || "128",
        TRANSLATION_USE_ENSEMBLE:
          process.env.TRANSLATION_USE_ENSEMBLE || "true",
        CLASSBRIDGE_OPENBLAS_THREADS:
          process.env.CLASSBRIDGE_OPENBLAS_THREADS || "1",
        CLASSBRIDGE_OMP_THREADS:
          process.env.CLASSBRIDGE_OMP_THREADS || "2",
        CLASSBRIDGE_MKL_THREADS:
          process.env.CLASSBRIDGE_MKL_THREADS || "2",
      },
    },
  );
  aiProcess.on("error", (error) => {
    console.error(`[ClassBridge] Không thể khởi động AI: ${error.message}`);
  });
  aiProcess.on("exit", (code, signal) => {
    aiProcess = null;
    if (!stopping) {
      console.error(
        `[ClassBridge] AI đã dừng (${signal ?? code}); sẽ tự khởi động lại.`,
      );
      scheduleAiRestart();
    }
  });
}

async function ensureAi() {
  if (stopping || aiProcess) return;
  if (await aiIsHealthy()) return;
  launchAi();
}

const webScript = mode === "dev" ? "dev:web" : "start:web";
const webArguments = [
  "run",
  webScript,
  ...(forwardedArguments.length ? ["--", ...forwardedArguments] : []),
];
const windowsForwardedArguments = forwardedArguments
  .map((value) => `"${value.replaceAll('"', '""')}"`)
  .join(" ");
const windowsCommandLine = `npm run ${webScript}${
  windowsForwardedArguments ? ` -- ${windowsForwardedArguments}` : ""
}`;
const webProcess = spawn(
  process.platform === "win32" ? process.env.ComSpec || "cmd.exe" : "npm",
  process.platform === "win32"
    ? ["/d", "/s", "/c", windowsCommandLine]
    : webArguments,
  {
    cwd: root,
    stdio: "inherit",
  },
);

function stop(exitCode = 0) {
  if (stopping) return;
  stopping = true;
  if (restartTimer) clearTimeout(restartTimer);
  aiProcess?.kill("SIGTERM");
  webProcess.kill("SIGTERM");
  setTimeout(() => process.exit(exitCode), 1_000).unref();
}

webProcess.on("error", (error) => {
  console.error(`[ClassBridge] Không thể khởi động web: ${error.message}`);
  stop(1);
});
webProcess.on("exit", (code) => stop(code ?? 0));
process.on("SIGINT", () => stop(0));
process.on("SIGTERM", () => stop(0));

await ensureAi();
setInterval(() => void ensureAi(), 5_000);
