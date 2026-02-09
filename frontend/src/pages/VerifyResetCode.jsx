import { useState } from "react";
import API from "../api";
import { useToast } from "../components/Toast";
import { useSearchParams, useNavigate } from "react-router-dom";

export default function VerifyResetCode() {
  const [code, setCode] = useState("");
  const [params] = useSearchParams();
  const email = params.get("email");
  const showToast = useToast();
  const navigate = useNavigate();

  const handleVerify = async () => {
    try {
      await API.post("/auth/verify-reset-code", null, {
        params: {
          email: email,
          code: code
        }
      });


      showToast("Kod doğrulandı!", "success");

      navigate(`/set-new-password?email=${email}&code=${code}`);
    } catch {
      showToast("Kod yanlış veya süresi dolmuş.", "error");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h2>Kodu Doğrula</h2>

        <input
          type="text"
          placeholder="6 haneli kod"
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />

        <button onClick={handleVerify}>Doğrula</button>
      </div>
    </div>
  );
}
