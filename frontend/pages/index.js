import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [form, setForm] = useState({
    normal_query: '',
    exact_phrase: '',
    semantic_query: '',
    include_terms: '',
    exclude_terms: '',
    filetype: '',
    site_include: '',
    site_exclude: '',
    intitle: '',
    inurl: '',
    start_date: '',
    end_date: '',
    max_pages: 20
  });

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/search', form);
      setResults(res.data.results);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1>DuckDuckGo Scraper</h1>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '0.5rem', maxWidth: '600px' }}>
        <input name="normal_query" placeholder="Normal query" value={form.normal_query} onChange={handleChange} />
        <input name="exact_phrase" placeholder="Exact phrase" value={form.exact_phrase} onChange={handleChange} />
        <input name="semantic_query" placeholder="Semantic query" value={form.semantic_query} onChange={handleChange} />
        <input name="include_terms" placeholder="Include terms (+)" value={form.include_terms} onChange={handleChange} />
        <input name="exclude_terms" placeholder="Exclude terms (-)" value={form.exclude_terms} onChange={handleChange} />
        <input name="filetype" placeholder="File type" value={form.filetype} onChange={handleChange} />
        <input name="site_include" placeholder="Site include" value={form.site_include} onChange={handleChange} />
        <input name="site_exclude" placeholder="Site exclude" value={form.site_exclude} onChange={handleChange} />
        <input name="intitle" placeholder="In title" value={form.intitle} onChange={handleChange} />
        <input name="inurl" placeholder="In URL" value={form.inurl} onChange={handleChange} />
        <input name="start_date" placeholder="Start date YYYY-MM-DD" value={form.start_date} onChange={handleChange} />
        <input name="end_date" placeholder="End date YYYY-MM-DD" value={form.end_date} onChange={handleChange} />
        <input name="max_pages" type="number" placeholder="Max pages" value={form.max_pages} onChange={handleChange} />
        <button type="submit">Search</button>
      </form>
      {loading && <p>Loading...</p>}
      <ul>
        {results.map((r, idx) => (
          <li key={idx}>
            <a href={r.href} target="_blank" rel="noreferrer">{r.title}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}
