import { useState } from "react";
import API from "../api";           
import { Link, useNavigate } from "react-router-dom";
import { useToast } from "../components/Toast";
import "./Auth.css";

export default function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const showToast = useToast();   
  const handleRegister = async () => {
    try {
      await API.post("/auth/register", {
        username,
        email,
        password,
      });

      showToast("Kayıt başarılı! Şimdi giriş yapabilirsin.", "success");  // ⭐ alert yerine toast
      navigate("/login");
    } catch (err) {
      showToast("Kayıt sırasında bir hata oluştu.", "error");             // ⭐ alert yerine toast
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h2>Kayıt Ol</h2>

        <input
          type="text"
          placeholder="Kullanıcı adı"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

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

        <button onClick={handleRegister}>Kayıt Ol</button>

        <p className="auth-link">
          Zaten hesabın var mı? <Link to="/login">Giriş yap</Link>
        </p>
      </div>
    </div>
  );
}
