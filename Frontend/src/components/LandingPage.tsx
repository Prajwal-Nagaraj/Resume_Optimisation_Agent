import React, { useState } from 'react';
import { FileUpload } from './FileUpload';
import { Zap, Brain, Target, CheckCircle, ArrowRight, Github, Heart, Users, Code } from 'lucide-react';

interface LandingPageProps {
  onFileUpload: (file: File, resumeId: string) => void;
  uploadedFile: File | null;
  onExtractDetails: () => void;
  isExtracting: boolean;
}

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Analysis',
    description: 'Advanced AI analyzes your resume and identifies key strengths and areas for improvement.'
  },
  {
    icon: Target,
    title: 'Job-Specific Tailoring',
    description: 'Automatically customize your resume for each job application to maximize your chances.'
  },
  {
    icon: Zap,
    title: 'Instant Optimization',
    description: 'Get real-time suggestions and improvements to make your resume stand out.'
  },
  {
    icon: CheckCircle,
    title: 'ATS Optimization',
    description: 'Ensure your resume passes through Applicant Tracking Systems with confidence.'
  }
];

export const LandingPage: React.FC<LandingPageProps> = ({ 
  onFileUpload, 
  uploadedFile, 
  onExtractDetails, 
  isExtracting 
}) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
          <div className="text-center">
            <div className="mb-6">
              <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-green-100 text-green-800">
                <Heart className="h-4 w-4 mr-2" />
                Open Source
              </span>
            </div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Transform Your Resume with
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> AI Power</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed">
              A free, open-source resume tailoring tool powered by AI. 
              Upload your resume and let our intelligent system optimize it for any job opportunity.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <a
                href="https://github.com/Prajwal-Nagaraj/Resume_Optimisation_Agent"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-2 px-6 py-3 rounded-lg bg-gray-900 text-white hover:bg-gray-800 transition-colors duration-200"
              >
                <Github className="h-5 w-5" />
                <span>View on GitHub</span>
              </a>
              <a
                href="https://github.com/Prajwal-Nagaraj/Resume_Optimisation_Agent/stargazers"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-2 px-6 py-3 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors duration-200"
              >
                <span>⭐ Star us on GitHub</span>
              </a>
            </div>
            
            {/* Upload Section */}
            <div className="mb-8">
              <FileUpload onFileUpload={onFileUpload} />
            </div>

            {/* Extract Details Button */}
            {uploadedFile && (
              <div className="mb-16">
                <button
                  onClick={onExtractDetails}
                  disabled={isExtracting}
                  className={`inline-flex items-center space-x-3 px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-200 ${
                    isExtracting
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl'
                  }`}
                >
                  {isExtracting ? (
                    <>
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                      <span>Extracting Resume Details...</span>
                    </>
                  ) : (
                    <>
                      <span>Extract Resume Details</span>
                      <ArrowRight className="h-5 w-5" />
                    </>
                  )}
                </button>
              </div>
            )}
            
            {/* Community Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto mb-16">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">100%</div>
                <div className="text-gray-600">Free & Open Source</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">Community</div>
                <div className="text-gray-600">Driven Development</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">MIT</div>
                <div className="text-gray-600">License</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why Choose Resume Tailor?
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Built by the community, for the community. Our open-source platform combines 
              cutting-edge AI technology with transparency and collaboration.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="text-center p-6 rounded-xl hover:shadow-lg transition-all duration-300 group hover:scale-105"
                >
                  <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-3 rounded-full w-16 h-16 mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Icon className="h-10 w-10 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Open Source Benefits */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Open Source Benefits
            </h2>
            <p className="text-lg text-gray-600">
              Why open source matters for your resume optimization
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Code className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Transparency</h3>
              <p className="text-gray-600">
                Review the code, understand how your data is processed, and contribute improvements
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Users className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Community</h3>
              <p className="text-gray-600">
                Join a community of developers and job seekers working together to improve the tool
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Heart className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Free Forever</h3>
              <p className="text-gray-600">
                No hidden costs, no premium features - everything is free and open to everyone
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* How it Works */}
      <div className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                      <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                How It Works
              </h2>
              <p className="text-lg text-gray-600">
                Four simple steps to transform your resume
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                          <div className="text-center">
                <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-blue-600">1</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Upload Resume</h3>
                <p className="text-gray-600">
                  Upload your current resume in PDF or Word format
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-purple-600">2</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Extract Details</h3>
                <p className="text-gray-600">
                  Our AI extracts and analyzes your resume details
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-green-600">3</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Search Jobs</h3>
                <p className="text-gray-600">
                  Search and choose the jobs that match your interests
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-orange-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-orange-600">4</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Download Resume</h3>
                <p className="text-gray-600">
                  Download your tailored resume optimized for each job
                </p>
              </div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="py-16 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to contribute?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Help us make Resume Tailor even better. Star the project, report issues, or submit pull requests.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="https://github.com/Prajwal-Nagaraj/Resume_Optimisation_Agent"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-2 px-8 py-4 rounded-lg bg-white text-blue-600 hover:bg-gray-100 transition-colors duration-200 font-semibold"
            >
              <Github className="h-5 w-5" />
              <span>Contribute on GitHub</span>
            </a>
            <a
              href="https://github.com/Prajwal-Nagaraj/Resume_Optimisation_Agent/issues"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-2 px-8 py-4 rounded-lg border-2 border-white text-white hover:bg-white hover:text-blue-600 transition-colors duration-200 font-semibold"
            >
              <span>Report Issues</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};