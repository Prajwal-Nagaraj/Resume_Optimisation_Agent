import asyncio
import os
from typing import List, Optional, Dict, Union
from pathlib import Path
import json # Added for json.dumps
import docx # type: ignore
from pydantic import BaseModel, Field, validator
from textwrap import dedent
import google.generativeai as genai
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv

load_dotenv()

# Function to validate Gemini API key
async def validate_gemini_api_key() -> Dict[str, Union[bool, str]]:
    """
    Validates the Gemini API key by making a simple test request.
    
    Returns:
        Dict containing validation result and error message if any
    """
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return {
                "valid": False,
                "error": "GOOGLE_API_KEY not found in environment variables"
            }
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Create a simple model instance and make a test request
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content("Hello, this is a test message.")
        
        if response and response.text:
            return {
                "valid": True,
                "error": None
            }
        else:
            return {
                "valid": False,
                "error": "API key is invalid or has insufficient permissions"
            }
            
    except Exception as e:
        return {
            "valid": False,
            "error": f"API validation failed: {str(e)}"
        }

# Pydantic Models for Resume Parsing
class ContactInfo(BaseModel):
    name: Optional[str] = Field(None, description="Full name of the candidate")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    portfolio: Optional[str] = Field(None, description="Portfolio website URL")


class WorkExperience(BaseModel):
    company: str = Field(..., description="Company name")
    title: str = Field(..., description="Job title")
    start_date: str = Field(..., description="Starting Month and Year")
    end_date: Optional[str] = Field(None, description="Ending Month and Year or 'Present'")
    location: Optional[str] = Field(None, description="Job location")
    description: List[str] = Field(default_factory=list, description="List of responsibilities and achievements")
    

class Education(BaseModel):
    institution: str = Field(..., description="University or institution name")
    degree: str = Field(..., description="Degree type")
    major: Optional[str] = Field(None, description="Field of study")
    graduation_date: Optional[str] = Field(None, description="Year of graduation")
    gpa: Optional[str] = Field(None, description="GPA if mentioned")
    location: Optional[str] = Field(None, description="Institution location")
    

class Skills(BaseModel):
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks and libraries")
    databases: List[str] = Field(default_factory=list, description="Database systems")
    languages: List[str] = Field(default_factory=list, description="Spoken languages")
    soft_skills: List[str] = Field(default_factory=list, description="Soft skills")
    other: List[str] = Field(default_factory=list, description="Other skills not categorized above")

class Project(BaseModel):
    title: str = Field(..., description="Project name")
    description: List[str] = Field(default_factory=list, description="Complete project description and features")
    url: Optional[str] = Field(None, description="Project URL if available")
    technologies_used: List[str] = Field(default_factory=list, description="Technologies, frameworks, and tools used")

class Resume(BaseModel):
    contact_info: ContactInfo = Field(..., description="Contact information")
    summary: Optional[str] = Field(None, description="Professional summary or objective statement")
    work_experience: List[WorkExperience] = Field(default_factory=list, description="Work experience entries")
    education: List[Education] = Field(default_factory=list, description="Education entries")
    skills: Skills = Field(..., description="Skills organized by category")
    projects: List[Project] = Field(default_factory=list, description="Projects")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")
    awards_and_honors: List[str] = Field(default_factory=list, description="Awards, honors, and recognitions")
    languages: List[str] = Field(default_factory=list, description="Languages with proficiency levels")
    
    def to_dict(self) -> Dict:
        """Convert Resume object to dictionary"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Convert Resume object to JSON string"""
        return self.model_dump_json(indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Resume':
        """Create Resume object from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Resume':
        """Create Resume object from JSON string"""
        return cls.model_validate_json(json_str)

# Helper function to load resume text from DOCX
def load_resume_from_docx(file_path: str) -> str:
    """Loads text content from a .docx file."""
    try:
        doc = docx.Document(file_path)
        full_text = [para.text for para in doc.paragraphs]
        return "\\n".join(full_text)
    except Exception as e:
        print(f"Error loading resume from {file_path}: {e}")
        return ""

# Helper function to load resume text from PDF
def load_resume_from_pdf(file_path: str) -> str:
    """Loads text content from a .pdf file."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        full_text = []
        for page in doc:
            full_text.append(page.get_text())
        doc.close()
        return "\\n".join(full_text)
    except Exception as e:
        print(f"Error loading resume from {file_path}: {e}")
        return ""

# Helper function to load resume text from any supported format
def load_resume_text(file_path: str) -> str:
    """Loads text content from supported file formats."""
    file_extension = Path(file_path).suffix.lower()
    
    if file_extension == '.pdf':
        return load_resume_from_pdf(file_path)
    elif file_extension in ['.docx', '.doc']:
        return load_resume_from_docx(file_path)
    else:
        print(f"Unsupported file format: {file_extension}")
        return ""

# Initialize the Agno Agent for Resume Parsing with Pydantic validation
resume_parser_agent = Agent(
    model=Gemini("gemini-2.5-flash"),
    description="Parse resumes and extract structured information into JSON format",
    instructions=dedent("""\
        Parse the given resume text and extract all information into a structured JSON object.
        
        Return ONLY a valid JSON object with this structure:
        {
          "contact_info": {
            "name": "Full name",
            "email": "email@example.com", 
            "phone": "phone number",
            "linkedin": "LinkedIn URL",
            "github": "GitHub URL",
            "portfolio": "Portfolio URL"
          },
          "summary": "Professional summary",
          "work_experience": [
            {
              "company": "Company Name",
              "title": "Job Title", 
              "start_date": "YYYY-MM",
              "end_date": "YYYY-MM or Present",
              "location": "Job location",
              "description": ["responsibility 1", "responsibility 2"]
            }
          ],
          "education": [
            {
              "institution": "University Name",
              "degree": "Degree Type",
              "major": "Field of Study",
              "graduation_date": "YYYY-MM",
              "gpa": "GPA if mentioned",
              "location": "Institution location"
            }
          ],
          "skills": {
            "programming_languages": ["language1", "language2"],
            "frameworks": ["framework1", "framework2"],
            "databases": ["database1", "database2"],
            "languages": ["spoken language1", "spoken language2"],
            "soft_skills": ["skill1", "skill2"],
            "other": ["other skill1", "other skill2"]
          },
          "projects": [
            {
              "title": "Project Name",
              "description": ["description1", "description2"],
              "url": "Project URL if available",
              "technologies_used": ["tech1", "tech2"]
            }
          ],
          "certifications": ["cert1", "cert2"],
          "awards_and_honors": ["award1", "award2"],
          "languages": ["language1", "language2"]
        }
        
        Extract ALL information found in the resume. Use null for missing optional fields and empty arrays for missing lists.
        """),
    response_model=Resume,  # Use the Pydantic model for validation
    markdown=False,
    show_tool_calls=False,
)

def parse_json_response(response_text: str) -> Optional[Dict]:
    """
    Parse the agent's response and extract JSON content
    """
    import re
    
    # Remove any <think> tags and their content
    response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
    response_text = response_text.strip()
    
    try:
        # Try to parse the response directly as JSON
        return json.loads(response_text)
    except json.JSONDecodeError:
        # If direct parsing fails, try to extract JSON from the response
        try:
            # Try to find JSON block in markdown format
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try to find the largest JSON object in the text
            json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
            for match in sorted(json_matches, key=len, reverse=True):
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
            
            # Try to find JSON object between the first { and last }
            first_brace = response_text.find('{')
            last_brace = response_text.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_text = response_text[first_brace:last_brace + 1]
                return json.loads(json_text)
                
        except json.JSONDecodeError:
            pass
    
    print(f"Failed to parse JSON from response: {response_text[:200]}...")
    return None


def convert_raw_json_to_resume(raw_data: Dict) -> Optional[Resume]:
    """
    Convert raw JSON data to validated Resume object
    """
    try:
        # Handle potential nested structure
        if 'resume_latest' in raw_data:
            raw_data = raw_data['resume_latest']
        
        # Create Resume object from raw data
        resume = Resume.from_dict(raw_data)
        print("Successfully converted raw JSON to validated Resume object")
        return resume
    except Exception as e:
        print(f"Error converting raw JSON to Resume object: {e}")
        return None

async def parse_resume_raw_json(resume_file_path: str) -> Optional[Dict]:
    """
    Alternative function that returns raw JSON data without StructuredResume conversion
    """
    # Validate Gemini API key before processing
    print("Validating Gemini API key...")
    api_validation = await validate_gemini_api_key()
    
    if not api_validation["valid"]:
        print(f"API validation failed: {api_validation['error']}")
        # Return a special error response that can be handled by the frontend
        return {
            "error": "api_key_invalid",
            "error_message": api_validation["error"],
            "status": "failed"
        }
    
    print("API key validated successfully. Proceeding with resume parsing...")
    
    print(f"Loading resume from: {resume_file_path}")
    resume_text = load_resume_text(resume_file_path)

    if not resume_text:
        print("Failed to load resume text.")
        return None

    print("Resume text loaded. Sending to ResumeParser-AI for processing...")
    
    prompt = f"""
    Please parse the following resume text and extract the information into the structured JSON format.

    Resume Text:
    ---
    {resume_text}
    ---

    CRITICAL: Return ONLY a valid JSON object with all the extracted resume information. Your response must start with {{ and end with }}. NO other text allowed.
    """
    
    try:
        response = await resume_parser_agent.arun(prompt)
        
        print(response)

        # Check if response is a RunResponse object with Resume content
        if hasattr(response, 'content') and isinstance(response.content, Resume):
            print("Resume parsed successfully! Converting Resume object to dictionary.")
            return response.content.model_dump()
        
        # Check if response is directly a Resume object
        elif isinstance(response, Resume):
            print("Resume parsed successfully! Converting Resume object to dictionary.")
            return response.model_dump()
        
        # Fallback: try to extract JSON from string response
        else:
            response_content = response.content if hasattr(response, 'content') else str(response)
            json_data = parse_json_response(response_content)
            
            if json_data:
                print("Resume parsed successfully! Returning raw JSON data.")
                return json_data
            else:
                print("Failed to parse JSON from agent response.")
                return None
            
    except Exception as e:
        print(f"An error occurred during resume parsing: {e}")
        return None

async def main():
    resume_path = r"C:\Users\Prajwal\Downloads\Prajwal_resume.docx.pdf" # REPLACE WITH YOUR RESUME FILE PATH

    print("=== Resume Parser with Pydantic Validation ===")
        
    # Parse resume with validation
    parsed_data = await parse_resume_raw_json(resume_path)

    print(parsed_data)
    
    if parsed_data:
        output_data = {"resume_parsed": parsed_data}
        output_filename = "resume_parsed.json"
        
        try:
            with open(output_filename, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\nSuccessfully saved parsed resume data to {output_filename}")
            
            # Print some parsing results
            print(f"\nParsing Results:")
            if 'contact_info' in parsed_data:
                print(f"- Contact Name: {parsed_data['contact_info'].get('name', 'N/A')}")
                print(f"- Email: {parsed_data['contact_info'].get('email', 'N/A')}")
            if 'work_experience' in parsed_data:
                print(f"- Work Experience Count: {len(parsed_data['work_experience'])}")
            if 'education' in parsed_data:
                print(f"- Education Count: {len(parsed_data['education'])}")
            if 'skills' in parsed_data:
                print(f"- Skills Categories: {list(parsed_data['skills'].keys())}")
            if 'projects' in parsed_data:
                print(f"- Projects Count: {len(parsed_data['projects'])}")
                
        except Exception as e:
            print(f"\nError saving parsed resume data to file: {e}")
    else:
        print("Resume parsing failed.")

if __name__ == "__main__":
   
    asyncio.run(main()) 