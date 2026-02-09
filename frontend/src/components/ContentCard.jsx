// src/components/ContentCard.jsx
import "./ContentCard.css";

export default function ContentCard({ title, year, poster }) {
  return (
    <div className="content-card">
      <div className="card-image-wrapper">
        <img src={poster} alt={title} className="card-image" />
      </div>

      <div className="card-info">
        <h4 className="card-title">{title}</h4>
        <p className="card-year">{year}</p>
      </div>
    </div>
  );
}
