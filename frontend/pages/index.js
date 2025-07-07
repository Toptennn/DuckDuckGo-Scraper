import { useState } from 'react';
import axios from 'axios';
import Head from 'next/head';
import ThemeToggle from '../components/ThemeToggle';
import SearchForm from '../components/SearchForm';
import SearchResults from '../components/SearchResults';

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [searchInfo, setSearchInfo] = useState(null);

  const handleSearch = async (formData) => {
    setLoading(true);
    setError(null);
    setResults([]);
    setSearchInfo(null);
    
    try {
      const res = await axios.post('http://127.0.0.1:8000/search', formData);
      setResults(res.data.results);
      setSearchInfo({
        query: res.data.query,
        pages_retrieved: res.data.pages_retrieved,
        total_results: res.data.results.length
      });
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'An error occurred while searching');
    }
    setLoading(false);
  };

  return (
    <>
      <Head>
        <title>DuckDuckGo Scraper - Advanced Search Tool</title>
        <meta name="description" content="Advanced DuckDuckGo search tool with powerful filtering options" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                    DuckDuckGo Scraper
                  </h1>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Advanced Search Tool
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="hidden sm:flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>API Connected</span>
                </div>
                <ThemeToggle />
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Welcome Section */}
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Powerful Search at Your Fingertips
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Use advanced search parameters to find exactly what you're looking for. 
              Our tool leverages DuckDuckGo's search capabilities with enhanced filtering options.
            </p>
          </div>

          {/* Search Form */}
          <SearchForm onSubmit={handleSearch} loading={loading} />

          {/* Search Results */}
          <SearchResults
            results={results}
            searchInfo={searchInfo}
            loading={loading}
            error={error}
          />
        </main>

        {/* Footer */}
        <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center">
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Built with Next.js, FastAPI, and Tailwind CSS
              </p>
              <div className="flex justify-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-gray-600 dark:text-gray-400">Frontend: Next.js</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-gray-600 dark:text-gray-400">Backend: FastAPI</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span className="text-gray-600 dark:text-gray-400">Scraping: Selenium</span>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
