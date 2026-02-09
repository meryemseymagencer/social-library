import { useState } from "react";
import  API  from "../api";

export default function ReviewBox({ itemId }) {
  const [text, setText] = useState("");

  const sendReview = async () => {
    try {
      await API.post(`/reviews/${itemId}`, { review: text });
      alert("Yorum gönderildi!");
    } catch (err) {
      console.error(err);
      alert("Yorum gönderilemedi.");
    }
  };

  return (
    <div>
      <textarea 
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Yorumunuzu yazın..."
        rows={4}
        style={{ width: "100%", marginBottom: 10 }}
      />
      <button onClick={sendReview}>Gönder</button>
    </div>
  );
}
