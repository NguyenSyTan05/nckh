import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

if (process.platform !== "win32") process.exit(0);

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const cacheModule = path.join(
  projectRoot,
  "node_modules",
  "vinext",
  "dist",
  "server",
  "static-file-cache.js",
);

const original = 'const pathname = "/" + relativePath;';
const patched = 'const pathname = "/" + relativePath.replaceAll("\\\\", "/");';
const source = await readFile(cacheModule, "utf8");

if (source.includes(patched)) process.exit(0);
if (!source.includes(original)) {
  throw new Error("Không tìm thấy đoạn mã vinext cần vá; hãy kiểm tra phiên bản vinext.");
}

await writeFile(cacheModule, source.replace(original, patched), "utf8");
console.log("[ClassBridge] Đã vá đường dẫn static asset của vinext trên Windows.");
