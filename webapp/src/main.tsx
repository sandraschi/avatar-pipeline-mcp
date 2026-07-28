import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import PipelinePage from "./pages/PipelinePage";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <PipelinePage />
  </StrictMode>,
);
