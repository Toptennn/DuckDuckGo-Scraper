import { useState, useMemo } from 'react';
import { format } from 'date-fns';
import * as XLSX from 'xlsx';
import { ResultsTableProps, TableFilters, SearchResult } from '../types';

const ResultsTable: React.FC<ResultsTableProps> = ({ results, loading }) => {
  const [filters, setFilters] = useState<TableFilters>({
    title_filter: '',
    date_filter: '',
    url_filter: '',
  });

  const [sortField, setSortField] = useState<keyof SearchResult>('title');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // Filter and sort results
  const filteredResults = useMemo(() => {
    let filtered = results.filter(result => {
      const titleMatch = result.title?.toLowerCase().includes(filters.title_filter.toLowerCase()) || !filters.title_filter;
      const urlMatch = result.url?.toLowerCase().includes(filters.url_filter.toLowerCase()) || !filters.url_filter;
      
      let dateMatch = true;
      if (filters.date_filter) {
        const resultDate = result.date || result.post_date || result.published_date;
        if (resultDate) {
          dateMatch = resultDate.toLowerCase().includes(filters.date_filter.toLowerCase());
        }
      }
      
      return titleMatch && urlMatch && dateMatch;
    });

    // Sort results
    filtered.sort((a, b) => {
      const aValue = a[sortField] || '';
      const bValue = b[sortField] || '';
      
      const comparison = aValue.toString().localeCompare(bValue.toString());
      return sortDirection === 'asc' ? comparison : -comparison;
    });

    return filtered;
  }, [results, filters, sortField, sortDirection]);

  const handleSort = (field: keyof SearchResult): void => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const exportToCSV = (): void => {
    const csvData = filteredResults.map(result => ({
      Title: result.title || '',
      URL: result.url || '',
      'Post Date': result.date || result.post_date || result.published_date || '',
    }));

    const ws = XLSX.utils.json_to_sheet(csvData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Search Results');
    XLSX.writeFile(wb, `search_results_${format(new Date(), 'yyyy-MM-dd_HH-mm-ss')}.csv`);
  };

  const exportToExcel = (): void => {
    const excelData = filteredResults.map(result => ({
      Title: result.title || '',
      URL: result.url || '',
      'Post Date': result.date || result.post_date || result.published_date || '',
    }));

    const ws = XLSX.utils.json_to_sheet(excelData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Search Results');
    XLSX.writeFile(wb, `search_results_${format(new Date(), 'yyyy-MM-dd_HH-mm-ss')}.xlsx`);
  };

  const formatDate = (dateString: string): string => {
    if (!dateString) return '';
    try {
      return format(new Date(dateString), 'MMM dd, yyyy');
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <div className="card p-8 text-center">
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-primary-200 dark:border-primary-800 rounded-full"></div>
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <p className="text-lg font-medium text-gray-900 dark:text-white">
            Loading results...
          </p>
        </div>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header with Export Buttons */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            Search Results ({filteredResults.length})
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {filteredResults.length !== results.length && 
              `Filtered from ${results.length} total results`
            }
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={exportToCSV}
            className="btn-secondary flex items-center gap-2 text-sm"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            Export CSV
          </button>
          <button
            onClick={exportToExcel}
            className="btn-secondary flex items-center gap-2 text-sm"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            Export Excel
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <h4 className="font-medium text-gray-900 dark:text-white mb-3">Filters</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Title Filter
            </label>
            <input
              type="text"
              placeholder="Filter by title..."
              value={filters.title_filter}
              onChange={(e) => setFilters(prev => ({ ...prev, title_filter: e.target.value }))}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              URL Filter
            </label>
            <input
              type="text"
              placeholder="Filter by URL..."
              value={filters.url_filter}
              onChange={(e) => setFilters(prev => ({ ...prev, url_filter: e.target.value }))}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Date Filter
            </label>
            <input
              type="text"
              placeholder="Filter by date..."
              value={filters.date_filter}
              onChange={(e) => setFilters(prev => ({ ...prev, date_filter: e.target.value }))}
              className="input-field"
            />
          </div>
        </div>
        
        {(filters.title_filter || filters.url_filter || filters.date_filter) && (
          <div className="mt-3 flex justify-end">
            <button
              onClick={() => setFilters({ title_filter: '', url_filter: '', date_filter: '' })}
              className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300"
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>

      {/* Results Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                  onClick={() => handleSort('title')}
                >
                  <div className="flex items-center gap-2">
                    Title
                    {sortField === 'title' && (
                      <svg className={`w-4 h-4 ${sortDirection === 'asc' ? '' : 'rotate-180'}`} fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                  onClick={() => handleSort('url')}
                >
                  <div className="flex items-center gap-2">
                    URL
                    {sortField === 'url' && (
                      <svg className={`w-4 h-4 ${sortDirection === 'asc' ? '' : 'rotate-180'}`} fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                  onClick={() => handleSort('date')}
                >
                  <div className="flex items-center gap-2">
                    Post Date
                    {sortField === 'date' && (
                      <svg className={`w-4 h-4 ${sortDirection === 'asc' ? '' : 'rotate-180'}`} fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredResults.map((result, index) => (
                <tr key={result.url || index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4">
                    <div className="max-w-xs">
                      <div className="text-sm font-medium text-gray-900 dark:text-white line-clamp-2">
                        {result.title || 'Untitled'}
                      </div>
                      {result.description && (
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                          {result.description}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="max-w-xs">
                      <div className="text-sm text-gray-900 dark:text-white truncate">
                        {result.url ? new URL(result.url).hostname : 'No URL'}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {result.url}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {formatDate(result.date || result.post_date || result.published_date || '')}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <a
                      href={result.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 flex items-center gap-1"
                    >
                      Visit
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ResultsTable;
