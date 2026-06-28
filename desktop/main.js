const { app, BrowserWindow, ipcMain } = require("electron");
const { spawn } = require("child_process");
const path = require("path");

let mainWindow, pythonProcess;

function startPythonBackend() {
  const backendPath = path.join(__dirname, "..", "main.py");
  pythonProcess = spawn("python3", [backendPath, "--mode=ws"], {
    stdio: ["pipe", "pipe", "pipe"],
  });
  pythonProcess.stdout.on("data", (data) => console.log(`[backend] ${data}`));
  pythonProcess.stderr.on("data", (data) => console.log(`[backend:err] ${data}`));
  pythonProcess.on("close", (code) => console.log(`Backend exited: ${code}`));
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 700,
    webPreferences: { preload: path.join(__dirname, "preload.js") },
    title: "MagicOrange",
  });
  mainWindow.loadFile("renderer/index.html");
  mainWindow.on("closed", () => (mainWindow = null));
}

app.whenReady().then(() => {
  startPythonBackend();
  createWindow();
});

app.on("before-quit", () => {
  if (pythonProcess) pythonProcess.kill();
});

app.on("window-all-closed", () => {
  if (pythonProcess) pythonProcess.kill();
  app.quit();
});
