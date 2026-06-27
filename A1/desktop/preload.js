const { contextBridge, ipcRenderer } = require("electron");
contextBridge.exposeInMainWorld("api", {
  sendMessage: (msg) => ipcRenderer.send("chat-message", msg),
  onResponse: (cb) => ipcRenderer.on("chat-response", (_, d) => cb(d)),
});
