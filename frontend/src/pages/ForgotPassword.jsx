import { useState } from "react";
import API from "../api";
import { useToast } from "../components/Toast";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const showToast = useToast();

  const handleSendCode = async () => {
    try {
      await API.post("/auth/request-reset", null, {
        params: { email }
      });
      showToast("Kod e-postana gönderildi!", "success");
      window.location.href = `/verify-code?email=${email}`;
    } catch {
      showToast("E-posta bulunamadı.", "error");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h2>Şifre Sıfırlama</h2>

        <input
          type="email"
          placeholder="E-posta adresi"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <button onClick={handleSendCode}>Kodu Gönder</button>
      </div>
    </div>
  );
}
