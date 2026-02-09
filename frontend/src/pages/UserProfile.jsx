import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API  from "../api";
import "./UserProfile.css";

export default function UserProfile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [showFollowModal, setShowFollowModal] = useState(null);
// "followers", "following" veya null

  const [userId, setUserId] = useState(id || null);
  const [user, setUser] = useState(null);
  const [tab, setTab] = useState("posts");

  const [posts, setPosts] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [lists, setLists] = useState([]);

  const [followers, setFollowers] = useState([]);
  const [following, setFollowing] = useState([]);

  const [loading, setLoading] = useState(true);
  const [followLoading, setFollowLoading] = useState(false);

  useEffect(() => {
    async function resolveUser() {
      if (!id) {
        try {
          const me = await API.get("/users/me");
          setUserId(me.data.id);
        } catch (err) {
        // 401 burada denk gelir → modal açılır
          return;
        }
      } else {
        setUserId(id);
      }
    }
    resolveUser();
  }, [id]);

  useEffect(() => {
    if (!userId) return;

    async function loadAll() {
        setLoading(true);
        try {
          const u = await API.get(`/users/${userId}`);
          const p = await API.get(`/users/${userId}/posts`);
          const r = await API.get(`/users/${userId}/reviews`);
          const l = await API.get(`/lists/user/${userId}`);
          const f1 = await API.get(`/users/${userId}/followers`);
          const f2 = await API.get(`/users/${userId}/following`);

          setUser(u.data);
          setPosts(p.data);
          setReviews(r.data);
          setLists(l.data);
          setFollowers(f1.data);
          setFollowing(f2.data);
        } catch (err) {
          // 401 burada denk gelirse modal açılır
          return;
        } finally {
          setLoading(false);
        }
      }


    loadAll();
  }, [userId]);

  if (loading) return <div className="loader">Yükleniyor...</div>;
  if (!loading && !user) { return <p>Kullanıcı bulunamadı.</p>;}

  const handleFollow = async () => {
    setFollowLoading(true);
    await API.post(`/follow/${user.id}`);
    const f = await API.get(`/users/${user.id}/followers`);
    const u = await API.get(`/users/${user.id}`);
    setFollowers(f.data);
    setUser(u.data);
    setFollowLoading(false);
  };

  const handleUnfollow = async () => {
    setFollowLoading(true);
    await API.delete(`/follow/${user.id}`);
    const f = await API.get(`/users/${user.id}/followers`);
    const u = await API.get(`/users/${user.id}`);
    setFollowers(f.data);
    setUser(u.data);
    setFollowLoading(false);
  };
  const handleAvatarUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await API.post("/users/me/avatar", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      // Avatar güncellendi → kullanıcı profilini yeniden çek
      const updated = await API.get(`/users/${userId}`);
      setUser(updated.data);

    } catch (err) {
      console.log(err);
      alert("Avatar yüklenemedi!");
    }
  };

  return (
        <div className="apple-profile-page">
          {/* -------- MODAL -------- */}
          {showFollowModal && (
            <div className="follow-modal-backdrop">
              <div className="follow-modal">
                <h2>
                  {showFollowModal === "followers" ? "Takipçiler" : "Takip Edilenler"}
                </h2>

                <button className="close-btn" onClick={() => setShowFollowModal(null)}>
                  ✕
                </button>

                <div className="follow-list">
                  {(showFollowModal === "followers" ? followers : following).map(
                    (usr) => (
                      <div
                        key={usr.id}
                        className="follow-user"
                        onClick={() => navigate(`/profile/${usr.id}`)}>
                        <img src={usr.avatar_url || "https://via.placeholder.com/50"} />
                        <span>{usr.username}</span>
                      </div>
                    )
                  )}
                </div>
            </div>
       </div>
    )}

      {/* HEADER */}
      <div className="apple-header">
        
        <div className="avatar-wrapper">
          <img src={user.avatar_url || "https://via.placeholder.com/250"} className="apple-avatar"
          onClick={() => user.is_me && document.getElementById("avatarInput").click()} 
          style={{ cursor: user.is_me ? "pointer" : "default" }} />
          <input id="avatarInput" type="file" accept="image/*" style={{ display: "none" }} onChange={handleAvatarUpload} />
        </div>

        <div className="apple-user-info">
          <h1>{user.username}</h1>
          <p>{user.bio || "Biyo yok"}</p>

          {!user.is_me && (
            user.is_following ? (
              <button className="apple-btn unfollow" onClick={handleUnfollow}>
                Takibi Bırak
              </button>
            ) : (
              <button className="apple-btn follow" onClick={handleFollow}>
                Takip Et
              </button>
            )
          )}

          {user.is_me && (
            <button
              className="apple-btn edit"
              onClick={() => navigate("/edit-profile")}
            >
              Profili Düzenle
            </button>
          )}

          {/* STATS */}
            <div className="apple-stats">
              <div >
                <strong>{posts.length}</strong>
                <span>Gönderi</span>
              </div>

              <div onClick={() => setShowFollowModal("followers")}>
                <strong>{followers.length}</strong>
                <span>Takipçi</span>
              </div>

              <div onClick={() => setShowFollowModal("following")}>
                <strong>{following.length}</strong>
                <span>Takip</span>
              </div>
            </div>
        </div>
      </div>

      {/* TABS */}
      <div className="apple-tabs">
        <button className={tab === "posts" ? "active" : ""} onClick={() => setTab("posts")}>Gönderiler</button>
        <button className={tab === "reviews" ? "active" : ""} onClick={() => setTab("reviews")}>Yorumlar</button>
        <button className={tab === "lists" ? "active" : ""} onClick={() => setTab("lists")}>Listeler</button>
      </div>

      {/* CONTENT */}
      <div className="apple-content">

        {/* POSTS */}
        {tab === "posts" && (
          <div className="apple-post-grid">
            {posts.length === 0 ? (
              <p className="empty">Gönderi yok.</p>
            ) : posts.map((p) => (
              <div key={p.id} className="apple-post-card">
                <img src={p.poster_url} />
              </div>
            ))}
          </div>
        )}

        {/* REVIEWS */}
        {tab === "reviews" && (
          <div className="apple-review-list">
            {reviews.map((r) => (
              <div key={r.id} className="apple-review-card">
                <h4>{r.item_title}</h4>
                <p>{r.review_text}</p>
              </div>
            ))}
          </div>
        )}

        {/* LISTS */}
         {tab === "lists" && (
          <div className="apple-list-grid">

            {lists.length === 0 && (
              <p className="empty">Henüz liste yok.</p>
            )}

            {lists.map((lst) => (
              <div
                key={lst.id}
                className="apple-list-card"
                onClick={() => navigate(`/lists/${lst.id}`)}
              >
                <h4>{lst.name}</h4>
                <p>{lst.description}</p>

                <div className="list-preview">
                  {(lst.items ?? []).slice(0, 4).map((item) => (
                    <img
                      key={item.id}
                      src={item.poster_url}
                      className="list-thumb"
                    />
                  ))}
                </div>
              </div>
            ))}

          </div>
        )}

      </div>
    </div>
  );
}
