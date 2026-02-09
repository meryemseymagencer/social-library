import { useNavigate } from "react-router-dom";
import "./UnauthorizedModal.css";

export default function UnauthorizedModal({ show, onClose }) {
  if (!show) return null;

  const navigate = useNavigate();

  return (
    <div className="unauth-backdrop">
      <div className="unauth-modal">
        <h2>Giriş Yapmalısınız</h2>
        <p>Bu sayfayı görüntülemek için giriş yapmanız gerekiyor.</p>

        <div className="unauth-buttons">

          {/* ⭐ KAPAT → Anasayfaya yönlendirme */}
          <button
            className="cancel-btn"
            onClick={() => {
              onClose();      // Eğer modal state varsa kapatsın
              navigate("/");  // Ana sayfaya yönlendir
            }}
          >
            Kapat
          </button>

          {/* Giriş Yap → Login sayfası */}
          <button
            className="login-btn"
            onClick={() => navigate("/login")}
          >
            Giriş Yap
          </button>

        </div>
      </div>
    </div>
  );
}
