/**
 * Quality Score Gauge Component
 */

import React from 'react';
import { formatPercentage } from '@/lib/api';
import clsx from 'clsx';

interface QualityScoreGaugeProps {
  score: number; // 0-100
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export function QualityScoreGauge({ score, size = 'md', showLabel = true }: QualityScoreGaugeProps) {
  const sizeClasses = {
    sm: 'w-24 h-24',
    md: 'w-32 h-32',
    lg: 'w-48 h-48',
  };

  const radius = size === 'sm' ? 35 : size === 'md' ? 50 : 75;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const getColor = (score: number) => {
    if (score >= 90) return '#10b981'; // green
    if (score >= 70) return '#f59e0b'; // yellow
    if (score >= 50) return '#f97316'; // orange
    return '#ef4444'; // red
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div className={clsx('relative', sizeClasses[size])}>
        <svg
          className="absolute inset-0 rotate-[-90deg]"
          width={size === 'sm' ? 96 : size === 'md' ? 128 : 192}
          height={size === 'sm' ? 96 : size === 'md' ? 128 : 192}
        >
          {/* Background circle */}
          <circle
            cx={size === 'sm' ? 48 : size === 'md' ? 64 : 96}
            cy={size === 'sm' ? 48 : size === 'md' ? 64 : 96}
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth={size === 'sm' ? 3 : size === 'md' ? 4 : 6}
          />

          {/* Progress circle */}
          <circle
            cx={size === 'sm' ? 48 : size === 'md' ? 64 : 96}
            cy={size === 'sm' ? 48 : size === 'md' ? 64 : 96}
            r={radius}
            fill="none"
            stroke={getColor(score)}
            strokeWidth={size === 'sm' ? 3 : size === 'md' ? 4 : 6}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{
              transition: 'stroke-dashoffset 0.5s ease',
            }}
          />
        </svg>

        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={clsx(
            'font-bold text-center',
            size === 'sm' ? 'text-xl' : size === 'md' ? 'text-2xl' : 'text-4xl'
          )}>
            {score.toFixed(1)}
          </span>
          <span className={clsx(
            'text-muted-foreground',
            size === 'sm' ? 'text-xs' : size === 'md' ? 'text-sm' : 'text-base'
          )}>
            {getQualityLabel(score)}
          </span>
        </div>
      </div>

      {showLabel && (
        <p className={clsx(
          'mt-4 text-center font-medium',
          size === 'sm' ? 'text-xs' : size === 'md' ? 'text-sm' : 'text-base'
        )}>
          Data Quality Score
        </p>
      )}
    </div>
  );
}

function getQualityLabel(score: number): string {
  if (score >= 90) return 'Excellent';
  if (score >= 70) return 'Good';
  if (score >= 50) return 'Fair';
  return 'Poor';
}
