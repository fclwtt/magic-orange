const { app, BrowserWindow, ipcMain } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const crypto = require("crypto");

let mainWindow, pythonProcess, wsClient;
let wsPort = 0;
let wsToken = "";

// ── Dynamic port allocation ───────────────────────────────
function getFreePort() {
  const net = require("net");
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.listen(0, "127.0.0.1", () => {
      const p = srv.address().port;
      srv.close(() => resolve(p));
    });
    srv.on("error", reject);
  });
}

// ── Python backend lifecycle ──────────────────────────────
async function startPythonBackend() {
  wsPort = await getFreePort();
  wsToken = crypto.randomBytes(12).toString("hex");

  const backendPath = path.join(__dirname, "..", "main.py");
  const env = {
    ...process.env,
    MO_WS_PORT: String(wsPort),
    MO_WS_TOKEN: wsToken,
  };

  pythonProcess = spawn("python", [backendPath, "ws"], {
    cwd: path.join(__dirname, ".."),
    env,
    stdio: ["ignore", "pipe", "pipe"],
  });

  pythonProcess.stdout.on("data", (data) => {
    const line = data.toString().trim();
    if (line) console.log(`[mo] ${line}`);
  });
  pythonProcess.stderr.on("data", (data) => {
    const line = data.toString().trim();
    if (line) console.log(`[mo:err] ${line}`);
  });
  pythonProcess.on("close", (code) => {
    console.log(`[mo] Backend exited (code ${code})`);
    wsClient = null;
  });

  // Wait for backend to be ready
  await waitForBackend();
}

async function waitForBackend(timeoutMs = 30000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const result = await sendWsRequest("ping", {});
      if (result && result.pong) {
        console.log(`[mo] Backend ready on ws://127.0.0.1:${wsPort}`);
        return;
      }
    } catch (_) {
      // Still starting...
    }
    await sleep(500);
  }
  console.warn("[mo] Backend start timed out, launching UI anyway");
}

// ── WebSocket client (main process → Python backend) ──────
const WebSocket = require("ws");  // from desktop/node_modules

function connectWebSocket() {
  return new Promise((resolve, reject) => {
    const url = `ws://127.0.0.1:${wsPort}`;
    // Append token as query param if set
    const fullUrl = wsToken ? `${url}?token=${wsToken}` : url;
    const ws = new WebSocket(fullUrl);
    const pending = new Map();
    let msgId = 0;

    ws.on("open", () => {
      console.log("[mo] WebSocket connected");
      resolve(ws);
    });

    ws.on("message", (raw) => {
      try {
        const msg = JSON.parse(raw.toString());
        // JSON-RPC 2.0 response
        if (msg.id && pending.has(msg.id)) {
          const { resolve: res, reject: rej } = pending.get(msg.id);
          pending.delete(msg.id);
          if (msg.error) {
            rej(new Error(msg.error.message || "RPC error"));
          } else {
            res(msg.result);
          }
          return;
        }
        // Server event notification
        if (msg.method === "event" && msg.params) {
          if (mainWindow && !mainWindow.isDestroyed()) {
            mainWindow.webContents.send("chat-event", msg.params);
          }
        }
      } catch (_) {
        // Ignore non-JSON messages
      }
    });

    ws.on("close", () => {
      console.log("[mo] WebSocket disconnected");
      pending.forEach(({ reject: rej }) =>
        rej(new Error("WebSocket closed"))
      );
      pending.clear();
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send("chat-event", {
          type: "connection.closed",
          payload: {},
        });
      }
      // Auto-reconnect after a delay
      setTimeout(() => {
        if (pythonProcess && !pythonProcess.killed) {
          console.log("[mo] Attempting reconnect...");
          connectWebSocket().then((newWs) => {
            wsClient = newWs;
          }).catch(() => {});
        }
      }, 2000);
    });

    ws.on("error", (err) => {
      console.log(`[mo] WebSocket error: ${err.message}`);
    });

    // Attach request method
    ws._pending = pending;
    ws._msgId = msgId;
    ws.request = function (method, params) {
      return new Promise((resolve, reject) => {
        const id = String(++this._msgId);
        this._pending.set(id, { resolve, reject });
        this.send(JSON.stringify({
          jsonrpc: "2.0", id, method, params,
        }));
        // Timeout after 120s
        setTimeout(() => {
          if (this._pending.has(id)) {
            this._pending.delete(id);
            reject(new Error("Request timeout"));
          }
        }, 120000);
      });
    };
    ws.closeConnection = function () {
      ws.close();
    };
  });
}

async function sendWsRequest(method, params) {
  if (!wsClient || wsClient.readyState !== WebSocket.OPEN) {
    throw new Error("WebSocket not connected");
  }
  return wsClient.request(method, params);
}

// ── IPC handlers ──────────────────────────────────────────
function registerIPC() {
  ipcMain.handle("chat:send", async (_, text) => {
    try {
      // Create session on first message
      if (!global._sessionId) {
        const res = await sendWsRequest("session.create", {});
        global._sessionId = res.session_id;
      }
      const res = await sendWsRequest("prompt.submit", {
        session_id: global._sessionId,
        text,
      });
      return res;
    } catch (err) {
      return { error: err.message };
    }
  });

  ipcMain.handle("chat:new-session", async () => {
    if (global._sessionId) {
      try {
        await sendWsRequest("session.reset", {
          session_id: global._sessionId,
        });
      } catch (_) {}
    }
    global._sessionId = null;
    return { ok: true };
  });

  ipcMain.handle("chat:status", async () => {
    return {
      connected: wsClient && wsClient.readyState === WebSocket.OPEN,
      port: wsPort,
      sessionId: global._sessionId || null,
    };
  });
}

// ── Window & app lifecycle ────────────────────────────────
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 960,
    height: 720,
    minWidth: 600,
    minHeight: 400,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
    title: "MagicOrange",
    show: false,
  });

  mainWindow.loadFile(path.join(__dirname, "renderer", "index.html"));
  mainWindow.once("ready-to-show", () => mainWindow.show());
  mainWindow.on("closed", () => (mainWindow = null));
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

app.whenReady().then(async () => {
  console.log("[mo] Starting MagicOrange...");
  registerIPC();

  try {
    await startPythonBackend();
    wsClient = await connectWebSocket();
  } catch (err) {
    console.error("[mo] Failed to start backend:", err.message);
  }

  createWindow();
});

app.on("before-quit", () => {
  if (wsClient) wsClient.closeConnection();
  if (pythonProcess) pythonProcess.kill();
});

app.on("window-all-closed", () => {
  if (pythonProcess) pythonProcess.kill();
  if (wsClient) wsClient.closeConnection();
  app.quit();
});

app.on("activate", () => {
  if (mainWindow === null) createWindow();
});
