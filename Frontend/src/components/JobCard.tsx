import React from 'react';
import { Building, MapPin, Clock, Users, ExternalLink, Briefcase, DollarSign } from 'lucide-react';

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

interface JobCardProps {
  job: Job;
  onClick: () => void;
  isSelected: boolean;
  onSelectionChange: (jobId: string, selected: boolean) => void;
}

export const JobCard: React.FC<JobCardProps> = ({ job, onClick, isSelected, onSelectionChange }) => {
  const handleApplyClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    window.open(job.linkedinUrl, '_blank');
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.stopPropagation();
    onSelectionChange(job.id, e.target.checked);
  };

  const truncateDescription = (text: string, maxLength: number = 200) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div 
      className={`bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border group cursor-pointer ${
        isSelected 
          ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' 
          : 'border-gray-100 hover:border-blue-200'
      }`}
      onClick={onClick}
    >
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
        {/* Selection Checkbox */}
        <div className="flex items-start space-x-4 flex-1">
          <div className="flex items-center pt-1">
            <input
              type="checkbox"
              checked={isSelected}
              onChange={handleCheckboxChange}
              className="w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 cursor-pointer"
              onClick={(e) => e.stopPropagation()}
            />
          </div>

          {/* Main Content */}
          <div className="flex-1 space-y-4">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="space-y-2">
                <h3 className="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors duration-200">
                  {job.title}
                </h3>
                <div className="flex items-center space-x-2 text-gray-600">
                  <Building className="h-4 w-4" />
                  <span className="font-medium">{job.company}</span>
                </div>
              </div>
              {job.companyLogo && (
                <img 
                  src={job.companyLogo} 
                  alt={`${job.company} logo`}
                  className="w-12 h-12 rounded-lg object-cover"
                />
              )}
            </div>

            {/* Job Details */}
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <MapPin className="h-4 w-4" />
                <span>{job.location}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Clock className="h-4 w-4" />
                <span>{job.postedDate}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Briefcase className="h-4 w-4" />
                <span>{job.employmentType}</span>
              </div>
              {job.applicants && (
                <div className="flex items-center space-x-1">
                  <Users className="h-4 w-4" />
                  <span>{job.applicants} applicants</span>
                </div>
              )}
            </div>

            {/* Experience Level & Salary */}
            <div className="flex flex-wrap items-center gap-3">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {job.experienceLevel}
              </span>
              {job.salary && (
                <span className="inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  <DollarSign className="h-3 w-3" />
                  <span>{job.salary}</span>
                </span>
              )}
            </div>

            {/* Description */}
            <div className="space-y-2">
              <p className="text-gray-700 leading-relaxed">
                {truncateDescription(job.description)}
              </p>
              <button className="text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors">
                View full details →
              </button>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col space-y-3 lg:min-w-[200px]">
          <button
            onClick={handleApplyClick}
            className="inline-flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-200"
          >
            <span>Apply on LinkedIn</span>
            <ExternalLink className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};