'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';

// Dynamically import Plotly with SSR disabled to prevent Node compilation errors
const Plot = dynamic(() => import('react-plotly.js'), {
  ssr: false,
  loading: () => <div className="h-72 w-full flex items-center justify-center text-muted-foreground text-xs">Loading charts library...</div>
});

interface QueryVisualizerProps {
  config: Record<string, any>;
}

export const QueryVisualizer: React.FC<QueryVisualizerProps> = ({ config }) => {
  if (!config) return null;

  const layout = {
    ...config.layout,
    autosize: true,
    font: { color: '#6B7280', family: 'Inter, sans-serif' },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    xaxis: {
      ...config.layout?.xaxis,
      gridcolor: '#E5E7EB',
      linecolor: '#D1D5DB',
      tickcolor: '#D1D5DB',
    },
    yaxis: {
      ...config.layout?.yaxis,
      gridcolor: '#E5E7EB',
      linecolor: '#D1D5DB',
      tickcolor: '#D1D5DB',
    },
  };

  return (
    <Card className="border-border bg-card mt-4">
      <CardHeader className="py-4">
        <CardTitle className="text-sm font-medium text-muted-foreground">Data Visualization Preview</CardTitle>
      </CardHeader>
      <CardContent className="flex justify-center overflow-hidden">
        <div className="w-full max-w-4xl h-80">
          <Plot
            data={config.data || []}
            layout={layout}
            useResizeHandler={true}
            className="w-full h-full"
            config={{ responsive: true, displayModeBar: false }}
          />
        </div>
      </CardContent>
    </Card>
  );
};

export default QueryVisualizer;
