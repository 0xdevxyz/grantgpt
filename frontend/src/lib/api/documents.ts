import { apiClient } from '../api-client';

export interface Document {
  id: string;
  application_id: string;
  document_type: string;
  format: string;
  filename: string;
  file_size?: number;
  generated_by_ai: boolean;
  version: number;
  created_at: string;
  download_url: string;
}

export const documentsApi = {
  generate: async (
    applicationId: string,
    format: 'pdf' | 'docx' = 'pdf'
  ): Promise<Document> => {
    const { data } = await apiClient.post(
      `/api/v1/documents/applications/${applicationId}/generate`,
      { format }
    );
    return data;
  },

  getInfo: async (documentId: string): Promise<Document> => {
    const { data } = await apiClient.get(`/api/v1/documents/${documentId}`);
    return data;
  },

  download: async (documentId: string): Promise<Blob> => {
    const { data } = await apiClient.get(
      `/api/v1/documents/${documentId}/download`,
      { responseType: 'blob' }
    );
    return data;
  },

  list: async (applicationId: string): Promise<Document[]> => {
    const { data } = await apiClient.get(
      `/api/v1/documents/applications/${applicationId}/documents`
    );
    return data;
  },

  delete: async (documentId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/documents/${documentId}`);
  },
};
