import { Link, useNavigate } from "react-router-dom";
import { sessionManager } from "../core/session-manager";
import "./Navbar.css";

export default function Navbar() {
  const user = sessionManager.getCurrentUser();
  const navigate = useNavigate();

  const logout = () => {
    sessionManager.clearUser();
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">

        {/* LOGO */}
        <Link to="/" className="navbar-logo">
          Social Library
        </Link>
        
        {/* MENÜ */}
        <div className="navbar-links">
          <Link to="/" className="nav-link">Ana Sayfa</Link>
          <Link to="/feed" className="nav-link">Akış</Link>
        </div>

        {/* SAĞ TARAF */}
        <div className="navbar-actions">
          {user ? (
            <>
              <Link to={`/profile/${user.id}`} className="profile-btn">
                Profilim
              </Link>
              <button className="logout-btn" onClick={logout}>
                Çıkış Yap
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-auth login-btn">Giriş</Link>
              <Link to="/register" className="nav-auth register-btn">Kayıt Ol</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
