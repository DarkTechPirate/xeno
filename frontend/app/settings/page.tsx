/**
 * Settings Page
 */

'use client';

import React from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/Card';
import { Button } from '@/components/Button';
import { Badge } from '@/components/Badge';

export default function SettingsPage() {
  return (
    <MainLayout>
      <div className="space-y-8 max-w-2xl">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="mt-2 text-gray-600">Manage your preferences and configuration</p>
        </div>

        {/* Account Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Account Settings</CardTitle>
            <CardDescription>Manage your account information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <label className="text-sm font-medium">Email</label>
              <input
                type="email"
                className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-2 text-sm"
                placeholder="user@example.com"
                disabled
              />
            </div>
            <div>
              <label className="text-sm font-medium">Organization</label>
              <input
                type="text"
                className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-2 text-sm"
                placeholder="Your Organization"
                disabled
              />
            </div>
            <Button variant="outline" disabled>
              Update Settings
            </Button>
          </CardContent>
        </Card>

        {/* Validation Rules */}
        <Card>
          <CardHeader>
            <CardTitle>Validation Rules</CardTitle>
            <CardDescription>Configure custom validation rules</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between p-3 rounded-lg border border-gray-200">
                <div>
                  <p className="font-medium">Phone Validation</p>
                  <p className="text-sm text-gray-600">Country-specific phone format validation</p>
                </div>
                <Badge variant="success">Enabled</Badge>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg border border-gray-200">
                <div>
                  <p className="font-medium">Date Validation</p>
                  <p className="text-sm text-gray-600">Flexible date format detection</p>
                </div>
                <Badge variant="success">Enabled</Badge>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg border border-gray-200">
                <div>
                  <p className="font-medium">Duplicate Detection</p>
                  <p className="text-sm text-gray-600">Automatic duplicate record identification</p>
                </div>
                <Badge variant="success">Enabled</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* API Settings */}
        <Card>
          <CardHeader>
            <CardTitle>API & Integrations</CardTitle>
            <CardDescription>Manage API keys and integrations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium mb-2">API Key</p>
              <div className="flex gap-2">
                <input
                  type="password"
                  value="••••••••••••••••"
                  className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm"
                  disabled
                />
                <Button variant="outline" disabled>Regenerate</Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Danger Zone */}
        <Card>
          <CardHeader>
            <CardTitle className="text-red-600">Danger Zone</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button variant="destructive" disabled>
              Delete Account
            </Button>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
