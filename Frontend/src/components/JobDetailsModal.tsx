import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  X, 
  Building, 
  MapPin, 
  Clock, 
  Users, 
  ExternalLink, 
  Briefcase, 
  DollarSign,
  Calendar,
  Star,
  Share2,
  Bookmark,
  Target
} from 'lucide-react';

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
  companySize?: string;
  industry?: string;
  skills?: string;
}

interface JobDetailsModalProps {
  job: Job;
  isOpen: boolean;
  onClose: () => void;
}

export const JobDetailsModal: React.FC<JobDetailsModalProps> = ({ job, isOpen, onClose }) => {
  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleApplyClick = () => {
    window.open(job.linkedinUrl, '_blank');
  };

  const skillList = job.skills ? job.skills.split(',').map(s => s.trim()).filter(s => s) : [];

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 flex-shrink-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-4 mb-4">
                {job.companyLogo && (
                  <img 
                    src={job.companyLogo} 
                    alt={`${job.company} logo`}
                    className="w-16 h-16 rounded-lg bg-white p-2"
                  />
                )}
                <div>
                  <h2 className="text-2xl font-bold mb-2">{job.title}</h2>
                  <div className="flex items-center space-x-2 text-blue-100">
                    <Building className="h-5 w-5" />
                    <span className="text-lg font-medium">{job.company}</span>
                  </div>
                </div>
              </div>
              
              <div className="flex flex-wrap items-center gap-4 text-sm text-blue-100">
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
            </div>
            
            <button
              onClick={onClose}
              className="p-2 hover:bg-white hover:bg-opacity-20 rounded-full transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="overflow-y-auto flex-grow">
          <div className="p-6 space-y-8">
            {/* Quick Info */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-blue-600 mb-1">{job.experienceLevel}</div>
                <div className="text-sm text-gray-600">Experience Level</div>
              </div>
              {job.salary && (
                <div className="bg-green-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-green-600 mb-1">{job.salary}</div>
                  <div className="text-sm text-gray-600">Salary Range</div>
                </div>
              )}
              {job.companySize && (
                <div className="bg-purple-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-purple-600 mb-1">{job.companySize}</div>
                  <div className="text-sm text-gray-600">Company Size</div>
                </div>
              )}
            </div>

            {/* Job Description */}
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Job Details</h3>
              <div className="prose prose-gray max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{job.description}</ReactMarkdown>
              </div>
            </div>

            {/* Skills */}
            {skillList.length > 0 && (
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">Required Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {skillList.map((skill, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800 hover:bg-gray-200 transition-colors"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Company Info */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">About {job.company}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                {job.industry && (
                  <div>
                    <span className="text-sm font-medium text-gray-500">Industry</span>
                    <p className="text-gray-900">{job.industry}</p>
                  </div>
                )}
                {job.companySize && (
                  <div>
                    <span className="text-sm font-medium text-gray-500">Company Size</span>
                    <p className="text-gray-900">{job.companySize}</p>
                  </div>
                )}
              </div>
              <p className="text-gray-700 leading-relaxed">
                Join our innovative team and help shape the future of technology. We're committed to creating 
                an inclusive environment where everyone can thrive and make a meaningful impact.
              </p>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="border-t border-gray-200 p-6 bg-gray-50 flex-shrink-0">
          <div className="flex flex-col sm:flex-row gap-3 justify-between items-center">
            <div className="flex space-x-3">
              <button className="inline-flex items-center space-x-2 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-all duration-200">
                <Bookmark className="h-4 w-4" />
                <span>Save Job</span>
              </button>
              <button className="inline-flex items-center space-x-2 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-all duration-200">
                <Share2 className="h-4 w-4" />
                <span>Share</span>
              </button>
            </div>
            
            <div className="flex space-x-3">
              <button className="inline-flex items-center space-x-2 px-6 py-3 border border-blue-300 text-blue-600 font-semibold rounded-lg hover:bg-blue-50 hover:border-blue-400 transition-all duration-200">
                <Target className="h-4 w-4" />
                <span>Tailor Resume</span>
              </button>
              <button
                onClick={handleApplyClick}
                className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-200"
              >
                <span>Apply on LinkedIn</span>
                <ExternalLink className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};