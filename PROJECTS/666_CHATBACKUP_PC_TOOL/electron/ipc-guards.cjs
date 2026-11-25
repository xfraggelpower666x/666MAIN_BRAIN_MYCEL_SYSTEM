"use strict";
// Only the application's own main frame may call privileged ChatBackup IPC.
// Imported Studio pages and secondary settings windows have separate contracts.
function trustedMainFrame(event, mainWindow) {
  return Boolean(
    mainWindow && !mainWindow.isDestroyed() && event &&
    event.sender === mainWindow.webContents &&
    event.senderFrame === mainWindow.webContents.mainFrame
  );
}
function assertTrustedMainFrame(event, mainWindow) {
  if (!trustedMainFrame(event, mainWindow)) throw new Error('Unauthorized ChatBackup IPC caller');
}
module.exports = { trustedMainFrame, assertTrustedMainFrame };
