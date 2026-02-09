import { useState } from "react";
import API from "../api";
import { useNavigate, useSearchParams } from "react-router-dom";
import "./Auth.css";
import { useToast } from "../components/Toast";

export default function ResetPassword() {
  const [password, setPassword] = useState("");
  const [params] = useSearchParams();
  const toast = useToast();
  const navigate = useNavigate();

  const email = params.get("email");
  const code = params.get("code");

  const handleReset = async () => {
    try {
      await API.post("/auth/reset-password", {
        email,
        code,
        new_password: password,
      });

      toast("Şifren başarıyla değiştirildi.", "success");
      navigate("/login");
    } catch (err) {
      toast("Kod geçersiz veya süresi dolmuş olabilir.", "error");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h2>Yeni Şifre Belirle</h2>

        <input
          type="password"
          placeholder="Yeni şifre"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={handleReset}>Şifreyi Güncelle</button>
      </div>
    </div>
  );
}
