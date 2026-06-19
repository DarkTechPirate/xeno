/**
 * Datasets Dashboard Page
 */

'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { MainLayout } from '@/components/MainLayout';
import { Button } from '@/components/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Upload, Loader2, Plus, BarChart3 } from 'lucide-react';
import { apiClient, formatBytes } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import toast from 'react-hot-toast';

export default function DatasetsPage() {
  const router = useRouter();
  const [datasets, setDatasets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDatasets = async () => {
      try {
        setLoading(true);
        // In real implementation, fetch from API
        // const response = await apiClient.getDatasets();
        // setDatasets(response);
      } catch (error) {
        console.error('Error loading datasets:', error);
        toast.error('Failed to load datasets');
      } finally {
        setLoading(false);
      }
    };

    loadDatasets();
  }, []);

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Datasets</h1>
            <p className="mt-2 text-gray-600">Manage and analyze your transaction datasets</p>
          </div>
          <Link href="/upload">
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Upload Dataset
            </Button>
          </Link>
        </div>

        {/* Empty State or List */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          </div>
        ) : datasets.length === 0 ? (
          <Card className="border-2 border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Upload className="mb-4 h-12 w-12 text-gray-400" />
              <h3 className="mb-2 text-lg font-semibold">No datasets yet</h3>
              <p className="mb-6 max-w-sm text-center text-sm text-gray-600">
                Upload your first CSV file to start validating transaction data
              </p>
              <Link href="/upload">
                <Button>Upload CSV</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {datasets.map((dataset: any) => (
              <Card
                key={dataset.id}
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => router.push(`/datasets/${dataset.id}`)}
              >
                <CardHeader>
                  <CardTitle className="text-lg">{dataset.name}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-600">Records</p>
                    <p className="text-2xl font-bold">
                      {dataset.total_records.toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Quality Score</p>
                      <p className="text-xl font-bold text-blue-600">
                        {dataset.quality_score.toFixed(1)}%
                      </p>
                    </div>
                    <Badge variant="success">
                      {dataset.status}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
