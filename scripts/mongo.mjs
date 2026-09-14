import { spawn } from "node:child_process";
import { existsSync, mkdirSync, readdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const tools = path.join(root, "data/tools/mongodb");
const local = existsSync(tools) ? readdirSync(tools).map(name => path.join(tools, name, "bin/mongod.exe")).find(existsSync) : undefined;
const binary = process.env.MONGOD_PATH || local || "mongod";
const data = path.join(root, "data/mongodb");
mkdirSync(data, { recursive: true });
const child = spawn(binary, ["--bind_ip", "127.0.0.1", "--port", "27017", "--dbpath", data, "--logpath", path.join(data, "mongod.log"), "--logappend"], { stdio: "inherit", windowsHide: true });
child.on("error", error => { console.error("MongoDB 啟動失敗。請先執行 Setup-WelfareBridge.ps1，或設定 MONGOD_PATH。", error.message); process.exitCode = 1; });
child.on("exit", code => { process.exitCode = code || 0; });
for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => child.kill("SIGTERM"));
