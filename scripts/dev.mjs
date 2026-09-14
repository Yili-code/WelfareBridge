import { spawn, spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
process.chdir(root);
if (existsSync(".env.local")) process.loadEnvFile(".env.local");
const python = process.env.PYTHON || path.join(root, "backend", ".venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
if (!existsSync(python)) {
 console.error("Python 環境尚未建立。請依 README 安裝 backend/.venv 與 requirements.txt。");
 process.exit(1);
}
const children = [];
let stopping = false;
function stop(code = 0) {
 if (stopping) return;
 stopping = true;
 for (const child of children) {
  if (!child.pid) continue;
  if (process.platform === "win32") spawn("taskkill", ["/PID", String(child.pid), "/T", "/F"], { windowsHide: true, stdio: "ignore" });
  else child.kill("SIGTERM");
 }
 setTimeout(() => process.exit(code), 500);
}
function run(command, args, cwd) {
 const child = spawn(command, args, { cwd, stdio: "inherit", windowsHide: true, env: process.env });
 children.push(child);
 child.on("error", error => { console.error(error.message); stop(1); });
 child.on("exit", code => { if (!stopping) stop(code || 1); });
 return child;
}
for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => stop());
const origin = process.env.BENEFIT_API_URL || "http://127.0.0.1:8000";
if (!process.env.BENEFIT_API_URL) {
 const pingMongo = () => spawnSync(python, ["-c", "from app.db import ping; raise SystemExit(0 if ping() else 1)"], { cwd: path.join(root, "backend"), stdio: "ignore", windowsHide: true, timeout: 7000 }).status === 0;
 if (!pingMongo()) {
  run(process.execPath, [path.join(root, "scripts/mongo.mjs")], root);
  let ready = false;
  for (let i = 0; i < 10 && !stopping; i++) {
   await new Promise(resolve => setTimeout(resolve, 500));
   if (pingMongo()) { ready = true; break; }
  }
  if (!ready) { console.error("MongoDB 未就緒，請查看 data/mongodb/mongod.log。"); stop(1); }
 }
 if (stopping) process.exit(1);
 run(python, ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"], path.join(root, "backend"));
}
let healthy = false;
for (let i = 0; i < 60 && !stopping; i++) {
 try {
  const res = await fetch(origin + "/api/health", { signal: AbortSignal.timeout(5000) });
  if (res.ok && (await res.json()).database === "ok") { healthy = true; break; }
 } catch {}
 await new Promise(resolve => setTimeout(resolve, 1000));
}
if (!healthy) {
 console.error("後端或 MongoDB 尚未就緒。先執行 docker compose up -d mongo，再重試。");
 stop(1);
} else if (!stopping) {
 const args = process.argv.slice(2);
 if (!args.includes("--port") && !args.includes("-p")) args.push("--port", process.env.PORT || "3000");
 run(process.execPath, [path.join(root, "node_modules/next/dist/bin/next"), "dev", ...args], root);
}
