import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import API from "../api";
import { useToast } from "../components/Toast";
import "./ItemDetail.css";
import { sessionManager } from "../core/session-manager";

export default function ItemDetail() {
  const { id } = useParams();
  const toast = useToast();

  const [item, setItem] = useState(null);
  const [summary, setSummary] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  const [listsPopup, setListsPopup] = useState(false);
  const [myLists, setMyLists] = useState([]);

  const [createListModal, setCreateListModal] = useState(false);
  const [newListName, setNewListName] = useState("");
    
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState("");

  async function addToDefaultList(name) {
        try {
          // 1) Kullanıcının listelerini çek
          const res = await API.get("/lists/me");
          const myLists = res.data;

          // 2) İstenen default listeyi bul
          const target = myLists.find((l) => l.name === name);

          if (!target) {
            toast(`${name} listesi bulunamadı!`, "error");
            return;
          }

          const listId = target.id;

          // 3) Item'ı listeye ekle
          await API.post(`/lists/${listId}/items/${item.id}`);

          toast("🎉 Listeye başarıyla eklendi!", "success");
          setListsPopup(false);

        } catch (err) {
          console.error(err);
          toast("Ekleme sırasında bir hata oluştu!", "error");
        }
      }


  const startEdit = (r) => {
    setEditingId(r.id);
    setEditText(r.content);
  };

  const saveEdit = async () => {
    try {
      await API.put(`/reviews/${editingId}`, { content: editText });
      toast("Yorum güncellendi!", "success");
      setEditingId(null);
      setEditText("");
      reloadReviews();
    } catch {
      toast("Yorum güncellendi!", "success");
    }
  };

  const deleteReview = async (id) => {
    if (!confirm("Yorumu silmek istediğine emin misin?")) return;

    try {
      await API.delete(`/reviews/${id}`);
      toast("Yorum silindi!", "success");
      reloadReviews();
    } catch {
      toast("Yorum silinemedi!", "error");
    }
  };

  const reloadSummary = async () => {
    const sumRes = await API.get(`/rating/${id}/summary`);
    setSummary(sumRes.data);
  };
  // === ITEM'E LİSTE EKLE ===
  const addToList = async (listId) => {
    try {
      await API.post(`/lists/${listId}/items/${id}`);
      toast("Listeye eklendi! ✔️", "success");
      setListsPopup(false);
    } catch {
      toast("Bu listeye zaten ekli olabilir!", "error");
    }
  };
  // === YENİ LİSTE OLUŞTUR ===
  const handleCreateList = async () => {
    if (!newListName.trim()) {
      toast("Liste adı boş olamaz!", "error");
      return;
    }

    try {
      await API.post("/lists/me", { name: newListName });
      toast("Liste oluşturuldu! 🎉", "success");

      setNewListName("");
      setCreateListModal(false);

      const listsRes = await API.get("/lists/me");
      setMyLists(listsRes.data);
    } catch {
      toast("Liste oluşturulurken hata oluştu!", "error");
    }
  };

  const reloadReviews = async () => {
    const revRes = await API.get(`/reviews/item/${id}`);
    setReviews(revRes.data);
  };
  useEffect(() => {
    async function load() {
      try {
        const itemRes = await API.get(`/items/${id}`);
        setItem(itemRes.data);

        const revRes = await API.get(`/reviews/item/${id}`);
        setReviews(revRes.data);

        try {
          const sumRes = await API.get(`/rating/${id}/summary`);
          setSummary(sumRes.data);
        } catch {
          setSummary({ average: null, count: 0, user_score: null });
        }

        const token = localStorage.getItem("token");

        if (token) {
          try {
            const listsRes = await API.get("/lists/me");
            setMyLists(listsRes.data);
          } catch {
            setMyLists([]);
          }
        } else {
          setMyLists([]);
        }

      } catch (err) {
        console.log(err);
        toast("Veriler yüklenirken hata oluştu!", "error");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [id]);
  if (loading || !item) return <p style={{ padding: 20 }}>Yükleniyor...</p>;
  return (
    <>
      <div className="item-detail-container">
        <div className="item-page">
         <div className="item-header">

        <img src={item.poster_url} className="item-poster" alt="poster" />
        <div className="item-description-box">
            <h2>{item.title}</h2>

            {item.authors && (
              <p className="item-authors"><strong>Yazar:</strong> {item.authors}</p>
            )}

            <p className="item-year"><strong>Yıl:</strong> {item.year}</p>

            <p className="item-description">
              {item.description || "Açıklama bulunmuyor."}
            </p>
          </div>

        <div className="item-info">
          <button className="add-list-btn" onClick={() => setListsPopup(true)}>
            + Listeye Ekle
          </button>
            {listsPopup && (
              <div className="modal-bg" onClick={() => setListsPopup(false)}>
                <div className="modal" onClick={(e) => e.stopPropagation()}>

                  {/* KAPATMA */}
                  <button className="modal-close-btn" onClick={() => setListsPopup(false)}>✖</button>

                  <h2>Listene Ekle</h2>

                  {/* YENİ LİSTE OLUŞTUR */}
                  <button className="modal-create-btn" onClick={() => setCreateListModal(true)}>
                    + Yeni Liste Oluştur
                  </button>

                  {/* DEFAULT LİSTELER */}
                  <div className="default-list-buttons">

                    {["Okudum", "Okuyacağım", "İzledim", "İzleyeceğim"].map((name) => (
                      <button
                        key={name}
                        className="default-list-btn"
                        onClick={() => addToDefaultList(name)}
                      >
                        {name}
                      </button>
                    ))}

                  </div>

                </div>
              </div>
            )}

        </div>

      </div>
          {summary && (
            <div className="rating-box">
              <h2>Puanlama Özeti</h2>
              <p><strong>Ortalama:</strong> {summary.average ?? "-"}</p>
              <p><strong>Toplam Oy:</strong> {summary.count}</p>
              <p><strong>Senin Puanın:</strong> {summary.user_score ?? "-"}</p>
            </div>
          )}
          <RatingBox itemId={id} reloadSummary={reloadSummary} />
          <ReviewBox itemId={id} reloadReviews={reloadReviews} />
          {/* YORUMLAR LİSTESİ */}
          <div className="reviews-section">
            <h2>Yorumlar</h2>
          {reviews.length === 0 ? (
            <p className="no-reviews">Bu içerik için henüz yorum yapılmamış.</p>
          ) : (
            reviews.map((r) => (
              <div key={r.id} className="review-card">

              <div className="review-header">
                <div className="review-user-info">
                  <Link to={`/user/${r.user?.id}`} className="review-username"> {r.user?.username} </Link>

                  <span className="review-date">
                    {new Date(r.created_at).toLocaleDateString("tr-TR")}
                  </span>
                </div>

                {/* SADECE SAHİBİNE GÖRÜNÜR */}
                {sessionManager.getCurrentUser()?.id === r.user?.id && (
                  <div className="review-actions">
                    <button className="review-btn edit" onClick={() => startEdit(r)}>
                       Düzenle
                    </button>
                    <button className="review-btn delete" onClick={() => deleteReview(r.id)}>
                       Sil
                    </button>
                  </div>
                )}
              </div>

              <p className="review-text">{r.content}</p>

            </div>

              
            ))
          )}

          </div>
          {/* ==== YORUM DÜZENLEME MODALI ==== */}
          {editingId && (
            <div className="edit-modal-bg">
              <div className="edit-modal">

                <h2>Yorumu Düzenle</h2>

                <textarea
                  className="edit-textarea"
                  value={editText}
                  onChange={(e) => setEditText(e.target.value)}
                />

                <div className="edit-modal-buttons">
                
                  <button className="cancel-btn" onClick={() => setEditingId(null)}>İptal</button>
                  <button className="save-btn" onClick={saveEdit}>Kaydet</button>
                </div>

              </div>
            </div>
          )}


        </div>
      </div>
      {/* === LİSTE SEÇİM POPUP === */}
      {listsPopup && (
        <div className="popup-bg" onClick={() => setListsPopup(false)}>
          <div className="popup" onClick={(e) => e.stopPropagation()}>

            {/*  KAPATMA BUTONU  */}
            <button
              className="close-btn"
              onClick={() => setListsPopup(false)}
            >
              ✖
            </button>

            <h3>Listene Ekle</h3>

            <button
              className="list-select-btn"
              style={{ background: "#00c78b", fontWeight: "700" }}
              onClick={() => {
                setListsPopup(false);
                setCreateListModal(true);
              }}
            >
              + Yeni Liste Oluştur
            </button>

            {myLists.length === 0 && <p>Hiç listen yok.</p>}

            {myLists.map((l) => (
              <button
                key={l.id}
                className="list-select-btn"
                onClick={() => addToList(l.id)}
              >
                {l.name}
              </button>
            ))}

          </div>
        </div>
      )}
      {createListModal && (
        <div className="modal-bg" onClick={() => setCreateListModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <button
              className="modal-close-btn"
              onClick={() => setCreateListModal(false)}
            >
              ✖
            </button>
            <h2>Yeni Liste Oluştur</h2>

            <input
              type="text"
              placeholder="Liste adı..."
              value={newListName}
              onChange={(e) => setNewListName(e.target.value)}
            />

            <div className="modal-buttons">
              <button className="btn-create" onClick={handleCreateList}>
                Oluştur
              </button>
              <button
                className="btn-cancel"
                onClick={() => setCreateListModal(false)}
              >
                İptal
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
// ==================== RATING BOX ====================
function RatingBox({ itemId, reloadSummary }) {
  const showToast = useToast();
  const [rating, setRating] = useState(null);
  const [hover, setHover] = useState(null);

  const sendRating = async (value) => {
    try {
      await API.post(`/rating/${itemId}`, { score: value });
      setRating(value);
      showToast("Puan kaydedildi!", "success");

      await reloadSummary();   // ⭐⭐ EKLENEN SATIR
    } catch (err) {
      showToast("Puan verirken hata!", "error");
    }
  };

  return (
    <div className="rating-box">
      <h2>Puan Ver</h2>
      <div>
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={`star ${(hover || rating) >= star ? "filled" : ""}`}
            onMouseEnter={() => setHover(star)}
            onMouseLeave={() => setHover(null)}
            onClick={() => sendRating(star)}
          >
            ★
          </span>
        ))}
      </div>
    </div>
  );
}
// ==================== REVIEW BOX ====================
function ReviewBox({ itemId, reloadReviews }) {
  const showToast = useToast();
  const [text, setText] = useState("");

  const sendReview = async () => {
    if (!text.trim()) {
      showToast("Yorum boş olamaz!", "error");  // düzeltildi
      return;
    }
    try {
      await API.post(`/reviews/${itemId}`, { content: text });
      showToast("Yorum gönderildi!", "success");
      setText("");
      reloadReviews();
    } catch (err) {
      showToast("Yorum gönderilemedi!", "error");
    }
  };

  return (
    <div className="add-review">
      <h2>Yorum Yaz</h2>
      <textarea value={text} onChange={(e) => setText(e.target.value)} />
      <button onClick={sendReview}>Gönder</button>
    </div>
  );
}