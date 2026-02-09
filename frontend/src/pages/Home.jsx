import { useEffect, useState } from "react";
import  API  from "../api";
import { Link } from "react-router-dom";
import "./Home.css";

export default function Home() {
  const [movies, setMovies] = useState([]);
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const movieRes = await API.get("/items/popular/movies");
        const bookRes = await API.get("/items/popular/books");

        setMovies(movieRes.data);
        setBooks(bookRes.data);
      } catch (err) {
        console.log(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) return <p className="loading-text">Yükleniyor...</p>;

  return (
    <div className="home-wrapper">

      <h1 className="page-title"> Popüler Filmler</h1>

      <div className="scroll-row">
        {movies.map((item) => (
          <Link to={`/item/${item.id}`} key={item.id} className="media-card">
            <img src={item.poster_url} className="media-img" />
            <div className="media-info">
              <h4>{item.title}</h4>
              <span>{item.year}</span>
            </div>
          </Link>
        ))}
      </div>

      <h1 className="page-title" style={{ marginTop: 50 }}>Popüler Kitaplar</h1>

      <div className="scroll-row">
        {books.map((item) => (
          <Link to={`/item/${item.id}`} key={item.id} className="media-card">
            <img src={item.poster_url} className="media-img" />
            <div className="media-info">
              <h4>{item.title}</h4>
              <span>{item.year}</span>
            </div>
          </Link>
        ))}
      </div>

    </div>
  );
}
