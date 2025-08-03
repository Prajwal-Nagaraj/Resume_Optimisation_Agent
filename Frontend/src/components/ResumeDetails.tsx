import React, { useState, useEffect } from 'react';
import { FileText, Briefcase, GraduationCap, Award, User, Code, Calendar, MapPin, Link as LinkIcon, Building } from 'lucide-react';

// A mapping from key names to icons
const iconMapping: { [key: string]: React.ElementType } = {
  personal_info: User,
  summary: FileText,
  experience: Briefcase,
  education: GraduationCap,
  skills: Code,
  projects: Briefcase,
  awards: Award,
  publications: FileText,
  certifications: Award,
  languages: User,
  references: User,
  date: Calendar,
  start_date: Calendar,
  end_date: Calendar,
  location: MapPin,
  company: Building,
  url: LinkIcon,
  website: LinkIcon,
};

// Helper to render a single value
const renderValue = (value: any) => {
  if (typeof value === 'string' && (value.startsWith('http') || value.startsWith('www'))) {
    return (
      <a href={value} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline break-all">
        {value}
      </a>
    );
  }
  return <span className="text-gray-700 break-words">{String(value)}</span>;
};

// Helper to render an editable value
const EditableValue: React.FC<{
  value: any;
  path: (string | number)[];
  onDataChange: (path: (string | number)[], value: any) => void;
}> = ({ value, path, onDataChange }) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    onDataChange(path, e.target.value);
  };

  const isLongText = typeof value === 'string' && value.length > 60;
  
  if (isLongText) {
    return (
      <textarea
        value={String(value)}
        onChange={handleChange}
        className="w-full p-2 text-base text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        rows={4}
      />
    );
  }

  return (
    <input
      type="text"
      value={String(value)}
      onChange={handleChange}
      className="w-full p-2 text-base text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  );
};

const JsonRenderer: React.FC<{ 
  data: any; 
  level?: number;
  path?: (string | number)[];
  onDataChange?: (path: (string | number)[], value: any) => void;
}> = ({ data, level = 0, path = [], onDataChange }) => {
  if (data === null || data === undefined) {
    return null;
  }

  // Handle arrays
  if (Array.isArray(data)) {
    const addItem = () => {
      if (onDataChange) {
        const newItem = typeof data[0] === 'string' ? '' : {};
        onDataChange([...path], [...data, newItem]);
      }
    };

    const removeItem = (index: number) => {
      if (onDataChange) {
        const newArray = data.filter((_, i) => i !== index);
        onDataChange([...path], newArray);
      }
    };

    return (
      <div className={`space-y-4`}>
        {data.map((item, index) => (
          <div key={index} className="bg-gray-50 p-4 rounded-lg border border-gray-200 relative">
            {onDataChange && (
              <button
                onClick={() => removeItem(index)}
                className="absolute top-2 right-2 text-red-500 hover:text-red-700 text-sm font-bold"
                title="Remove item"
              >
                ×
              </button>
            )}
            <JsonRenderer data={item} level={level + 1} path={[...path, index]} onDataChange={onDataChange} />
          </div>
        ))}
        {onDataChange && (
          <button
            onClick={addItem}
            className="mt-2 px-4 py-2 bg-green-500 text-white text-sm rounded-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            Add Item
          </button>
        )}
      </div>
    );
  }

  // Handle objects
  if (typeof data === 'object') {
    return (
      <div className={`space-y-4`}>
        {Object.entries(data).map(([key, value]) => {
          const Icon = iconMapping[key.toLowerCase()] || null;
          const isObject = value !== null && typeof value === 'object';
          
          return (
            <div key={key} className="mb-4 last:mb-0">
              <div className="flex items-center text-lg font-semibold text-gray-800 mb-2">
                {Icon && <Icon className="h-5 w-5 mr-3 text-blue-600" />}
                <span className="capitalize">{key.replace(/_/g, ' ')}</span>
              </div>
              <div className={`pl-${Icon ? '8' : '0'}`}>
                {isObject ? (
                  <JsonRenderer data={value} level={level + 1} path={[...path, key]} onDataChange={onDataChange} />
                ) : (
                  onDataChange ? 
                  <EditableValue value={value} path={[...path, key]} onDataChange={onDataChange} /> : 
                  <div className="text-base">{String(value)}</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  // Handle primitive values
  return onDataChange ? (
    <EditableValue value={data} path={path} onDataChange={onDataChange} />
  ) : (
    <div className="text-base">{String(data)}</div>
  );
};


interface ResumeDetailsProps {
    extractedData: any;
    uploadedFile: File | null;
    resumeId: string | null;
    onNavigateToJobSearch?: () => void;
}

export const ResumeDetails: React.FC<ResumeDetailsProps> = ({ extractedData, uploadedFile, resumeId, onNavigateToJobSearch }) => {
    const [editableData, setEditableData] = useState<any>(null);
    const [isSaving, setIsSaving] = useState(false);
    const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

    useEffect(() => {
      setEditableData(extractedData);
    }, [extractedData]);

    const handleDataChange = (path: (string | number)[], value: any) => {
      setEditableData((prevData: any) => {
        const newData = JSON.parse(JSON.stringify(prevData));
        let current = newData;
        for (let i = 0; i < path.length - 1; i++) {
          current = current[path[i]];
        }
        current[path[path.length - 1]] = value;
        return newData;
      });
    };

    const handleSave = async () => {
      if (!editableData || !resumeId) return;
      setIsSaving(true);
      setSaveStatus('idle');

      try {
        const response = await fetch(`http://localhost:8000/api/resume/${resumeId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(editableData),
        });

        if (response.ok) {
          setSaveStatus('success');
          // Navigate to job search after successful save
          setTimeout(() => {
            if (onNavigateToJobSearch) {
              onNavigateToJobSearch();
            }
          }, 1500); // Give user time to see success message
        } else {
          setSaveStatus('error');
        }
      } catch (error) {
        setSaveStatus('error');
      } finally {
        setIsSaving(false);
        setTimeout(() => setSaveStatus('idle'), 3000);
      }
    };
    
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-center text-3xl font-bold text-gray-900 mb-4">Resume Details</h2>
          
          {uploadedFile && (
            <div className="bg-white rounded-xl shadow-md p-6 mb-8 border border-gray-200">
              <p className="text-xl text-gray-800 mb-2">
                Processed resume: <span className="font-semibold text-blue-600">{uploadedFile.name}</span>
              </p>
              <p className="text-sm text-gray-500">
                File size: {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          )}
  
          {editableData ? (
            <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-200">
              <h3 className="text-2xl font-bold mb-6 text-gray-900 border-b pb-4">Extracted Information</h3>
              <JsonRenderer data={editableData} onDataChange={handleDataChange} />
              <div className="mt-8 pt-6 border-t border-gray-200 flex justify-end items-center">
                {saveStatus === 'success' && <p className="text-green-600 mr-4">Saved successfully!</p>}
                {saveStatus === 'error' && <p className="text-red-600 mr-4">Failed to save.</p>}
                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75 disabled:bg-gray-400"
                >
                  {isSaving ? 'Saving...' : 'Save Resume Details'}
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center bg-white p-12 rounded-xl shadow-md">
              <p className="text-gray-600 text-lg">No extracted data to display.</p>
            </div>
          )}
        </div>
      </div>
    );
}; 