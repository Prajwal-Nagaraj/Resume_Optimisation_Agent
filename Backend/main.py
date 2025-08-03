import asyncio
import os
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Query, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
# Import existing modules
from jobs_scraper import SpeedyApplyTool
from resume_parser_agent import parse_resume_raw_json
from resume_tailor_agent import tailor_resume as tailor_resume_with_ai
from pdf_generator import ResumePDFGenerator

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ResumeTailor API",
    description="API for job search, resume parsing, and automated resume tailoring",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize tools and agents
job_scraper = SpeedyApplyTool()
pdf_generator = ResumePDFGenerator()

# Storage directories
UPLOAD_DIR = Path("uploads")
TAILORED_RESUMES_DIR = Path("tailored_resumes")
UPLOAD_DIR.mkdir(exist_ok=True)
TAILORED_RESUMES_DIR.mkdir(exist_ok=True)

resume_storage: Dict[str, Dict] = {}
extraction_status: Dict[str, Dict] = {}
tailoring_jobs: Dict[str, Dict] = {}

# Pydantic models for API requests/responses
class JobSearchResponse(BaseModel):
    jobs: List[Dict[str, Any]]
    total_count: int
    search_term: str
    location: str

class UploadResponse(BaseModel):
    resume_id: str
    filename: str
    message: str

class ExtractionStatusResponse(BaseModel):
    resume_id: str
    status: str  # "pending", "processing", "completed", "failed"
    extracted_data: Optional[Dict] = None
    error_message: Optional[str] = None

class TailorRequest(BaseModel):
    resume_id: str
    job_descriptions: List[Dict[str, str]]  # List of objects with description and company

class TailorResponse(BaseModel):
    task_id: str
    message: str
    status: str

class IndividualJobStatus(BaseModel):
    job_index: int
    job_title: str
    company: str
    status: str  # "pending", "processing", "completed", "failed"
    progress_message: Optional[str] = None
    error_message: Optional[str] = None
    tailored_resume: Optional[Dict] = None
    download_links: Optional[Dict] = None

class TailorStatusResponse(BaseModel):
    task_id: str
    overall_status: str  # "pending", "processing", "completed", "failed"
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    individual_jobs: List[IndividualJobStatus]
    error_message: Optional[str] = None

class UpdatedResume(BaseModel):
    data: Dict[str, Any]

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ResumeTailor API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search",
            "upload": "/api/upload", 
            "extract": "/api/extract/{resume_id}",
            "tailor": "/api/tailor",
            "download": "/api/download/{file_key}",
            "download_pdf": "/api/download/{file_key}/pdf"
        }
    }

@app.get("/api/search", response_model=JobSearchResponse)
async def search_jobs(
    query: str = Query(..., description="Job search keywords"),
    location: str = Query(..., description="Job location"),
    limit: int = Query(20, description="Maximum number of results"),
    proxy: Optional[str] = Query(None, description="Proxy URL to use for scraping")
):
    """
    Search for job listings using the job scraper
    """
    try:
        # Use the existing job scraper to get DataFrame directly
        jobs_df = job_scraper.find_and_save_jobs(search_term=query, location=location, proxy_url=proxy)
        
        if jobs_df is None or jobs_df.empty:
            raise HTTPException(status_code=404, detail="No jobs found or scraping failed")
        
        # Convert DataFrame to list of dictionaries and limit results
        jobs_list = jobs_df.head(limit).to_dict('records')
        
        return JobSearchResponse(
            jobs=jobs_list,
            total_count=len(jobs_list),
            search_term=query,
            location=location
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job search failed: {str(e)}")

@app.post("/api/upload", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF or DOCX)
    """
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.doc']
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not supported. Allowed types: {allowed_extensions}"
        )
    
    # Generate unique resume ID
    resume_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{resume_id}_{file.filename}"
    
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Store resume metadata
        resume_storage[resume_id] = {
            "filename": file.filename,
            "file_path": str(file_path),
            "upload_time": datetime.now().isoformat(),
            "status": "uploaded"
        }
        
        # Initialize extraction status
        extraction_status[resume_id] = {
            "status": "pending",
            "extracted_data": None,
            "error_message": None
        }
        
        return UploadResponse(
            resume_id=resume_id,
            filename=file.filename,
            message="Resume uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.post("/api/extract/{resume_id}", response_model=ExtractionStatusResponse)
async def extract_resume_data(resume_id: str, background_tasks: BackgroundTasks):
    """
    Start resume data extraction process
    """
    if resume_id not in resume_storage:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if resume_id not in extraction_status:
        extraction_status[resume_id] = {
            "status": "pending",
            "extracted_data": None,
            "error_message": None
        }
    
    # Start background extraction task
    background_tasks.add_task(perform_extraction, resume_id)
    
    # Update status to processing
    extraction_status[resume_id]["status"] = "processing"
    
    return ExtractionStatusResponse(
        resume_id=resume_id,
        status="processing",
        extracted_data=None,
        error_message=None
    )

@app.get("/api/extract/{resume_id}/status", response_model=ExtractionStatusResponse)
async def get_extraction_status(resume_id: str):
    """
    Get the status of resume extraction
    """
    if resume_id not in extraction_status:
        raise HTTPException(status_code=404, detail="Extraction status not found")
    
    status_data = extraction_status[resume_id]
    
    return ExtractionStatusResponse(
        resume_id=resume_id,
        status=status_data["status"],
        extracted_data=status_data["extracted_data"],
        error_message=status_data["error_message"]
    )

@app.put("/api/resume/{resume_id}")
async def update_resume_data(resume_id: str, updated_data: Dict[str, Any]):
    """
    Update extracted resume data
    """
    if resume_id not in extraction_status:
        raise HTTPException(status_code=404, detail="Resume not found")

    if extraction_status[resume_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Resume extraction not complete, cannot update.")

    extraction_status[resume_id]["extracted_data"] = updated_data
    
    return {"message": "Resume data updated successfully"}

@app.post("/api/tailor", response_model=TailorResponse)
async def tailor_resume(request: TailorRequest, background_tasks: BackgroundTasks):
    """
    Submit resume and job descriptions for tailoring
    """
    # Validate resume exists and is extracted
    if request.resume_id not in resume_storage:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if request.resume_id not in extraction_status:
        raise HTTPException(status_code=400, detail="Resume not extracted yet")
    
    if extraction_status[request.resume_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Resume extraction not completed")
    
    if not extraction_status[request.resume_id]["extracted_data"]:
        raise HTTPException(status_code=400, detail="No extracted resume data available")
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Initialize tailoring job with individual job tracking
    individual_jobs = []
    for i, job_desc in enumerate(request.job_descriptions):
        individual_jobs.append({
            "job_index": i,
            "job_title": job_desc.get("title", "Unknown Title"),
            "company": job_desc.get("company", "Unknown Company"),
            "status": "pending",
            "progress_message": None,
            "error_message": None,
            "tailored_resume": None,
            "download_links": None
        })
    
    tailoring_jobs[task_id] = {
        "resume_id": request.resume_id,
        "job_descriptions": request.job_descriptions,
        "status": "pending",
        "individual_jobs": individual_jobs,
        "error_message": None,
        "created_at": datetime.now().isoformat()
    }
    
    # Start background tailoring task
    background_tasks.add_task(perform_tailoring, task_id)
    
    return TailorResponse(
        task_id=task_id,
        message="Resume tailoring started",
        status="processing"
    )

@app.get("/api/tailor/{task_id}/status", response_model=TailorStatusResponse)
async def get_tailoring_status(task_id: str):
    """
    Get the status of resume tailoring
    """
    if task_id not in tailoring_jobs:
        raise HTTPException(status_code=404, detail="Tailoring task not found")
    
    job_data = tailoring_jobs[task_id]
    
    # Calculate completed and failed jobs
    completed_jobs = sum(1 for job in job_data["individual_jobs"] if job["status"] == "completed")
    failed_jobs = sum(1 for job in job_data["individual_jobs"] if job["status"] == "failed")
    
    # Convert individual jobs to IndividualJobStatus objects
    individual_jobs = [
        IndividualJobStatus(
            job_index=job["job_index"],
            job_title=job["job_title"],
            company=job["company"],
            status=job["status"],
            progress_message=job["progress_message"],
            error_message=job["error_message"],
            tailored_resume=job["tailored_resume"],
            download_links=job["download_links"]
        )
        for job in job_data["individual_jobs"]
    ]
    
    return TailorStatusResponse(
        task_id=task_id,
        overall_status=job_data["status"],
        total_jobs=len(job_data["job_descriptions"]),
        completed_jobs=completed_jobs,
        failed_jobs=failed_jobs,
        individual_jobs=individual_jobs,
        error_message=job_data["error_message"]
    )

@app.get("/api/download/{file_key}")
async def download_tailored_resume(file_key: str):
    """
    Download a tailored resume file (JSON or PDF)
    """
    file_path = TAILORED_RESUMES_DIR / file_key
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on file extension
    if file_key.endswith('.pdf'):
        media_type = 'application/pdf'
    elif file_key.endswith('.json'):
        media_type = 'application/json'
    else:
        media_type = 'application/octet-stream'
    
    return FileResponse(
        path=file_path,
        filename=file_key,
        media_type=media_type
    )

@app.get("/api/download/{file_key}/pdf")
async def download_tailored_resume_pdf(file_key: str):
    """
    Download a tailored resume as PDF (converts from JSON if needed)
    """
    # Remove .json extension if present and add .pdf
    base_name = file_key.replace('.json', '')
    pdf_file_key = f"{base_name}.pdf"
    json_file_key = f"{base_name}.json"
    
    pdf_path = TAILORED_RESUMES_DIR / pdf_file_key
    json_path = TAILORED_RESUMES_DIR / json_file_key
    
    # If PDF exists, return it
    if pdf_path.exists():
        return FileResponse(
            path=pdf_path,
            filename=pdf_file_key,
            media_type='application/pdf'
        )
    
    # If JSON exists, convert to PDF
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                resume_data = json.load(f)
            
            # Generate PDF
            if pdf_generator.generate_pdf(resume_data, str(pdf_path)):
                return FileResponse(
                    path=pdf_path,
                    filename=pdf_file_key,
                    media_type='application/pdf'
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to generate PDF")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
    
    raise HTTPException(status_code=404, detail="Resume file not found")

# Background task functions

async def perform_extraction(resume_id: str):
    """
    Background task to extract resume data
    """
    try:
        resume_data = resume_storage[resume_id]
        file_path = resume_data["file_path"]
        
            # Fallback to raw JSON parsing
        extracted_data = await parse_resume_raw_json(file_path)
        
        if extracted_data:
            # Check if the response contains an API key error
            if isinstance(extracted_data, dict) and extracted_data.get("error") == "api_key_invalid":
                extraction_status[resume_id] = {
                    "status": "failed",
                    "extracted_data": None,
                    "error_message": f"API Key Error: {extracted_data.get('error_message', 'Invalid or missing API key')}"
                }
            else:
                extraction_status[resume_id] = {
                    "status": "completed",
                    "extracted_data": extracted_data,
                    "error_message": None
                }
        else:
            extraction_status[resume_id] = {
                "status": "failed",
                "extracted_data": None,
                "error_message": "Failed to extract resume data"
            }
            
    except Exception as e:
        extraction_status[resume_id] = {
            "status": "failed",
            "extracted_data": None,
            "error_message": str(e)
        }

async def perform_tailoring(task_id: str):
    """
    Background task to tailor resumes for multiple jobs with individual job tracking
    """
    try:
        job_data = tailoring_jobs[task_id]
        resume_id = job_data["resume_id"]
        job_descriptions = job_data["job_descriptions"]
        
        # Update overall status to processing
        tailoring_jobs[task_id]["status"] = "processing"
        
        # Get extracted resume data
        resume_data = extraction_status[resume_id]["extracted_data"]
        
        # Process each job individually with real-time updates
        for i, job_desc_data in enumerate(job_descriptions):
            try:
                # Update individual job status to processing
                tailoring_jobs[task_id]["individual_jobs"][i]["status"] = "processing"
                tailoring_jobs[task_id]["individual_jobs"][i]["progress_message"] = "Starting resume tailoring..."
                
                # Create enhanced job context with all available fields
                job_context = {
                    "title": job_desc_data.get("title", ""),
                    "company": job_desc_data.get("company", ""),
                    "location": job_desc_data.get("location", ""),
                    "job_level": job_desc_data.get("job_level", ""),
                    "job_function": job_desc_data.get("job_function", ""),
                    "company_industry": job_desc_data.get("company_industry", ""),
                    "description": job_desc_data.get("description", ""),
                    "skills": job_desc_data.get("skills", ""),
                    "experience_range": job_desc_data.get("experience_range", ""),
                    "is_remote": job_desc_data.get("is_remote", False),
                    "job_type": job_desc_data.get("job_type", ""),
                    "company_description": job_desc_data.get("company_description", ""),
                    "company_num_employees": job_desc_data.get("company_num_employees", ""),
                    "min_amount": job_desc_data.get("min_amount", ""),
                    "max_amount": job_desc_data.get("max_amount", ""),
                    "currency": job_desc_data.get("currency", "")
                }
                
                # Update progress message
                tailoring_jobs[task_id]["individual_jobs"][i]["progress_message"] = "Tailoring resume with AI..."
                
                # Tailor resume for this job with enhanced context
                tailored_content = await tailor_resume_with_ai(resume_data, job_context)
                
                if tailored_content:
                    # Update progress message
                    tailoring_jobs[task_id]["individual_jobs"][i]["progress_message"] = "Converting to dictionary format..."
                    
                    # Convert Pydantic model to dict for JSON serialization and PDF generation
                    tailored_dict = tailored_content.model_dump()
                    
                    # Update progress message
                    tailoring_jobs[task_id]["individual_jobs"][i]["progress_message"] = "Generating filenames..."
                    
                    # Generate filename for tailored resume
                    safe_company = "".join(c for c in job_desc_data.get("company", "Unknown") if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_title = "".join(c for c in job_desc_data.get("title", "Unknown") if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    base_filename = f"{resume_id}_{safe_company}_{safe_title}_{i}"
                    json_filename = f"{base_filename}.json"
                    pdf_filename = f"{base_filename}.pdf"
                    
                    # Update progress message
                    tailoring_jobs[task_id]["individual_jobs"][i]["progress_message"] = "Saving JSON file..."
                    
                    # Save tailored resume as JSON
                    json_file_path = TAILORED_RESUMES_DIR / json_filename
                    with open(json_file_path, 'w', encoding='utf-8') as f:
                        json.dump(tailored_dict, f, indent=2)
                    
                    # Update progress message
                    tailoring_jobs[task_id]["individual_jobs"][i]["progress_message"] = "Generating PDF..."
                    
                    # Generate PDF version
                    pdf_file_path = TAILORED_RESUMES_DIR / pdf_filename
                    pdf_generated = pdf_generator.generate_pdf(tailored_dict, str(pdf_file_path))
                    
                    # Update progress message
                    tailoring_jobs[task_id]["individual_jobs"][i]["progress_message"] = "Creating download links..."
                    
                    # Create download links
                    download_links = {
                        "json": f"/api/download/{json_filename}",
                        "pdf": f"/api/download/{pdf_filename}" if pdf_generated else f"/api/download/{json_filename}/pdf"
                    }
                    
                    # Update individual job as completed
                    tailoring_jobs[task_id]["individual_jobs"][i].update({
                        "status": "completed",
                        "progress_message": "Resume tailored successfully!",
                        "tailored_resume": tailored_dict,
                        "download_links": download_links,
                        "error_message": None
                    })
                    
                else:
                    # Update individual job as failed
                    tailoring_jobs[task_id]["individual_jobs"][i].update({
                        "status": "failed",
                        "progress_message": None,
                        "tailored_resume": None,
                        "download_links": None,
                        "error_message": "Failed to generate tailored content"
                    })
                
            except Exception as e:
                print(f"Error tailoring resume for job {i}: {e}")
                # Update individual job as failed
                tailoring_jobs[task_id]["individual_jobs"][i].update({
                    "status": "failed",
                    "progress_message": None,
                    "tailored_resume": None,
                    "download_links": None,
                    "error_message": str(e)
                })
                continue
        
        # Check overall completion status
        completed_count = sum(1 for job in tailoring_jobs[task_id]["individual_jobs"] if job["status"] == "completed")
        failed_count = sum(1 for job in tailoring_jobs[task_id]["individual_jobs"] if job["status"] == "failed")
        total_count = len(tailoring_jobs[task_id]["individual_jobs"])
        
        if completed_count > 0:
            # At least one job completed successfully
            if completed_count == total_count:
                # All jobs completed successfully
                tailoring_jobs[task_id]["status"] = "completed"
            else:
                # Some jobs completed, some failed
                tailoring_jobs[task_id]["status"] = "completed"
                tailoring_jobs[task_id]["error_message"] = f"{completed_count} out of {total_count} jobs completed successfully. {failed_count} jobs failed."
        else:
            # All jobs failed
            tailoring_jobs[task_id]["status"] = "failed"
            tailoring_jobs[task_id]["error_message"] = "All jobs failed to process"
            
    except Exception as e:
        tailoring_jobs[task_id].update({
            "status": "failed",
            "error_message": str(e)
        })

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# API key validation endpoint
@app.get("/api/validate-key")
async def validate_api_key():
    """Validate the Gemini API key"""
    from resume_parser_agent import validate_gemini_api_key
    
    try:
        validation_result = await validate_gemini_api_key()
        return {
            "valid": validation_result["valid"],
            "error_message": validation_result.get("error"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "valid": False,
            "error_message": f"Validation failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 