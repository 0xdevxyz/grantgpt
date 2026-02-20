import { apiClient } from '../api-client';

export interface GrantSearchParams {
  company_size?: number;
  industry?: string;
  project_description?: string;
  budget?: number;
  location?: string;
}

export interface Grant {
  id: string;
  name: string;
  type: string;
  category: string;
  max_funding: number;
  deadline: string;
  description: string;
  eligibility: string[];
  success_rate?: number;
  match_score?: number;
}

export interface GrantDetail extends Grant {
  requirements: string[];
  application_process: string;
  duration: string;
  contact: {
    website: string;
    email: string;
    phone: string;
    funder: string;
  };
}

export const grantsApi = {
  search: async (params: GrantSearchParams): Promise<Grant[]> => {
    const { data } = await apiClient.post('/api/v1/grants/search', params);
    return data;
  },

  list: async (params?: {
    type?: string;
    category?: string;
    skip?: number;
    limit?: number;
  }): Promise<Grant[]> => {
    const { data } = await apiClient.get('/api/v1/grants', { params });
    return data;
  },

  getDetails: async (grantId: string): Promise<GrantDetail> => {
    const { data } = await apiClient.get(`/api/v1/grants/${grantId}`);
    return data;
  },
};
