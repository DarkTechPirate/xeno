/**
 * Badge component
 */

import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import clsx from 'clsx';

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ring-1 ring-inset',
  {
    variants: {
      variant: {
        default: 'bg-blue-50 text-blue-700 ring-blue-600/20',
        secondary: 'bg-gray-50 text-gray-700 ring-gray-600/20',
        success: 'bg-green-50 text-green-700 ring-green-600/20',
        warning: 'bg-yellow-50 text-yellow-700 ring-yellow-600/20',
        danger: 'bg-red-50 text-red-700 ring-red-600/20',
        info: 'bg-blue-50 text-blue-700 ring-blue-600/20',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={clsx(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
