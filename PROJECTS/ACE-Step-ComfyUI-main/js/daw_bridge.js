import { app } from "../../scripts/app.js";
import { handleDawMessage } from "./daw_bridge_core.mjs";

app.registerExtension({
    name: "AceStep.DawWorkflowBridge",
    setup() {
        window.addEventListener("message", event => void handleDawMessage(app, window, event));
    },
});
