import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
});

// 📌 SAYFA YENİLENDİĞİNDE TOKEN'I GERİ YÜKLE
const savedToken = localStorage.getItem("token");
if (savedToken) {
  API.defaults.headers.common["Authorization"] = `Bearer ${savedToken}`;
}

// 🔐 Token ekleyici
export function setAuthToken(token) {
  if (token) {
    API.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    localStorage.setItem("token", token);
  } else {
    delete API.defaults.headers.common["Authorization"];
    localStorage.removeItem("token");
  }
}

// 🛑 401 interceptor
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn("401: kullanıcı oturumu geçersiz.");

      localStorage.removeItem("token");
      localStorage.removeItem("user");

      if (window.showAuthModal) {
        window.showAuthModal();
      }
    }
    return Promise.reject(error);
  }
);

export default API;
