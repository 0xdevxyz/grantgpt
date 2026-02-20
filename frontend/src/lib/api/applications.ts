import { apiClient } from '../api-client';

export interface ApplicationCreate {
  grant_id: string;
  project_title: string;
  project_description: string;
  project_goals?: string[];
  project_innovation?: string;
  timeline_months: number;
  total_budget: number;
  requested_funding: number;
  own_contribution: number;
  team_info?: Record<string, any>;
  target_audience?: string;
  market_analysis?: string;
}

export interface Application {
  id: string;
  grant_external_id: string;
  project_title: string;
  project_description: string;
  status: string;
  completion_percentage: number;
  total_budget: number;
  requested_funding: number;
  created_at: string;
  updated_at: string;
}

export interface ApplicationDetail extends Application {
  project_goals?: string[];
  project_innovation?: string;
  timeline_months: number;
  own_contribution: number;
  team_info?: Record<string, any>;
  generated_content?: Record<string, string>;
  compliance_score?: number;
}

export const applicationsApi = {
  create: async (data: ApplicationCreate): Promise<Application> => {
    const response = await apiClient.post('/api/v1/applications', data);
    return response.data;
  },

  list: async (params?: {
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<Application[]> => {
    const { data } = await apiClient.get('/api/v1/applications', { params });
    return data;
  },

  getDetails: async (applicationId: string): Promise<ApplicationDetail> => {
    const { data } = await apiClient.get(`/api/v1/applications/${applicationId}`);
    return data;
  },

  update: async (
    applicationId: string,
    updates: Partial<ApplicationCreate>
  ): Promise<Application> => {
    const { data } = await apiClient.patch(
      `/api/v1/applications/${applicationId}`,
      updates
    );
    return data;
  },

  delete: async (applicationId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/applications/${applicationId}`);
  },

  regenerate: async (
    applicationId: string,
    section?: string
  ): Promise<{ message: string }> => {
    const { data } = await apiClient.post(
      `/api/v1/applications/${applicationId}/generate`,
      { section }
    );
    return data;
  },

  submit: async (applicationId: string): Promise<{
    message: string;
    tracking_number: string;
  }> => {
    const { data } = await apiClient.post(
      `/api/v1/applications/${applicationId}/submit`
    );
    return data;
  },
};
