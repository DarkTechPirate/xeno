/**
 * Dashboard Page
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { MainLayout } from '@/components/MainLayout';
import { Button } from '@/components/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card';
import { BarChart3, Upload, TrendingUp, Clock } from 'lucide-react';
import { StatCard } from '@/components/';

export default function DashboardPage() {
  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="mt-2 text-gray-600">Welcome to TransactIQ</p>
          </div>
          <Link href="/upload">
            <Button className="gap-2">
              <Upload className="h-4 w-4" />
              Upload Dataset
            </Button>
          </Link>
        </div>

        {/* Stats */}
        <div className="grid gap-6 md:grid-cols-4">
          <StatCard
            title="Total Datasets"
            value="0"
            icon={<BarChart3 className="h-5 w-5" />}
          />
          <StatCard
            title="Records Validated"
            value="0"
            icon={<TrendingUp className="h-5 w-5" />}
          />
          <StatCard
            title="Avg Quality Score"
            value="0%"
            icon={<BarChart3 className="h-5 w-5" />}
          />
          <StatCard
            title="Processing Time"
            value="0s"
            icon={<Clock className="h-5 w-5" />}
          />
        </div>

        {/* Quick Start */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Start</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <Button variant="outline" className="justify-start h-auto flex-col items-start p-4" disabled>
                <Upload className="h-5 w-5 mb-2" />
                <span>Upload Your CSV</span>
                <span className="text-xs text-gray-500 mt-1">Add your transaction data</span>
              </Button>
              <Button variant="outline" className="justify-start h-auto flex-col items-start p-4" disabled>
                <BarChart3 className="h-5 w-5 mb-2" />
                <span>View Results</span>
                <span className="text-xs text-gray-500 mt-1">Check validation results</span>
              </Button>
              <Button variant="outline" className="justify-start h-auto flex-col items-start p-4" disabled>
                <TrendingUp className="h-5 w-5 mb-2" />
                <span>Export Report</span>
                <span className="text-xs text-gray-500 mt-1">Download compliance reports</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
