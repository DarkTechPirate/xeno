/**
 * Stat Card Component
 */

import React from 'react';
import { Card } from './Card';
import clsx from 'clsx';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
}

export function StatCard({ title, value, change, icon, trend = 'neutral' }: StatCardProps) {
  const trendColor = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-gray-600',
  };

  return (
    <Card className="overflow-hidden">
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="mt-2 text-3xl font-bold">{value}</p>
            {change !== undefined && (
              <p className={clsx('mt-2 text-sm font-medium', trendColor[trend])}>
                {trend === 'up' && '+'}
                {change}% from last week
              </p>
            )}
          </div>
          {icon && (
            <div className="text-muted-foreground opacity-50">{icon}</div>
          )}
        </div>
      </div>
    </Card>
  );
}

/**
 * Progress Bar Component
 */

interface ProgressBarProps {
  value: number;
  max?: number;
  className?: string;
  showLabel?: boolean;
  color?: 'green' | 'yellow' | 'red' | 'blue';
}

export function ProgressBar({
  value,
  max = 100,
  className,
  showLabel = true,
  color = 'blue',
}: ProgressBarProps) {
  const percentage = (value / max) * 100;

  const colorClasses = {
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    blue: 'bg-blue-500',
  };

  return (
    <div className={className}>
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className={clsx(colorClasses[color], 'h-full transition-all duration-500')}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <p className="text-xs text-muted-foreground mt-1">
          {value} / {max}
        </p>
      )}
    </div>
  );
}
