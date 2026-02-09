import { useState } from "react";
import API from "../api";
import { useToast } from "../components/Toast";
import { useSearchParams } from "react-router-dom";

export default function SetNewPassword() {
  const [params] = useSearchParams();
  const email = params.get("email");
  const code = params.get("code");
  const [password, setPassword] = useState("");
  const showToast = useToast();

  const handleNewPassword = async () => {
    try {
      await API.post("/auth/set-new-password", null, {
        params: {
          email,
          code,
          new_password: password
        }
      });

      showToast("Şifre başarıyla güncellendi!", "success");
      window.location.href = "/login";
    } catch {
      showToast("İşlem başarısız.", "error");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h2>Yeni Şifre</h2>

        <input
          type="password"
          placeholder="Yeni şifre"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={handleNewPassword}>Kaydet</button>
      </div>
    </div>
  );
}
