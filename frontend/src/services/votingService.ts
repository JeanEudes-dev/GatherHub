import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Apply interceptors (similar to other services)
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry && localStorage.getItem('refreshToken')) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, { refresh: refreshToken });
        const { access, refresh } = response.data;
        localStorage.setItem('accessToken', access);
        if (refresh) localStorage.setItem('refreshToken', refresh);

        axios.defaults.headers.common['Authorization'] = 'Bearer ' + access;
        originalRequest.headers['Authorization'] = 'Bearer ' + access;
        return apiClient(originalRequest);
      } catch (refreshError) {
        console.error("Token refresh failed in votingService:", refreshError);
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

// Voting Types (should be in a central types/index.ts)
export interface VoteOption {
  id?: number; // Optional on create, present on retrieve
  text: string;
  vote_count?: number; // On retrieve
  percentage?: number; // On retrieve results
}

export interface VoteCreator {
  id: number;
  username: string;
}

export interface VoteEventInfo {
  id: number;
  title: string;
  date?: string;
}

export interface UserVoteInfo {
    option_id: number; // ID of the option voted for
    voted_at: string;
}

export interface Vote {
  id: number;
  title: string;
  description: string;
  status: 'active' | 'ended';
  event: VoteEventInfo; // Can be just event ID on create
  creator: VoteCreator;
  options: VoteOption[];
  total_votes: number;
  ends_at: string | null; // ISO 8601 datetime string or null
  multiple_choice: boolean;
  created_at: string;
  updated_at?: string; // Not in API_REFERENCE.md but common
  user_voted?: boolean; // If user has voted (on retrieve details)
  user_vote?: UserVoteInfo | null; // Details of user's vote (on retrieve details)
}

export interface PaginatedVotesResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Vote[];
}

export interface CreateVoteData {
  title: string;
  description: string;
  event: number; // Event ID
  options: Array<{ text: string }>; // Array of option texts
  ends_at?: string | null; // ISO 8601 datetime string
  multiple_choice?: boolean;
}

export interface CastVoteData {
  options: number[]; // Array of selected option IDs
}

export interface VoteResults extends Pick<Vote, 'id' | 'title' | 'status' | 'total_votes' | 'ends_at'> {
    results: VoteOption[]; // Options with vote_count and percentage
    winner?: VoteOption | null; // Winning option if applicable
}


// API Functions for Voting
export const listVotes = async (params?: Record<string, any>): Promise<PaginatedVotesResponse> => {
  const response = await apiClient.get('/voting/', { params });
  return response.data;
};

export const createVote = async (voteData: CreateVoteData): Promise<Vote> => {
  const response = await apiClient.post('/voting/', voteData);
  return response.data;
};

export const getVoteDetails = async (voteId: number): Promise<Vote> => {
  const response = await apiClient.get(`/voting/${voteId}/`);
  return response.data;
};

export const castVote = async (voteId: number, optionsData: CastVoteData): Promise<{ message: string; vote: Partial<Vote> }> => {
  const response = await apiClient.post(`/voting/${voteId}/vote/`, optionsData);
  return response.data;
};

export const getVoteResults = async (voteId: number): Promise<VoteResults> => {
  const response = await apiClient.get(`/voting/${voteId}/results/`);
  return response.data;
};

// Note: Update/Delete for Votes are not specified in API_REFERENCE.md.
// If needed, they would be added here.
// export const updateVote = async (voteId: number, voteData: Partial<CreateVoteData>): Promise<Vote> => { ... };
// export const deleteVote = async (voteId: number): Promise<void> => { ... };
