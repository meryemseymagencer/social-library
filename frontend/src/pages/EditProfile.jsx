import { useState, useEffect } from "react";
import API from "../api";
import { useToast } from "../components/Toast";
import "./EditProfile.css";
import { useNavigate } from "react-router-dom";

export default function EditProfile() {
  const toast = useToast();
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [username, setUsername] = useState("");
  const [bio, setBio] = useState("");

  useEffect(() => {
    API.get("/users/me")
      .then((res) => {
        setUser(res.data);
        setUsername(res.data.username);
        setBio(res.data.bio || "");
      })
      .catch(() => {
        toast("Profil bilgileri alınamadı!", "error");
      });
  }, []);

  const handleSave = async () => {
    try {
      await API.put("/users/me", { username, bio });

      toast("Profil güncellendi! ✔️", "success");
      setTimeout(() => navigate("/me"), 700);
    } catch (err) {
      toast("Profil güncellenirken hata oluştu!", "error");
    }
  };

  const handleAvatarChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      await API.post("/users/me/avatar", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const updated = await API.get("/users/me");
      setUser(updated.data);

      toast("Avatar güncellendi!", "success");
    } catch (err) {
      toast("Avatar yüklenemedi!", "error");
    }
  };

  return (
    <div className="edit-container">
      <h2>Profili Düzenle</h2>

      <div className="avatar-section">
        <div className="avatar-wrapper">
          <img
            src={
              user?.avatar_url
                ? user.avatar_url + "?t=" + Date.now()
                : "https://via.placeholder.com/250"
            }
            className="avatar-img"
            alt="Avatar"
          />

          <div className="avatar-overlay">
            <span className="camera-icon">📷</span>
            <span className="avatar-text">Avatarı Değiştir</span>
          </div>

          <input
            type="file"
            accept="image/*"
            className="avatar-input"
            onChange={handleAvatarChange}
          />
        </div>
      </div>

      <label>Kullanıcı Adı</label>
      <input
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />

      <label>Biyografi</label>
      <textarea
        value={bio}
        onChange={(e) => setBio(e.target.value)}
      />

      <button className="save-btn" onClick={handleSave}>
        Kaydet
      </button>
    </div>
  );
}
