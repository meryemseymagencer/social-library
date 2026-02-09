import { useState } from "react";
import API, { setAuthToken } from "../api";
import { Link, useNavigate } from "react-router-dom";
import { sessionManager } from "../core/session-manager";
import { useToast } from "../components/Toast"; 
import "./Auth.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const toast = useToast();   

  const handleLogin = async () => {
    try {
      const res = await API.post("/auth/login", {
        email,
        password,
      });

      setAuthToken(res.data.access_token);

      const me = await API.get("/users/me");
      sessionManager.saveUser(me.data);

      toast("Giriş başarılı!", "success");  
      navigate("/feed");

    } catch (err) {
      toast("Giriş hatalı!", "error");      
    }
  };

  return (
  <div className="auth-container">
    <div className="auth-box">
      <h2>Giriş Yap</h2>

      <input
        type="email"
        placeholder="E-posta"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <input
        type="password"
        placeholder="Şifre"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button onClick={handleLogin}>Giriş Yap</button>

      {/* ⭐ Şifremi Unuttum linkini ekledik */}
      <p className="auth-link">
        <Link to="/forgot-password">Şifremi Unuttum</Link>
      </p>

      <p className="auth-link">
        Hesabın yok mu? <Link to="/register">Kayıt ol</Link>
      </p>
    </div>
  </div>
);

}
