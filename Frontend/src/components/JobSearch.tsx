import React, { useState } from 'react';
import { Search, MapPin, Calendar, Globe, Settings, Briefcase, Target, CheckSquare, Square, Hash } from 'lucide-react';
import { JobCard } from './JobCard';
import { JobDetailsModal } from './JobDetailsModal';

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
  industry?: string;
  companySize?: string;
  skills?: string;
}

interface JobSearchProps {
  onJobsTailored: (jobs: Job[], taskId?: string) => void;
  resumeId: string | null;
}

export const JobSearch: React.FC<JobSearchProps> = ({ onJobsTailored, resumeId }) => {
  const [searchParams, setSearchParams] = useState({
    jobTitle: '',
    location: '',
    datePosted: '7', // Default to "Past week"
    resultsCount: '20' // Default to 20 jobs
  });
  const [useProxy, setUseProxy] = useState(false);
  const [proxyUrl, setProxyUrl] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [searchPerformed, setSearchPerformed] = useState(false);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedJobs, setSelectedJobs] = useState<Set<string>>(new Set());
  const [isTailoring, setIsTailoring] = useState(false);

  const dateOptions = [
    { value: 'any', label: 'Any time' },
    { value: '1', label: 'Past 24 hours' },
    { value: '7', label: 'Past week' },
    { value: '30', label: 'Past month' }
  ];

  const handleInputChange = (field: string, value: string) => {
    setSearchParams(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const searchJobsFromBackend = async (): Promise<Job[]> => {
    try {
      // Build query parameters
      const params = new URLSearchParams({
        query: searchParams.jobTitle,
        location: searchParams.location,
        limit: searchParams.resultsCount
      });

      // Add proxy parameter if enabled
      if (useProxy && proxyUrl.trim()) {
        params.append('proxy', proxyUrl);
      }

      // Make API call to backend
      const response = await fetch(`http://localhost:8000/api/search?${params.toString()}`);

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      // Transform backend response to match our Job interface
      const transformedJobs: Job[] = data.jobs.map((job: any, index: number) => ({
        id: job.id || `job_${index}`,
        title: job.title || job.Title || 'Unknown Title',
        company: job.company || job.Company || 'Unknown Company',
        location: job.location || job.Location || 'Unknown Location',
        postedDate: job.date_posted || job.posted_date || job.postedDate || job['Posted Date'] || 'Recently',
        description: job.description || job.Description || 'No description available',
        employmentType: job.job_type || job.employment_type || job.employmentType || job['Employment Type'] || 'Full-time',
        experienceLevel: job.job_level || job.experience_level || job.experienceLevel || job['Experience Level'] || 'Not specified',
        salary: job.min_amount && job.max_amount ? `$${job.min_amount/1000}k - $${job.max_amount/1000}k` : (job.salary || job.Salary || undefined),
        linkedinUrl: job.job_url || job.linkedin_url || job.linkedinUrl || job['LinkedIn URL'] || job.url || '#',
        companyLogo: job.company_logo || job.companyLogo || undefined,
        applicants: job.applicants || job.Applicants || undefined,
        industry: job.company_industry || undefined,
        companySize: job.company_num_employees || undefined,
        skills: job.skills || undefined,
      }));

      return transformedJobs;
    } catch (error) {
      console.error('Job search API error:', error);
      throw error;
    }
  };

  const tailorResumeWithBackend = async (selectedJobsData: Job[]) => {
    try {
      if (!resumeId) {
        throw new Error('No resume uploaded. Please upload a resume first.');
      }

      // Transform jobs data to send job descriptions and company names
      const jobDescriptions = selectedJobsData.map(job => ({
        description: job.description,
        company: job.company
      }));

      const payload = {
        resume_id: resumeId,
        job_descriptions: jobDescriptions
      };

      console.log('Sending tailoring request to backend:', payload);

      const response = await fetch('http://localhost:8000/api/tailor', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Backend tailoring response:', result);
      
      return result;
    } catch (error) {
      console.error('Error tailoring resume with backend:', error);
      throw error;
    }
  };

  const handleSearch = async () => {
    if (!searchParams.jobTitle.trim()) {
      alert('Please enter a job title');
      return;
    }

    if (!searchParams.location.trim()) {
      alert('Please enter a location');
      return;
    }

    if (useProxy && !proxyUrl.trim()) {
      alert('Please enter a proxy URL');
      return;
    }

    const resultsCount = parseInt(searchParams.resultsCount);
    if (isNaN(resultsCount) || resultsCount < 1 || resultsCount > 500) {
      alert('Please enter a valid number of jobs between 1 and 500');
      return;
    }

    setIsSearching(true);
    setSearchPerformed(true);
    setSelectedJobs(new Set()); // Clear previous selections

    try {
      console.log('Searching with params:', searchParams);
      console.log('Using proxy:', useProxy ? proxyUrl : 'No proxy');
      console.log('Requesting', searchParams.resultsCount, 'jobs');
      
      const searchResults = await searchJobsFromBackend();
      setJobs(searchResults);
    } catch (error: any) {
      console.error('Search failed:', error);
      const errorMessage = error.message || 'Search failed. Please try again.';
      alert(`Job search failed: ${errorMessage}`);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleJobClick = (job: Job) => {
    setSelectedJob(job);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedJob(null);
  };

  const handleJobSelection = (jobId: string, selected: boolean) => {
    setSelectedJobs(prev => {
      const newSet = new Set(prev);
      if (selected) {
        newSet.add(jobId);
      } else {
        newSet.delete(jobId);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (selectedJobs.size === jobs.length) {
      // Deselect all
      setSelectedJobs(new Set());
    } else {
      // Select all
      setSelectedJobs(new Set(jobs.map(job => job.id)));
    }
  };

  const handleTailorResumes = async () => {
    if (selectedJobs.size === 0) {
      alert('Please select at least one job to tailor your resume for.');
      return;
    }

    if (!resumeId) {
      alert('Please upload and extract a resume first before tailoring.');
      return;
    }

    setIsTailoring(true);
    
    try {
      // Get the selected job objects
      const selectedJobsData = jobs.filter(job => selectedJobs.has(job.id));
      
      // Start resume tailoring process with backend
      console.log('Starting resume tailoring process...');
      const tailoringResult = await tailorResumeWithBackend(selectedJobsData);
      
      if (tailoringResult.task_id) {
        console.log('Resume tailoring started with task ID:', tailoringResult.task_id);
        alert(`✅ Resume tailoring started successfully! Task ID: ${tailoringResult.task_id}\n\nYou can check the status in the tailoring tab.`);
        
        // Navigate to tailoring tab with selected jobs and task ID
        onJobsTailored(selectedJobsData, tailoringResult.task_id);
      } else {
        throw new Error('No task ID received from backend');
      }
      
    } catch (error: any) {
      console.error('Resume tailoring failed:', error);
      alert(`❌ Failed to start resume tailoring: ${error.message}`);
    } finally {
      setIsTailoring(false);
    }
  };

  const TailorButton = ({ className = "" }: { className?: string }) => (
    <button
      onClick={handleTailorResumes}
      disabled={selectedJobs.size === 0 || isTailoring || !resumeId}
      className={`inline-flex items-center space-x-3 px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-200 ${
        selectedJobs.size === 0 || isTailoring || !resumeId
          ? 'bg-gray-400 cursor-not-allowed text-white'
          : 'bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white shadow-lg hover:shadow-xl'
      } ${className}`}
    >
      {isTailoring ? (
        <>
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
          <span>Processing & Storing Jobs...</span>
        </>
      ) : (
        <>
          <Target className="h-5 w-5" />
          <span>
            {!resumeId 
              ? 'Upload Resume First' 
              : selectedJobs.size === 0 
                ? 'Select Jobs to Tailor Resume'
                : `Tailor Resume for Selected Jobs (${selectedJobs.size})`
            }
          </span>
        </>
      )}
    </button>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            LinkedIn Job Search
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Find your next opportunity with our intelligent job search powered by LinkedIn data
          </p>
        </div>

        {/* Search Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            {/* Job Title */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-gray-700">
                Job Title *
              </label>
              <div className="relative">
                <Briefcase className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  value={searchParams.jobTitle}
                  onChange={(e) => handleInputChange('jobTitle', e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="e.g. Software Engineer"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                />
              </div>
            </div>

            {/* Location */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-gray-700">
                Location *
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  value={searchParams.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="e.g. San Francisco, CA"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                />
              </div>
            </div>

            {/* Date Posted */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-gray-700">
                Date Posted
              </label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <select
                  value={searchParams.datePosted}
                  onChange={(e) => handleInputChange('datePosted', e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 appearance-none bg-white"
                >
                  {dateOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Number of Results */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-gray-700">
                Number of Jobs
              </label>
              <div className="relative">
                <Hash className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="number"
                  min="1"
                  max="500"
                  value={searchParams.resultsCount}
                  onChange={(e) => handleInputChange('resultsCount', e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="e.g. 20"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                />
              </div>
            </div>
          </div>

          {/* Proxy Toggle */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Globe className="h-5 w-5 text-gray-600" />
                <span className="font-semibold text-gray-700">Use Proxy</span>
              </div>
              <button
                onClick={() => setUseProxy(!useProxy)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                  useProxy ? 'bg-blue-600' : 'bg-gray-300'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    useProxy ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
            
            {useProxy && (
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Proxy URL
                </label>
                <div className="relative">
                  <Settings className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    value={proxyUrl}
                    onChange={(e) => setProxyUrl(e.target.value)}
                    placeholder="http://proxy-server:port"
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Search Button */}
          <div className="text-center">
            <button
              onClick={handleSearch}
              disabled={isSearching}
              className={`inline-flex items-center space-x-3 px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-200 ${
                isSearching
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl'
              }`}
            >
              {isSearching ? (
                <>
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                  <span>Searching LinkedIn Jobs...</span>
                </>
              ) : (
                <>
                  <Search className="h-5 w-5" />
                  <span>Search Jobs</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Search Results */}
        {searchPerformed && (
          <div className="space-y-6">
            {jobs.length > 0 ? (
              <>
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                  <div className="flex items-center space-x-4">
                    <h2 className="text-2xl font-bold text-gray-900">
                      Search Results ({jobs.length} jobs found)
                    </h2>
                    <div className="text-sm text-gray-600">
                      Showing results for "{searchParams.jobTitle}"
                      {searchParams.location && ` in ${searchParams.location}`}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={handleSelectAll}
                      className="inline-flex items-center space-x-2 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-all duration-200"
                    >
                      {selectedJobs.size === jobs.length ? (
                        <CheckSquare className="h-4 w-4" />
                      ) : (
                        <Square className="h-4 w-4" />
                      )}
                      <span>
                        {selectedJobs.size === jobs.length ? 'Deselect All' : 'Select All'}
                      </span>
                    </button>
                  </div>
                </div>

                {/* Top Tailor Button */}
                <div className="text-center">
                  <TailorButton />
                </div>
                
                <div className="grid grid-cols-1 gap-6">
                  {jobs.map(job => (
                    <JobCard 
                      key={job.id} 
                      job={job} 
                      onClick={() => handleJobClick(job)}
                      isSelected={selectedJobs.has(job.id)}
                      onSelectionChange={handleJobSelection}
                    />
                  ))}
                </div>

                {/* Bottom Tailor Button */}
                <div className="text-center pt-6 border-t border-gray-200">
                  <TailorButton />
                </div>
              </>
            ) : !isSearching ? (
              <div className="text-center py-12">
                <div className="bg-white rounded-lg shadow-md p-8">
                  <Search className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">No jobs found</h3>
                  <p className="text-gray-600">
                    Try adjusting your search criteria or search terms
                  </p>
                </div>
              </div>
            ) : null}
          </div>
        )}
      </div>

      {/* Job Details Modal */}
      {selectedJob && (
        <JobDetailsModal
          job={selectedJob}
          isOpen={isModalOpen}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};