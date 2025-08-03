# Resume Tailor

A powerful AI-driven application that automatically tailors your resume for specific job opportunities. Upload your resume, search for jobs, and get perfectly customized resumes optimized for each position.

## 🚀 Features

### Core Functionality
- **Smart Resume Parsing**: Extract and analyze resume content using AI agents
- **Job Search Integration**: Search and browse job opportunities with detailed filtering
- **AI-Powered Tailoring**: Automatically customize resumes for specific job requirements
- **Bulk Processing**: Tailor multiple resumes simultaneously for different positions
- **Progress Tracking**: Real-time progress monitoring for tailoring operations
- **PDF Generation**: Generate professional PDF resumes with optimized formatting

### User Experience
- **Modern UI/UX**: Clean, responsive interface built with React and Tailwind CSS
- **Interactive Job Cards**: Detailed job information with company logos and metadata
- **Real-time Updates**: Live progress tracking with status indicators


## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Modern ES6+** features

### Backend
- **Python 3.8+**
- **Flask/FastAPI** for API endpoints
- **AI Agents** for resume parsing and tailoring
- **PDF Generation** libraries
- **Job Scraping** capabilities
- **Static file serving**

## 🔨 Built with

This project is built with the help of these amazing libraries and tools:

- **[Agno](https://github.com/agno-agi/agno)** - AI Agentic Framework
- **[Jobspy](https://github.com/speedyapply/JobSpy)** - Job search and scraping functionality

## 📦 Installation

### Prerequisites
- Node.js 16+ and npm/yarn
- Python 3.10+
- Gemini API key (get it from [Google AI Studio](https://aistudio.google.com/apikey))


### Backend Setup

1. **Clone the repository**
   ```
   git clone <repository-url>
   cd Resume_Tailor_Frontend
   ```

2. **Navigate to backend directory**
   ```
   cd Backend
   ```

3. **Create virtual environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

5. **Run the backend server**
   ```
   python main.py
   ```

The backend server will start on `http://localhost:5000` (or configured port).

### Frontend Setup

1. **Navigate to frontend directory**
   ```
   cd Frontend
   ```

2. **Install dependencies**
   ```
   npm install
   # or
   yarn install
   ```

3. **Start development server**
   ```
   npm run dev
   # or
   yarn dev
   ```

The frontend will start on `http://localhost:5173`.

## 🎯 Usage

### Getting Started

1. **Launch the Application**
   - Start both backend and frontend servers
   - Open your browser to `http://localhost:5173`

2. **Upload Your Resume**
   - Click on "Upload Resume" or drag and drop your PDF/DOC file
   - Wait for the AI to parse and analyze your resume

3. **Search for Jobs**
   - Use the job search feature to find relevant positions
   - Filter by location, company, experience level, etc.
   - Browse through job cards with detailed information

4. **Select Jobs for Tailoring**
   - Select multiple jobs you want to apply for
   - Review job details and requirements
   - Proceed to tailoring process

5. **Monitor Progress**
   - Watch real-time progress as AI tailors your resume
   - Track individual job progress and overall completion
   - View processing times and status updates

6. **Download Tailored Resumes**
   - Download individual tailored resumes as they complete
   - Use "Download All" for bulk downloading
   - Each resume is optimized for specific job requirements

### Advanced Features

- **Batch Processing**: Select up to 10+ jobs for simultaneous tailoring
- **Resume Optimization**: AI analyzes job descriptions and optimizes content
- **Professional Formatting**: Maintains clean, ATS-friendly formatting
- **Progress Tracking**: Real-time updates with detailed status information

## 📁 Project Structure

```
Resume_Tailor_Frontend/
├── Backend/                          # Python backend application
│   ├── jobs_scraper.py              # Job scraping functionality
│   ├── main.py                      # Main Flask/FastAPI application
│   ├── pdf_generator_simple.py     # PDF generation utilities
│   ├── resume_parser_agent.py      # AI resume parsing agent
│   ├── resume_tailor_agent.py      # AI resume tailoring agent
│   ├── requirements.txt             # Python dependencies
│   ├── static/                      # Static files and CSS
│   ├── tailored_resumes/           # Generated resume outputs
│   ├── templates/                   # HTML templates
│   └── test_output/                # Test files and outputs
│
├── Frontend/                        # React TypeScript frontend
│   ├── src/
│   │   ├── components/             # React components
│   │   │   ├── FileUpload.tsx      # Resume upload component
│   │   │   ├── JobCard.tsx         # Job display card
│   │   │   ├── JobDetailsModal.tsx # Job details modal
│   │   │   ├── JobSearch.tsx       # Job search interface
│   │   │   ├── LandingPage.tsx     # Landing page component
│   │   │   ├── Navigation.tsx      # Navigation bar
│   │   │   ├── ResumeDetails.tsx   # Resume details view
│   │   │   └── ResumeTailoring.tsx # Tailoring progress page
│   │   ├── types/                  # TypeScript type definitions
│   │   ├── App.tsx                 # Main app component
│   │   ├── main.tsx                # App entry point
│   │   └── index.css               # Global styles
│   ├── resumes/                    # Resume storage directory
│   ├── index.html                  # HTML template
│   ├── package.json               # Node.js dependencies
│   ├── tailwind.config.js         # Tailwind CSS configuration
│   ├── vite.config.ts             # Vite configuration
│   └── postcss.config.js          # PostCSS configuration
│
└── README.md                       # Project documentation
```

## 🔧 Configuration

### Backend Configuration
- Update API endpoints in `main.py`
- Configure AI agent parameters in respective agent files
- Set up environment variables for API keys and settings

### Frontend Configuration
- Update API base URL in the frontend configuration
- Modify Tailwind CSS theme in `tailwind.config.js`
- Configure Vite settings in `vite.config.ts`

## 🧪 Development

### Running Tests
```
# Backend tests
cd Backend
python -m pytest

# Frontend tests
cd Frontend
npm test
```

## 📚 API Documentation

### Key Endpoints

- `POST /api/upload-resume` - Upload and parse resume
- `GET /api/jobs/search` - Search for jobs
- `POST /api/tailor-resume` - Tailor resume for specific job
- `GET /api/download-resume/:id` - Download tailored resume
- `GET /api/jobs/:id` - Get job details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Built with ❤️ for job seekers everywhere** 