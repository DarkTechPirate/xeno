/**
 * API client and utilities
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { Dataset, ValidationResult, ValidationError, Correction, DemoDataset, ChunkInfo } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // ============ Dataset Methods ============

  async uploadDataset(file: File, name?: string): Promise<Dataset> {
    const formData = new FormData();
    formData.append('file', file);
    if (name) formData.append('name', name);

    const response = await this.client.post('/datasets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  async getDataset(datasetId: string): Promise<Dataset> {
    const response = await this.client.get(`/datasets/${datasetId}`);
    return response.data;
  }

  async getValidationResults(datasetId: string): Promise<ValidationResult> {
    const response = await this.client.get(`/datasets/${datasetId}/results`);
    return response.data;
  }

  // ============ Errors Methods ============

  async getErrors(
    datasetId: string,
    skip: number = 0,
    limit: number = 50,
    filters?: { severity?: string; fieldName?: string }
  ): Promise<{ total: number; items: ValidationError[] }> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
      ...filters,
    });

    const response = await this.client.get(`/datasets/${datasetId}/errors?${params}`);
    return response.data;
  }

  // ============ Corrections Methods ============

  async getCorrections(
    datasetId: string,
    skip: number = 0,
    limit: number = 50
  ): Promise<{ total: number; accepted: number; rejected: number; pending: number; items: Correction[] }> {
    const response = await this.client.get(`/datasets/${datasetId}/corrections`, {
      params: { skip, limit },
    });
    return response.data;
  }

  async actionCorrection(
    datasetId: string,
    correctionId: string,
    isAccepted: boolean
  ): Promise<{ status: string }> {
    const response = await this.client.post(`/datasets/${datasetId}/corrections/${correctionId}/action`, {
      is_accepted: isAccepted,
    });
    return response.data;
  }

  // ============ Chunks Methods ============

  async getChunks(datasetId: string): Promise<{ total_chunks: number; chunks: ChunkInfo[] }> {
    const response = await this.client.get(`/datasets/${datasetId}/chunks`);
    return response.data;
  }

  // ============ Reports Methods ============

  async downloadReport(datasetId: string, format: 'pdf' | 'csv' = 'pdf'): Promise<Blob> {
    const response = await this.client.get(`/datasets/${datasetId}/report/${format}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // ============ Demo Methods ============

  async getDemoDatasetsNS(): Promise<DemoDataset[]> {
    const response = await this.client.get('/demo-datasets');
    return response.data.datasets;
  }

  async loadDemoDataset(demoId: string): Promise<Dataset> {
    const response = await this.client.post(`/demo-datasets/${demoId}/load`);
    return response.data;
  }

  // ============ Health Check ============

  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const apiClient = new APIClient();

/**
 * Utility functions
 */

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';

  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num);
}

export function formatPercentage(num: number, decimals: number = 1): string {
  return parseFloat((num * 100).toFixed(decimals)) + '%';
}

export function getQualityColor(score: number): string {
  if (score >= 90) return 'text-green-600';
  if (score >= 70) return 'text-yellow-600';
  if (score >= 50) return 'text-orange-600';
  return 'text-red-600';
}

export function getSeverityColor(severity: string): string {
  switch (severity) {
    case 'info':
      return 'bg-blue-100 text-blue-800';
    case 'warning':
      return 'bg-yellow-100 text-yellow-800';
    case 'error':
      return 'bg-red-100 text-red-800';
    case 'critical':
      return 'bg-red-200 text-red-900';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

export function downloadFile(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
