'use client';

import React, { useState } from 'react';
import { TableCellsIcon, SparklesIcon } from '@heroicons/react/24/outline';
import BusinessDataManager from './BusinessDataManager';
import DatasetUploader from './DatasetUploader';

type DataSubTab = 'business' | 'uploaded';

const SUB_TABS: { id: DataSubTab; label: string; icon: React.ElementType }[] = [
  { id: 'business', label: 'Business Tables', icon: TableCellsIcon },
  { id: 'uploaded', label: 'Uploaded Tables', icon: SparklesIcon },
];

/**
 * Unified "Data" workspace. Groups the two data-management surfaces that used to
 * be separate admin tabs:
 *   - Business Tables  -> CRUD + CSV import for the built-in tables
 *   - Uploaded Tables  -> create new tables from a CSV / manage dynamic tables
 * Both feed the same database the analyst queries, so they live under one roof.
 */
export const DataWorkspace: React.FC = () => {
  const [sub, setSub] = useState<DataSubTab>('business');

  return (
    <div className="space-y-5">
      <div className="flex gap-1.5">
        {SUB_TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setSub(id)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold cursor-pointer transition-colors ${
              sub === id
                ? 'bg-primary/10 text-primary'
                : 'text-muted-foreground hover:bg-muted/40 hover:text-foreground'
            }`}
          >
            <Icon className="h-4 w-4" />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {sub === 'business' && <BusinessDataManager />}
      {sub === 'uploaded' && <DatasetUploader />}
    </div>
  );
};

export default DataWorkspace;
