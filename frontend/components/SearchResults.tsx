import { SearchResultsProps } from '../types';
import ResultsTable from './ResultsTable';

const SearchResults: React.FC<SearchResultsProps> = ({ results, searchInfo, loading, error }) => {
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
            Search Summary
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

      {/* Results Table */}
      <ResultsTable results={results} loading={false} />
    </div>
  );
};

export default SearchResults;
