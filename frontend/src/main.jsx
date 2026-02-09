import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { setAuthToken } from "./api";

// Token varsa axios'a yükle
const token = localStorage.getItem("token");
if (token) setAuthToken(token);

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
