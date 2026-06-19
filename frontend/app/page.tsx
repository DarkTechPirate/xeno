/**
 * Landing Page - Home
 */

'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Upload, Zap, BarChart3, Shield, ArrowRight, Loader2 } from 'lucide-react';
import { Button } from '@/components/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { apiClient } from '@/lib/api';
import { DemoDataset } from '@/types';
import toast from 'react-hot-toast';

export default function HomePage() {
  const router = useRouter();
  const [demoDatasets, setDemoDatasets] = useState<DemoDataset[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingDemo, setLoadingDemo] = useState<string | null>(null);

  useEffect(() => {
    const loadDemoDatasets = async () => {
      try {
        setLoading(true);
        const datasets = await apiClient.getDemoDatasetsNS();
        setDemoDatasets(datasets);
      } catch (error) {
        console.error('Error loading demo datasets:', error);
        toast.error('Failed to load demo datasets');
      } finally {
        setLoading(false);
      }
    };

    loadDemoDatasets();
  }, []);

  const handleLoadDemo = async (demoId: string) => {
    try {
      setLoadingDemo(demoId);
      const dataset = await apiClient.loadDemoDataset(demoId);
      toast.success('Demo dataset loaded!');
      router.push(`/datasets/${dataset.id}`);
    } catch (error) {
      console.error('Error loading demo:', error);
      toast.error('Failed to load demo dataset');
    } finally {
      setLoadingDemo(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 md:px-8">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white font-bold">
              T
            </div>
            <span className="text-lg font-semibold">TransactIQ</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-sm font-medium text-gray-600 hover:text-gray-900">
              Dashboard
            </Link>
            <Button size="sm">Sign In</Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="mx-auto max-w-7xl px-4 pt-32 pb-16 md:px-8 md:pt-40 md:pb-24">
        <div className="text-center">
          <div className="mb-4 inline-block">
            <Badge variant="secondary">Enterprise-Grade Data Validation</Badge>
          </div>

          <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-6xl">
            Transform Raw Transaction Data Into{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Business-Ready Insights
            </span>
          </h1>

          <p className="mx-auto mb-10 max-w-2xl text-lg text-gray-600">
            Validate, clean, correct, analyze, and export transaction datasets with enterprise-grade accuracy. 
            Detect errors, suggest fixes, and generate compliance-ready reports—all in one platform.
          </p>

          <div className="mb-12 flex flex-col justify-center gap-4 sm:flex-row">
            <Link href="/upload">
              <Button size="lg" className="gap-2">
                <Upload className="h-5 w-5" />
                Upload CSV
              </Button>
            </Link>
            <Button
              variant="outline"
              size="lg"
              className="gap-2"
              onClick={() => document.getElementById('demo-datasets')?.scrollIntoView({ behavior: 'smooth' })}
            >
              <Zap className="h-5 w-5" />
              Try Demo Dataset
            </Button>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3 mt-20">
          <Card>
            <CardHeader>
              <Shield className="mb-2 h-8 w-8 text-blue-600" />
              <CardTitle className="text-lg">Enterprise Validation</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Multi-level validation for orders, products, payments, and compliance with country-specific rules.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Zap className="mb-2 h-8 w-8 text-blue-600" />
              <CardTitle className="text-lg">Auto-Correction Engine</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Intelligent suggestions with confidence scores. Accept or reject fixes with full audit trail.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <BarChart3 className="mb-2 h-8 w-8 text-blue-600" />
              <CardTitle className="text-lg">AI Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Root-cause analysis, failure patterns, and business-level recommendations in real-time.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Demo Datasets Section */}
      <section id="demo-datasets" className="mx-auto max-w-7xl px-4 py-16 md:px-8 md:py-24">
        <div className="mb-12">
          <h2 className="mb-4 text-3xl font-bold tracking-tight">Pre-Loaded Demo Datasets</h2>
          <p className="text-lg text-gray-600">
            Start exploring TransactIQ instantly. No setup required.
          </p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
            {demoDatasets.map((dataset) => (
              <Card key={dataset.id} className="flex flex-col overflow-hidden hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-base">{dataset.name}</CardTitle>
                  <CardDescription className="text-xs">
                    {dataset.record_count.toLocaleString()} rows
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-1">
                  <p className="text-sm text-gray-600 mb-4">{dataset.description}</p>
                  <div className="flex flex-wrap gap-1 mb-4">
                    {dataset.scenarios.slice(0, 2).map((scenario) => (
                      <Badge key={scenario} variant="secondary" className="text-xs">
                        {scenario.replace(/_/g, ' ')}
                      </Badge>
                    ))}
                    {dataset.scenarios.length > 2 && (
                      <Badge variant="secondary" className="text-xs">
                        +{dataset.scenarios.length - 2} more
                      </Badge>
                    )}
                  </div>
                </CardContent>
                <div className="p-6 border-t border-gray-200 pt-4">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full gap-2"
                    onClick={() => handleLoadDemo(dataset.id)}
                    disabled={loadingDemo === dataset.id}
                  >
                    {loadingDemo === dataset.id ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Loading...
                      </>
                    ) : (
                      <>
                        <ArrowRight className="h-4 w-4" />
                        Load Dataset
                      </>
                    )}
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>

      {/* CTA Section */}
      <section className="border-t border-gray-200 bg-gray-50 py-16 md:py-24">
        <div className="mx-auto max-w-4xl px-4 text-center md:px-8">
          <h2 className="mb-4 text-3xl font-bold tracking-tight">Ready to Validate Your Data?</h2>
          <p className="mb-8 text-lg text-gray-600">
            Join enterprise clients worldwide who trust TransactIQ to ensure data quality and compliance.
          </p>
          <div className="flex flex-col justify-center gap-4 sm:flex-row">
            <Link href="/upload">
              <Button size="lg" className="gap-2">
                <Upload className="h-5 w-5" />
                Upload Your CSV
              </Button>
            </Link>
            <Button variant="outline" size="lg">
              Contact Sales
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white py-12">
        <div className="mx-auto max-w-7xl px-4 md:px-8">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4 mb-12">
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link href="#" className="hover:text-gray-900">Features</Link></li>
                <li><Link href="#" className="hover:text-gray-900">Pricing</Link></li>
                <li><Link href="#" className="hover:text-gray-900">Security</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link href="#" className="hover:text-gray-900">About</Link></li>
                <li><Link href="#" className="hover:text-gray-900">Blog</Link></li>
                <li><Link href="#" className="hover:text-gray-900">Careers</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link href="#" className="hover:text-gray-900">Docs</Link></li>
                <li><Link href="#" className="hover:text-gray-900">API</Link></li>
                <li><Link href="#" className="hover:text-gray-900">Support</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link href="#" className="hover:text-gray-900">Privacy</Link></li>
                <li><Link href="#" className="hover:text-gray-900">Terms</Link></li>
                <li><Link href="#" className="hover:text-gray-900">Contact</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-200 pt-8 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              © 2025 TransactIQ. All rights reserved.
            </p>
            <div className="flex gap-4">
              <Link href="#" className="text-gray-600 hover:text-gray-900">
                Twitter
              </Link>
              <Link href="#" className="text-gray-600 hover:text-gray-900">
                LinkedIn
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
