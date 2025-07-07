// Types for search functionality
export interface SearchFormData {
  normal_query: string;
  exact_phrase: string;
  semantic_query: string;
  include_terms: string;
  exclude_terms: string;
  filetype: string;
  site_include: string;
  site_exclude: string;
  intitle: string;
  inurl: string;
  start_date: string;
  end_date: string;
  max_pages: number;
}

export interface SearchResult {
  title: string;
  url: string;
  description?: string;
  date?: string;
  post_date?: string;
  published_date?: string;
  [key: string]: any;
}

export interface SearchResponse {
  query: string;
  pages_retrieved: number;
  results: SearchResult[];
}

export interface SearchInfo {
  query: string;
  pages_retrieved: number;
  total_results: number;
}

// Props interfaces
export interface SearchFormProps {
  onSubmit: (data: SearchFormData) => void;
  loading: boolean;
}

export interface SearchResultsProps {
  results: SearchResult[];
  searchInfo: SearchInfo | null;
  loading: boolean;
  error: string | null;
}

export interface ResultsTableProps {
  results: SearchResult[];
  loading: boolean;
}

// Filter types
export interface TableFilters {
  title_filter: string;
  date_filter: string;
  url_filter: string;
}
