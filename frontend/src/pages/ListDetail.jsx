import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import API from "../api";

export default function ListDetail() {
  const { id } = useParams();
  const [list, setList] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await API.get(`/lists/${id}`);
        setList(res.data);
      } catch (err) {
        console.log(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) return <p>Yükleniyor...</p>;
  if (!list) return <p>Liste bulunamadı.</p>;

  return (
    <div className="list-detail-page">
      <h2>{list.name}</h2>
      <p>{list.description}</p>

      <div className="list-items-grid">
        {list.items.map(item => (
          <div key={item.id} className="list-item-card">
            <img src={item.poster_url} />
            <p>{item.title}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
