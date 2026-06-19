/**
 * Upload Page
 */

'use client';

import React, { useCallback, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Upload, File, X, Loader2, CheckCircle } from 'lucide-react';
import { Button } from '@/components/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card';
import { apiClient, formatBytes } from '@/lib/api';
import toast from 'react-hot-toast';

export default function UploadPage() {
  const router = useRouter();
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      const droppedFile = files[0];
      if (droppedFile.type === 'text/csv' || droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
      } else {
        toast.error('Please drop a CSV file');
      }
    }
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  }, []);

  const handleUpload = async () => {
    if (!file) return;

    try {
      setUploading(true);
      const result = await apiClient.uploadDataset(file);
      toast.success('Dataset uploaded and processed!');
      router.push(`/datasets/${result.dataset_id}`);
    } catch (error: any) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Failed to upload dataset');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      {/* Navigation */}
      <nav className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 md:px-8">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white font-bold">
              T
            </div>
            <span className="text-lg font-semibold">TransactIQ</span>
          </Link>
        </div>
      </nav>

      {/* Upload Container */}
      <div className="mx-auto max-w-2xl px-4 py-16 md:px-8 md:py-24">
        <div className="mb-12 text-center">
          <h1 className="mb-4 text-3xl font-bold tracking-tight md:text-4xl">
            Upload Your Transaction Data
          </h1>
          <p className="text-lg text-gray-600">
            Supported format: CSV files up to 5GB
          </p>
        </div>

        <Card className="overflow-hidden">
          <CardHeader>
            <CardTitle>Select CSV File</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Upload Area */}
            {!file ? (
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`relative flex flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-16 transition-colors ${
                  dragActive
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 bg-gray-50 hover:border-gray-400'
                }`}
              >
                <Upload className="mb-4 h-12 w-12 text-gray-400" />
                <p className="mb-2 text-center text-lg font-semibold">
                  Drag and drop your CSV file here
                </p>
                <p className="mb-6 text-center text-sm text-gray-600">
                  or click to browse
                </p>

                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileInput}
                  className="absolute inset-0 cursor-pointer opacity-0"
                />

                <Button variant="outline" size="lg">
                  <Upload className="mr-2 h-5 w-5" />
                  Browse Files
                </Button>

                <p className="mt-6 text-center text-xs text-gray-500">
                  Maximum file size: 5GB
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* File Info */}
                <div className="flex items-center justify-between rounded-lg bg-blue-50 p-4">
                  <div className="flex items-center gap-4">
                    <File className="h-8 w-8 text-blue-600" />
                    <div>
                      <p className="font-medium text-gray-900">{file.name}</p>
                      <p className="text-sm text-gray-600">
                        {formatBytes(file.size)}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setFile(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                {/* Upload Progress */}
                {uploading && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">
                        {uploadProgress < 100 ? 'Uploading...' : 'Processing...'}
                      </p>
                      <span className="text-sm text-gray-600">
                        {uploadProgress}%
                      </span>
                    </div>
                    <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-600 transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-4 pt-4">
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => setFile(null)}
                    disabled={uploading}
                  >
                    Choose Different File
                  </Button>
                  <Button
                    className="flex-1 gap-2"
                    onClick={handleUpload}
                    disabled={uploading}
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-4 w-4" />
                        Upload & Process
                      </>
                    )}
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Info Cards */}
        <div className="mt-12 grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">What Gets Validated?</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-gray-600">
              <p>✓ Order-level details</p>
              <p>✓ Product information</p>
              <p>✓ Payment data</p>
              <p>✓ Phone numbers (country-specific)</p>
              <p>✓ Date and time formats</p>
              <p>✓ Data integrity & duplicates</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">What You Get</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-gray-600">
              <p>✓ Detailed error report</p>
              <p>✓ Auto-correction suggestions</p>
              <p>✓ Quality scoring (0-100%)</p>
              <p>✓ Cleaned dataset download</p>
              <p>✓ Compliance reports (PDF/CSV)</p>
              <p>✓ AI-powered insights</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
