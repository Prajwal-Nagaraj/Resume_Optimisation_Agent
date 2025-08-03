import React, { useState } from 'react';
import { Navigation } from './components/Navigation';
import { LandingPage } from './components/LandingPage';
import { JobSearch } from './components/JobSearch';
import { ResumeTailoring } from './components/ResumeTailoring';
import { ResumeDetails } from './components/ResumeDetails';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  postedDate: string;
  description: string;
  employmentType: string;
  experienceLevel: string;
  salary?: string;
  linkedinUrl: string;
  companyLogo?: string;
  applicants?: number;
}

function App() {
  const [activeTab, setActiveTab] = useState('landing');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [resumeId, setResumeId] = useState<string | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [selectedJobsForTailoring, setSelectedJobsForTailoring] = useState<Job[]>([]);
  const [tailoringTaskId, setTailoringTaskId] = useState<string | null>(null);
  const [extractedData, setExtractedData] = useState<any | null>(null);

  const handleFileUpload = (file: File, resumeId: string) => {
    setUploadedFile(file);
    setResumeId(resumeId);
    console.log('File uploaded:', file.name, 'Resume ID:', resumeId);
  };

  const handleExtractDetails = async () => {
    if (!resumeId) return;

    setIsExtracting(true);
    setExtractedData(null);

    try {
      // 1. Start extraction
      const startResponse = await fetch(`http://localhost:8000/api/extract/${resumeId}`, {
        method: 'POST',
      });

      if (!startResponse.ok) {
        throw new Error('Failed to start extraction process.');
      }

      // 2. Poll for status
      const poll = async (): Promise<any> => {
        const statusResponse = await fetch(`http://localhost:8000/api/extract/${resumeId}/status`);
        if (!statusResponse.ok) {
          throw new Error('Failed to get extraction status.');
        }
        const statusData = await statusResponse.json();

        if (statusData.status === 'completed') {
          return statusData.extracted_data;
        } else if (statusData.status === 'failed') {
          throw new Error(statusData.error_message || 'Extraction failed.');
        } else {
          // It's still processing, wait and poll again
          await new Promise(resolve => setTimeout(resolve, 2000)); // wait 2 seconds
          return await poll();
        }
      };

      const data = await poll();
      setExtractedData(data);

      // Navigate to Resume Details tab
      setActiveTab('details');
    } catch (error: any) {
      console.error('Error extracting resume details:', error);
      alert(`Extraction failed: ${error.message}`);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleJobsTailored = (jobs: Job[], taskId?: string) => {
    setSelectedJobsForTailoring(jobs);
    setTailoringTaskId(taskId || null);
    setActiveTab('tailoring');
  };

  const handleBackToJobSearch = () => {
    setActiveTab('search');
  };

  const handleNavigateToJobSearch = () => {
    setActiveTab('search');
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'landing':
        return (
          <LandingPage 
            onFileUpload={handleFileUpload} 
            uploadedFile={uploadedFile}
            onExtractDetails={handleExtractDetails}
            isExtracting={isExtracting}
          />
        );
      case 'details':
        return (
          <ResumeDetails 
            extractedData={extractedData}
            uploadedFile={uploadedFile}
            resumeId={resumeId}
            onNavigateToJobSearch={handleNavigateToJobSearch}
          />
        );
      case 'search':
        return <JobSearch onJobsTailored={handleJobsTailored} resumeId={resumeId} />;
      case 'tailoring':
        return (
          <ResumeTailoring 
            selectedJobs={selectedJobsForTailoring}
            onBack={handleBackToJobSearch}
            taskId={tailoringTaskId || undefined}
          />
        );
      default:
        return (
          <LandingPage 
            onFileUpload={handleFileUpload} 
            uploadedFile={uploadedFile}
            onExtractDetails={handleExtractDetails}
            isExtracting={isExtracting}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      {renderContent()}
    </div>
  );
}

export default App;