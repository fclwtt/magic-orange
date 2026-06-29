const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("moAPI", {
  // Send a chat message — returns {status: "processing"} or {error: "..."}
  sendMessage: (text) => ipcRenderer.invoke("chat:send", text),

  // Start a new session
  newSession: () => ipcRenderer.invoke("chat:new-session"),

  // Get connection status
  getStatus: () => ipcRenderer.invoke("chat:status"),

  // Listen for streaming events from the backend
  onEvent: (callback) => {
    const handler = (_, event) => callback(event);
    ipcRenderer.on("chat-event", handler);
    // Return cleanup function
    return () => ipcRenderer.removeListener("chat-event", handler);
  },
});
