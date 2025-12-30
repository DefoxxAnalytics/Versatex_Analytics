/**
 * API client for Django backend with typed interfaces
 */
import axios, { AxiosResponse } from 'axios';

// =====================
// Type Definitions
// =====================

// Base types
export type UserRole = 'admin' | 'manager' | 'viewer';
export type UploadStatus = 'processing' | 'completed' | 'failed' | 'partial';

// Organization
export interface Organization {
  id: number;
  name: string;
  slug: string;
  description: string;
  is_active: boolean;
  created_at: string;
}

// User Profile
export interface UserProfile {
  id: number;
  organization: number;
  organization_name: string;
  role: UserRole;
  phone: string;
  department: string;
  is_active: boolean;
  created_at: string;
}

// User
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile: UserProfile;
}

// Authentication
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
  organization: number;
  role?: UserRole;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
  message: string;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
  new_password_confirm: string;
}

// Supplier
export interface Supplier {
  id: number;
  name: string;
  code: string;
  contact_email: string;
  contact_phone: string;
  address: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  transaction_count?: number;
  total_spend?: number;
}

export interface SupplierCreateRequest {
  name: string;
  code?: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  is_active?: boolean;
}

export interface SupplierUpdateRequest extends Partial<SupplierCreateRequest> {}

// Category
export interface Category {
  id: number;
  name: string;
  parent: number | null;
  parent_name: string | null;
  description: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  transaction_count?: number;
  total_spend?: number;
}

export interface CategoryCreateRequest {
  name: string;
  parent?: number | null;
  description?: string;
  is_active?: boolean;
}

export interface CategoryUpdateRequest extends Partial<CategoryCreateRequest> {}

// Transaction
export interface Transaction {
  id: number;
  supplier: number;
  supplier_name: string;
  category: number;
  category_name: string;
  amount: string;
  date: string;
  description: string;
  subcategory: string;
  location: string;
  fiscal_year: number | null;
  spend_band: string;
  payment_method: string;
  invoice_number: string;
  upload_batch: string;
  uploaded_by: number;
  uploaded_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreateRequest {
  supplier?: number;
  supplier_name?: string;
  category?: number;
  category_name?: string;
  amount: number | string;
  date: string;
  description?: string;
  subcategory?: string;
  location?: string;
  fiscal_year?: number;
  spend_band?: string;
  payment_method?: string;
  invoice_number?: string;
}

export interface TransactionUpdateRequest extends Partial<TransactionCreateRequest> {}

export interface BulkDeleteRequest {
  ids: number[];
}

export interface BulkDeleteResponse {
  deleted: number;
  message: string;
}

// Data Upload
export interface DataUpload {
  id: number;
  file_name: string;
  file_size: number;
  batch_id: string;
  total_rows: number;
  successful_rows: number;
  failed_rows: number;
  duplicate_rows: number;
  status: UploadStatus;
  error_log: UploadError[];
  uploaded_by: number;
  uploaded_by_name: string;
  created_at: string;
  completed_at: string | null;
}

export interface UploadError {
  row: number;
  error: string;
  data: Record<string, unknown>;
}

export interface CSVUploadResponse {
  upload: DataUpload;
  message: string;
}

// Analytics types
export interface OverviewStats {
  total_spend: number;
  transaction_count: number;
  supplier_count: number;
  category_count: number;
  avg_transaction: number;
}

export interface SpendByCategory {
  category: string;
  amount: number;
  count: number;
}

export interface SpendBySupplier {
  supplier: string;
  amount: number;
  count: number;
}

export interface MonthlyTrend {
  month: string;
  amount: number;
  count: number;
}

export interface ParetoItem {
  supplier: string;
  amount: number;
  cumulative_percentage: number;
}

export interface TailSpendSupplier {
  supplier: string;
  supplier_id: number;
  amount: number;
  transaction_count: number;
}

export interface TailSpendAnalysis {
  tail_suppliers: TailSpendSupplier[];
  tail_count: number;
  tail_spend: number;
  tail_percentage: number;
}

export interface StratificationCategory {
  category: string;
  spend: number;
  supplier_count: number;
  transaction_count: number;
}

export interface SpendStratification {
  strategic: StratificationCategory[];
  leverage: StratificationCategory[];
  bottleneck: StratificationCategory[];
  tactical: StratificationCategory[];
}

export interface SeasonalityData {
  month: string;
  average_spend: number;
  occurrences: number;
}

export interface YearOverYearData {
  year: number;
  total_spend: number;
  transaction_count: number;
  avg_transaction: number;
  growth_percentage?: number;
}

export interface ConsolidationSupplier {
  name: string;
  spend: number;
}

export interface ConsolidationOpportunity {
  category: string;
  supplier_count: number;
  total_spend: number;
  suppliers: ConsolidationSupplier[];
  potential_savings: number;
}

// Paginated response
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Query parameters
export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface SupplierQueryParams extends PaginationParams {
  search?: string;
  is_active?: boolean;
  ordering?: string;
}

export interface CategoryQueryParams extends PaginationParams {
  search?: string;
  is_active?: boolean;
  parent?: number | null;
  ordering?: string;
}

export interface TransactionQueryParams extends PaginationParams {
  search?: string;
  supplier?: number;
  category?: number;
  start_date?: string;
  end_date?: string;
  fiscal_year?: number;
  ordering?: string;
}

export interface ExportParams {
  start_date?: string;
  end_date?: string;
  supplier?: number;
  category?: number;
}

// =====================
// API Configuration
// =====================

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return axios(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// =====================
// API Functions
// =====================

// Authentication API
export const authAPI = {
  register: (data: RegisterRequest): Promise<AxiosResponse<AuthResponse>> =>
    api.post('/auth/register/', data),

  login: (data: LoginRequest): Promise<AxiosResponse<AuthResponse>> =>
    api.post('/auth/login/', data),

  logout: (refreshToken: string): Promise<AxiosResponse<{ message: string }>> =>
    api.post('/auth/logout/', { refresh_token: refreshToken }),

  getCurrentUser: (): Promise<AxiosResponse<User>> =>
    api.get('/auth/user/'),

  changePassword: (data: ChangePasswordRequest): Promise<AxiosResponse<{ message: string }>> =>
    api.post('/auth/change-password/', data),
};

// Procurement API
export const procurementAPI = {
  // Suppliers
  getSuppliers: (params?: SupplierQueryParams): Promise<AxiosResponse<PaginatedResponse<Supplier>>> =>
    api.get('/procurement/suppliers/', { params }),

  getSupplier: (id: number): Promise<AxiosResponse<Supplier>> =>
    api.get(`/procurement/suppliers/${id}/`),

  createSupplier: (data: SupplierCreateRequest): Promise<AxiosResponse<Supplier>> =>
    api.post('/procurement/suppliers/', data),

  updateSupplier: (id: number, data: SupplierUpdateRequest): Promise<AxiosResponse<Supplier>> =>
    api.patch(`/procurement/suppliers/${id}/`, data),

  deleteSupplier: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/procurement/suppliers/${id}/`),

  // Categories
  getCategories: (params?: CategoryQueryParams): Promise<AxiosResponse<PaginatedResponse<Category>>> =>
    api.get('/procurement/categories/', { params }),

  getCategory: (id: number): Promise<AxiosResponse<Category>> =>
    api.get(`/procurement/categories/${id}/`),

  createCategory: (data: CategoryCreateRequest): Promise<AxiosResponse<Category>> =>
    api.post('/procurement/categories/', data),

  updateCategory: (id: number, data: CategoryUpdateRequest): Promise<AxiosResponse<Category>> =>
    api.patch(`/procurement/categories/${id}/`, data),

  deleteCategory: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/procurement/categories/${id}/`),

  // Transactions
  getTransactions: (params?: TransactionQueryParams): Promise<AxiosResponse<PaginatedResponse<Transaction>>> =>
    api.get('/procurement/transactions/', { params }),

  getTransaction: (id: number): Promise<AxiosResponse<Transaction>> =>
    api.get(`/procurement/transactions/${id}/`),

  createTransaction: (data: TransactionCreateRequest): Promise<AxiosResponse<Transaction>> =>
    api.post('/procurement/transactions/', data),

  updateTransaction: (id: number, data: TransactionUpdateRequest): Promise<AxiosResponse<Transaction>> =>
    api.patch(`/procurement/transactions/${id}/`, data),

  deleteTransaction: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/procurement/transactions/${id}/`),

  uploadCSV: (file: File, skipDuplicates: boolean = true): Promise<AxiosResponse<CSVUploadResponse>> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('skip_duplicates', String(skipDuplicates));
    return api.post('/procurement/transactions/upload_csv/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  bulkDelete: (ids: number[]): Promise<AxiosResponse<BulkDeleteResponse>> =>
    api.post('/procurement/transactions/bulk_delete/', { ids }),

  exportCSV: (params?: ExportParams): Promise<AxiosResponse<Blob>> =>
    api.get('/procurement/transactions/export/', {
      params,
      responseType: 'blob',
    }),

  // Uploads
  getUploads: (params?: PaginationParams): Promise<AxiosResponse<PaginatedResponse<DataUpload>>> =>
    api.get('/procurement/uploads/', { params }),
};

// Analytics API
export const analyticsAPI = {
  getOverview: (): Promise<AxiosResponse<OverviewStats>> =>
    api.get('/analytics/overview/'),

  getSpendByCategory: (): Promise<AxiosResponse<SpendByCategory[]>> =>
    api.get('/analytics/spend-by-category/'),

  getSpendBySupplier: (): Promise<AxiosResponse<SpendBySupplier[]>> =>
    api.get('/analytics/spend-by-supplier/'),

  getMonthlyTrend: (months: number = 12): Promise<AxiosResponse<MonthlyTrend[]>> =>
    api.get('/analytics/monthly-trend/', { params: { months } }),

  getParetoAnalysis: (): Promise<AxiosResponse<ParetoItem[]>> =>
    api.get('/analytics/pareto/'),

  getTailSpend: (threshold: number = 20): Promise<AxiosResponse<TailSpendAnalysis>> =>
    api.get('/analytics/tail-spend/', { params: { threshold } }),

  getStratification: (): Promise<AxiosResponse<SpendStratification>> =>
    api.get('/analytics/stratification/'),

  getSeasonality: (): Promise<AxiosResponse<SeasonalityData[]>> =>
    api.get('/analytics/seasonality/'),

  getYearOverYear: (): Promise<AxiosResponse<YearOverYearData[]>> =>
    api.get('/analytics/year-over-year/'),

  getConsolidation: (): Promise<AxiosResponse<ConsolidationOpportunity[]>> =>
    api.get('/analytics/consolidation/'),
};

export default api;
