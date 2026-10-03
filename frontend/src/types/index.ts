
export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

export interface ApiResponse<T> {
  data: T;
  pagination?: PaginationMeta;
}

export type WawqiCategory = 'Excellent' | 'Good' | 'Poor' | 'Very Poor' | 'Unsuitable' | 'UNAVAILABLE';

export interface OverviewStats {
  total_samples: number;
  eligible_samples: number;
  unavailable_samples: number;
  state_count: number;
  district_count: number;
  location_count: number;
  min_wqi: number;
  max_wqi: number;
  mean_wqi: number;
  median_wqi: number;
  p25_wqi: number;
  p75_wqi: number;
  p90_wqi: number;
  p95_wqi: number;
  p99_wqi: number;
}
