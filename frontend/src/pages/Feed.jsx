// src/pages/Feed.jsx
import { useEffect, useState } from "react";
import API from "../api";
import { Link, useNavigate } from "react-router-dom";
import { sessionManager } from "../core/session-manager";
import "./Feed.css";

function truncate(text, max = 120) {
  if (!text) return "";
  return text.length > max ? text.substring(0, max) + "..." : text;
}

function formatTime(dateString) {
  const d = new Date(dateString);
  const diffMs = Date.now() - d.getTime();
  const diffMin = Math.floor(diffMs / 60000);


  if (diffMin < 1) return "az önce";
  if (diffMin < 60) return `${diffMin} dk önce`;

  const diffHour = Math.floor(diffMin / 60);
  if (diffHour < 24) return `${diffHour} sa önce`;

  const diffDay = Math.floor(diffHour / 24);
  if (diffDay < 7) return `${diffDay} gün önce`;

  return d.toLocaleDateString("tr-TR");
}

export default function Feed() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState("");
  const currentUserId = sessionManager.getCurrentUserId();

      useEffect(() => {
      API.get("/activity/feed")
        .then((res) => {
          setActivities(res.data);
          setLoading(false);
        })
        .catch(() => {
          // 401 durumunda interceptor zaten modal açacak
          setLoading(false);
        });
    }, []);
    async function openComments(a) {
  setSelectedActivity(a);

  const res = await API.get(`/activity/${a.id}/comments`);
  setComments(res.data);
}
async function submitComment() {
  if (!commentText.trim()) return;

  const res = await API.post(
    `/activity/${selectedActivity.id}/comment`,
    null,
    { params: { content: commentText } }
  );

  setComments([...comments, res.data]);
  setCommentText("");

  // feed üzerindeki comment_count da artsın
  selectedActivity.comment_count++;
}

async function toggleLike(a) {
  try {
    if (a.is_liked_by_me) {
      await API.delete(`/activity/${a.id}/like`);
      a.like_count--;
      a.is_liked_by_me = false;
    } else {
      await API.post(`/activity/${a.id}/like`);
      a.like_count++;
      a.is_liked_by_me = true;
    }

    setActivities([...activities]); // UI güncelleme

  } catch (err) {
    console.log("Like error:", err);
  }
}


  if (loading)
    return <p style={{ padding: 20, color: "#ccc" }}>Yükleniyor...</p>;

  return (
  <div className="feed-page">

    <h1 className="feed-title">Akış</h1>
    <p className="feed-subtitle">Takip ettiğin kullanıcıların son aktiviteleri</p>

    {activities.length === 0 && (
      <div className="feed-empty">
        <p>Hiç aktivite yok.</p>
        <p>Başka kullanıcıları takip etmeyi deneyebilirsin.</p>
      </div>
    )}

    <div className="feed-list">
      {activities.map((a) => (
        <div key={a.id} className="feed-card">

          <div className="feed-poster">
            {a.item ? (
              <img
                src={a.item.poster_url}
                alt={a.item.title}
                onClick={() => navigate(`/item/${a.item.id}`)}
              />
            ) : (
              <div className="feed-poster-placeholder">—</div>
            )}
          </div>

          <div className="feed-content">

            <div className="feed-header">
              <img
                src={a.user?.avatar_url || "https://via.placeholder.com/40"}
                alt={a.user?.username}
                className="feed-avatar"
                onClick={() => navigate(`/profile/${a.user?.id}`)}
              />

              <div>
                <Link to={`/profile/${a.user?.id}`} className="feed-username">
                  {a.user?.username}
                </Link>
                <div className="feed-time">{formatTime(a.created_at)}</div>
              </div>
            </div>

            <div className="feed-text">

              {a.activity_type === "rating" && (
                <div className="feed-rating-box">
                  <p>
                    ⭐{" "}
                    <Link to={`/item/${a.item?.id}`} className="feed-item-title">
                      {a.item?.title}
                    </Link>{" "}
                    için{" "}
                    <span className="feed-rating-score">
                      {a.rating_value}/5
                    </span>{" "}
                    puan verdi.
                  </p>
                </div>
              )}

              {a.activity_type === "review" && (
                <div className="feed-review-box">
                  <p>
                    ✍️{" "}
                    <Link to={`/item/${a.item?.id}`} className="feed-item-title">
                      {a.item?.title}
                    </Link>{" "}
                    için yorum yaptı:
                  </p>

                  <p className="feed-review">
                    {truncate(a.review_excerpt, 120)}
                  </p>
                </div>
              )}

              {a.activity_type === "list_add" && (
                <div className="feed-list-add-box">
                  <p className="feed-list-add-title">📚 Liste Güncellemesi</p>
                  <p>
                    <Link to={`/item/${a.item?.id}`} className="feed-item-title">
                      {a.item?.title}
                    </Link>{" "}
                    adlı içerik bir listeye eklendi.
                  </p>
                </div>
              )}

            </div>

            <div className="feed-footer">
              <button
                className="feed-footer-btn"
                onClick={() => toggleLike(a)}
                style={{ color: a.is_liked_by_me ? "#40BCF4" : "#9db5cc" }}
              >
                👍 ({a.like_count || 0})
              </button>

              <button
                className="feed-footer-btn"
                onClick={() => openComments(a)}
              >
                💬 ({a.comment_count || 0})
              </button>
            </div>

          </div>
        </div>
      ))}
    </div>

    {/* MODAL BURAYA GELECEK */}
    {selectedActivity && (
      <div className="comment-modal">
        <div className="comment-modal-inner">

          <h3>Yorumlar</h3>

          <div className="comment-list">
            {comments.map((c) => (
              <div key={c.id} className="comment-item">
                <img src={c.user.avatar_url} className="comment-avatar" />
                <div className="comment-body">
                  <strong>{c.user.username}</strong>
                  <p>{c.content}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="comment-input">
            <input
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              placeholder="Yorum yaz..."
            />
            <button onClick={submitComment}>Gönder</button>
          </div>

          <button className="close-modal" onClick={() => setSelectedActivity(null)}>
            Kapat
          </button>

        </div>
      </div>
    )}

  </div>
);
}

