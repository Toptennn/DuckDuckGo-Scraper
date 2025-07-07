import { useState } from 'react';

export default function SearchForm({ onSubmit, loading }) {
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

  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  const clearForm = () => {
    setForm({
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
  };

  return (
    <div className="card p-6 mb-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Search Parameters
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Enter your search criteria to find relevant results from DuckDuckGo
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Search Fields */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="form-group">
            <label className="form-label">
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                </svg>
                Normal Query
              </span>
            </label>
            <input
              name="normal_query"
              placeholder="Enter your search terms..."
              value={form.normal_query}
              onChange={handleChange}
              className="input-field"
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
                Exact Phrase
              </span>
            </label>
            <input
              name="exact_phrase"
              placeholder="Exact phrase to search for..."
              value={form.exact_phrase}
              onChange={handleChange}
              className="input-field"
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Semantic Query
              </span>
            </label>
            <input
              name="semantic_query"
              placeholder="Semantic search terms..."
              value={form.semantic_query}
              onChange={handleChange}
              className="input-field"
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                Include Terms
              </span>
            </label>
            <input
              name="include_terms"
              placeholder="Terms to include (comma-separated)..."
              value={form.include_terms}
              onChange={handleChange}
              className="input-field"
            />
          </div>
        </div>

        {/* Advanced Search Toggle */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-2 text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium transition-colors"
          >
            <svg
              className={`w-4 h-4 transform transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            {showAdvanced ? 'Hide Advanced Options' : 'Show Advanced Options'}
          </button>

          <div className="flex items-center gap-2">
            <label className="form-label mb-0">Max Pages:</label>
            <input
              name="max_pages"
              type="number"
              min="1"
              max="100"
              value={form.max_pages}
              onChange={handleChange}
              className="input-field w-20"
            />
          </div>
        </div>

        {/* Advanced Search Fields */}
        {showAdvanced && (
          <div className="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-700 fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="form-group">
                <label className="form-label">Exclude Terms</label>
                <input
                  name="exclude_terms"
                  placeholder="Terms to exclude (comma-separated)..."
                  value={form.exclude_terms}
                  onChange={handleChange}
                  className="input-field"
                />
              </div>

              <div className="form-group">
                <label className="form-label">File Type</label>
                <input
                  name="filetype"
                  placeholder="e.g., pdf, doc, txt..."
                  value={form.filetype}
                  onChange={handleChange}
                  className="input-field"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Site Include</label>
                <input
                  name="site_include"
                  placeholder="e.g., reddit.com, github.com..."
                  value={form.site_include}
                  onChange={handleChange}
                  className="input-field"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Site Exclude</label>
                <input
                  name="site_exclude"
                  placeholder="e.g., pinterest.com..."
                  value={form.site_exclude}
                  onChange={handleChange}
                  className="input-field"
                />
              </div>

              <div className="form-group">
                <label className="form-label">In Title</label>
                <input
                  name="intitle"
                  placeholder="Text that must appear in title..."
                  value={form.intitle}
                  onChange={handleChange}
                  className="input-field"
                />
              </div>

              <div className="form-group">
                <label className="form-label">In URL</label>
                <input
                  name="inurl"
                  placeholder="Text that must appear in URL..."
                  value={form.inurl}
                  onChange={handleChange}
                  className="input-field"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Start Date</label>
                <input
                  name="start_date"
                  type="date"
                  value={form.start_date}
                  onChange={handleChange}
                  className="input-field"
                />
              </div>

              <div className="form-group">
                <label className="form-label">End Date</label>
                <input
                  name="end_date"
                  type="date"
                  value={form.end_date}
                  onChange={handleChange}
                  className="input-field"
                />
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 pt-6">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex-1 flex items-center justify-center gap-2 min-h-[48px]"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Searching...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                </svg>
                Search DuckDuckGo
              </>
            )}
          </button>

          <button
            type="button"
            onClick={clearForm}
            className="btn-secondary flex items-center justify-center gap-2 min-h-[48px]"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            Clear Form
          </button>
        </div>
      </form>
    </div>
  );
}
