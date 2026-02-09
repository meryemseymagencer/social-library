import { useState } from "react";
import  API  from "../api";

export default function RatingBox({ itemId }) {
  const [value, setValue] = useState(0);

  const sendRating = async () => {
    try {
      await API.post(`/ratings/${itemId}`, { rating: value });
      alert("Puan gönderildi!");
    } catch (err) {
      console.error(err);
      alert("Puan gönderilemedi.");
    }
  };

  return (
    <div>
      <input
        type="number"
        min="1"
        max="10"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <button onClick={sendRating}>Gönder</button>
    </div>
  );
}
