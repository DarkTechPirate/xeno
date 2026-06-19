/**
 * Dataset Detail Page - Main Validation Dashboard
 */

'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { MainLayout } from '@/components/MainLayout';
import { Button } from '@/components/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { QualityScoreGauge, StatCard } from '@/components/';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/Tabs';
import { Download, BarChart3, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { Dataset, ValidationResult, ValidationError } from '@/types';
import toast from 'react-hot-toast';

export default function DatasetDetailPage() {
  const params = useParams();
  const datasetId = params.datasetId as string;
  
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [results, setResults] = useState<ValidationResult | null>(null);
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [datasetData, resultsData, errorsData] = await Promise.all([
          apiClient.getDataset(datasetId),
          apiClient.getValidationResults(datasetId),
          apiClient.getErrors(datasetId, 0, 100),
        ]);
        
        setDataset(datasetData);
        setResults(resultsData);
        setErrors(errorsData.items);
      } catch (error) {
        console.error('Error loading dataset:', error);
        toast.error('Failed to load dataset details');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [datasetId]);

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        </div>
      </MainLayout>
    );
  }

  if (!dataset) {
    return (
      <MainLayout>
        <Card>
          <CardContent className="py-12 text-center">
            <AlertCircle className="mb-4 h-12 w-12 text-red-500 mx-auto" />
            <h3 className="text-lg font-semibold">Dataset Not Found</h3>
          </CardContent>
        </Card>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-start">
          <div className="flex-1">
            <h1 className="text-3xl font-bold tracking-tight">{dataset.name}</h1>
            <div className="mt-2 flex flex-wrap gap-2">
              <Badge variant="secondary">{dataset.metadata.total_records.toLocaleString()} records</Badge>
              <Badge variant="secondary">{dataset.metadata.total_columns} columns</Badge>
              <Badge variant="success">{dataset.status}</Badge>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-2">
              <Download className="h-4 w-4" />
              Export Report
            </Button>
            <Button size="sm" className="gap-2">
              <Download className="h-4 w-4" />
              Download Cleaned Data
            </Button>
          </div>
        </div>

        {/* Quality Overview */}
        <div className="grid gap-6 md:grid-cols-4">
          <Card className="md:col-span-1">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Quality Score</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center">
              <QualityScoreGauge score={dataset.health.quality_score} size="sm" showLabel={false} />
            </CardContent>
          </Card>

          <StatCard
            title="Valid Records"
            value={results?.valid_records.toLocaleString() || '0'}
            icon={<CheckCircle className="h-5 w-5" />}
          />
          
          <StatCard
            title="Invalid Records"
            value={results?.invalid_records.toLocaleString() || '0'}
            icon={<AlertCircle className="h-5 w-5" />}
          />

          <StatCard
            title="Completeness"
            value={`${dataset.health.completeness_score.toFixed(1)}%`}
          />
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-4 w-full">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="errors">Errors</TabsTrigger>
            <TabsTrigger value="corrections">Corrections</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Dataset Metadata</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-600">Total Records</p>
                    <p className="text-lg font-semibold">{dataset.metadata.total_records.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Columns</p>
                    <p className="text-lg font-semibold">{dataset.metadata.total_columns}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Countries Detected</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {dataset.metadata.detected_countries.map((country) => (
                        <Badge key={country} variant="secondary">{country}</Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Quality Metrics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm font-medium">Completeness</span>
                      <span className="text-sm font-bold">{dataset.health.completeness_score.toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-600 transition-all"
                        style={{ width: `${dataset.health.completeness_score}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm font-medium">Accuracy</span>
                      <span className="text-sm font-bold">{dataset.health.accuracy_score.toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-green-600 transition-all"
                        style={{ width: `${dataset.health.accuracy_score}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm font-medium">Consistency</span>
                      <span className="text-sm font-bold">{dataset.health.consistency_score.toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-yellow-600 transition-all"
                        style={{ width: `${dataset.health.consistency_score}%` }}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Data Issues Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                    <span className="font-medium">Duplicate Records</span>
                    <span className="text-lg font-bold">{dataset.metadata.duplicate_record_count}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                    <span className="font-medium">Missing Values</span>
                    <span className="text-lg font-bold">{dataset.metadata.missing_values_count}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Errors Tab */}
          <TabsContent value="errors" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Validation Errors</CardTitle>
                <CardDescription>
                  Found {errors.length} errors across the dataset
                </CardDescription>
              </CardHeader>
              <CardContent>
                {errors.length === 0 ? (
                  <div className="text-center py-8">
                    <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                    <p className="text-gray-600">No errors found in this dataset!</p>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {errors.slice(0, 10).map((error) => (
                      <div key={error.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-medium">{error.field_name}</p>
                            <p className="text-sm text-gray-600 mt-1">{error.error_message}</p>
                            <p className="text-xs text-gray-500 mt-2">Row {error.row_number}</p>
                          </div>
                          <Badge variant={error.severity as any}>
                            {error.severity}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Corrections Tab */}
          <TabsContent value="corrections">
            <Card>
              <CardHeader>
                <CardTitle>Auto-Correction Suggestions</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">Correction suggestions coming soon...</p>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Reports Tab */}
          <TabsContent value="reports">
            <Card>
              <CardHeader>
                <CardTitle>Generated Reports</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start" disabled>
                    <Download className="mr-2 h-4 w-4" />
                    Download PDF Report
                  </Button>
                  <Button variant="outline" className="w-full justify-start" disabled>
                    <Download className="mr-2 h-4 w-4" />
                    Download CSV Report
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
}
