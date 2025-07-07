export default function SearchResults({ results, searchInfo, loading, error }) {
  if (loading) {
    return (
      <div className="card p-8 text-center">
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-primary-200 dark:border-primary-800 rounded-full"></div>
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <div className="space-y-2">
            <p className="text-lg font-medium text-gray-900 dark:text-white">
              Searching DuckDuckGo...
            </p>
            <p className="text-gray-600 dark:text-gray-400">
              This may take a few moments while we gather results
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-6 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20">
        <div className="flex items-center gap-3">
          <svg className="w-8 h-8 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <div>
            <h3 className="text-lg font-semibold text-red-800 dark:text-red-200">
              Search Error
            </h3>
            <p className="text-red-700 dark:text-red-300">
              {error}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Search Information */}
      {searchInfo && (
        <div className="stats-card">
          <h3 className="text-lg font-semibold text-primary-800 dark:text-primary-200 mb-3">
            Search Results
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-primary-700 dark:text-primary-300">
                {searchInfo.total_results}
              </p>
              <p className="text-sm text-primary-600 dark:text-primary-400">
                Results Found
              </p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-primary-700 dark:text-primary-300">
                {searchInfo.pages_retrieved}
              </p>
              <p className="text-sm text-primary-600 dark:text-primary-400">
                Pages Scraped
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-primary-700 dark:text-primary-300 break-words">
                {searchInfo.query || 'No query specified'}
              </p>
              <p className="text-sm text-primary-600 dark:text-primary-400">
                Search Query
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Results List */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <svg className="w-5 h-5 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
          </svg>
          Search Results ({results.length})
        </h3>

        <div className="grid gap-4">
          {results.map((result, index) => (
            <div key={result.href || index} className="search-result-card fade-in">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                  <span className="text-primary-600 dark:text-primary-400 font-medium">
                    {index + 1}
                  </span>
                </div>
                
                <div className="flex-1 min-w-0">
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    <a
                      href={result.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors duration-200 group"
                    >
                      {result.title || 'Untitled'}
                      <svg className="w-4 h-4 inline-block ml-1 opacity-0 group-hover:opacity-100 transition-opacity" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </a>
                  </h4>
                  
                  {result.description && (
                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-3 leading-relaxed">
                      {result.description}
                    </p>
                  )}
                  
                  <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-500">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4.083 9h1.946c.089-1.546.383-2.97.837-4.118A6.004 6.004 0 004.083 9zM10 2a8 8 0 100 16 8 8 0 000-16zm0 2c-.076 0-.232.032-.465.262-.238.234-.497.623-.737 1.182-.389.907-.673 2.142-.766 3.556h3.936c-.093-1.414-.377-2.649-.766-3.556-.24-.559-.499-.948-.737-1.182C10.232 4.032 10.076 4 10 4zm3.971 5c-.089-1.546-.383-2.97-.837-4.118A6.004 6.004 0 0115.917 9h-1.946zm-2.003 2H8.032c.093 1.414.377 2.649.766 3.556.24.559.499.948.737 1.182.233.23.389.262.465.262.076 0 .232-.032.465-.262.238-.234.497-.623.737-1.182.389-.907.673-2.142.766-3.556zm1.166 4.118c.454-1.147.748-2.572.837-4.118h1.946a6.004 6.004 0 01-2.783 4.118zm-6.268 0C6.412 13.97 6.118 12.546 6.03 11H4.083a6.004 6.004 0 002.783 4.118z" clipRule="evenodd" />
                    </svg>
                    <span className="truncate">
                      {result.href ? new URL(result.href).hostname : 'No URL'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {results.length > 0 && (
          <div className="text-center pt-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Showing {results.length} results
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
