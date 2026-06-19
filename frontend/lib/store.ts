/**
 * Global state management with Zustand
 */

import { create } from 'zustand';
import { Dataset, ValidationResult, ValidationError, Correction } from '@/types';

interface AppStore {
  // Current dataset
  currentDataset: Dataset | null;
  setCurrentDataset: (dataset: Dataset | null) => void;

  // Validation results
  validationResult: ValidationResult | null;
  setValidationResult: (result: ValidationResult | null) => void;

  // Errors
  errors: ValidationError[];
  setErrors: (errors: ValidationError[]) => void;
  addError: (error: ValidationError) => void;

  // Corrections
  corrections: Correction[];
  setCorrections: (corrections: Correction[]) => void;

  // UI states
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;

  uploading: boolean;
  uploadProgress: number;
  setUploading: (uploading: boolean) => void;
  setUploadProgress: (progress: number) => void;

  // Filters
  activeTab: string;
  setActiveTab: (tab: string) => void;

  // Modals
  showUploadModal: boolean;
  setShowUploadModal: (show: boolean) => void;

  showReportModal: boolean;
  setShowReportModal: (show: boolean) => void;

  // Reset
  reset: () => void;
}

export const useAppStore = create<AppStore>((set) => ({
  currentDataset: null,
  setCurrentDataset: (dataset) => set({ currentDataset: dataset }),

  validationResult: null,
  setValidationResult: (result) => set({ validationResult: result }),

  errors: [],
  setErrors: (errors) => set({ errors }),
  addError: (error) => set((state) => ({ errors: [...state.errors, error] })),

  corrections: [],
  setCorrections: (corrections) => set({ corrections }),

  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  uploading: false,
  uploadProgress: 0,
  setUploading: (uploading) => set({ uploading }),
  setUploadProgress: (progress) => set({ uploadProgress: progress }),

  activeTab: 'overview',
  setActiveTab: (tab) => set({ activeTab: tab }),

  showUploadModal: false,
  setShowUploadModal: (show) => set({ showUploadModal: show }),

  showReportModal: false,
  setShowReportModal: (show) => set({ showReportModal: show }),

  reset: () =>
    set({
      currentDataset: null,
      validationResult: null,
      errors: [],
      corrections: [],
      isLoading: false,
      uploading: false,
      uploadProgress: 0,
      activeTab: 'overview',
    }),
}));
