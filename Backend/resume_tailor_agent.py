import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from textwrap import dedent
from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.models.google import Gemini

# Pydantic models for structured resume output
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
    start_date: str = Field(..., description="Start date in YYYY-MM format")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM format, or 'Present'")
    location: Optional[str] = Field(None, description="Job location")
    description: List[str] = Field(..., description="List of job responsibilities and achievements")

class Education(BaseModel):
    institution: str = Field(..., description="University or institution name")
    degree: str = Field(..., description="Degree type")
    major: Optional[str] = Field(None, description="Field of study")
    graduation_date: Optional[str] = Field(None, description="Year of graduation")
    gpa: Optional[str] = Field(None, description="GPA if mentioned")
    location: Optional[str] = Field(None, description="Institution location")   
    grade: Optional[str] = Field(None, description="Grade if mentioned")

class Project(BaseModel):
    title: str = Field(..., description="Project title")
    description: List[str] = Field(..., description="List of project descriptions and outcomes")
    url: Optional[str] = Field(None, description="Project URL if available")
    technologies_used: List[str] = Field(..., description="List of technologies used in the project")

class Skills(BaseModel):
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks and libraries")
    databases: List[str] = Field(default_factory=list, description="Database systems")
    languages: List[str] = Field(default_factory=list, description="Spoken languages")
    soft_skills: List[str] = Field(default_factory=list, description="Soft skills")
    other: List[str] = Field(default_factory=list, description="Other skills not categorized above")

class TailoredResume(BaseModel):
    contact_info: ContactInfo = Field(..., description="Contact information")
    summary: str = Field(..., description="Tailored professional summary")
    skills: Skills = Field(..., description="Tailored skills organized by category")
    work_experience: List[WorkExperience] = Field(..., description="Tailored work experience")
    education: List[Education] = Field(default_factory=list, description="Education entries")
    projects: List[Project] = Field(..., description="Tailored projects")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")
    awards_and_honors: List[str] = Field(default_factory=list, description="Awards, honors, and recognitions")
    languages: List[str] = Field(default_factory=list, description="Languages with proficiency levels")


def create_resume_tailor_agent() -> Agent:
    """
    Creates and returns a resume tailor agent using Gemini 2.5 Flash.
    
    Returns:
        Agent: The configured resume tailor agent.
    """
    return Agent(
        model=Gemini("gemini-2.5-flash"),
        description="Tailor resume sections to match specific job descriptions",
        instructions=dedent("""\
            Tailor the provided resume sections (summary, skills, work_experience, projects) to match the specific job opportunity.
            
            You will receive comprehensive job context including title, company, industry, level, requirements, and description.
            Use this context to make informed tailoring decisions.
            
            Return ONLY a valid JSON object with the tailored sections. Follow these rules:
            
            1. NO FABRICATION: Only use information present in the original resume
            2. PRESERVE ALL CONTENT: Keep all bullet points, responsibilities, and achievements
            3. ENHANCE WITH KEYWORDS: Incorporate relevant keywords from the job description and requirements
            4. MAINTAIN STRUCTURE: Keep the same field names and organization
            5. CONTEXT-AWARE: Use job title, company, industry, and level to guide your tailoring approach
            6. PLAIN TEXT ONLY: Do not use markdown or any other formatting.
            
            REQUIRED OUTPUT STRUCTURE:
            {
                "contact_info": {
                    "name": "Full name",
                    "email": "email@example.com",
                    "phone": "phone number",
                    "linkedin": "LinkedIn URL",
                    "github": "GitHub URL",
                    "portfolio": "Portfolio URL"
                },
                "summary": "string - tailored professional summary",
                "skills": {
                    "programming_languages": ["language1", "language2"],
                    "frameworks": ["framework1", "framework2"],
                    "databases": ["database1", "database2"],
                    "languages": ["spoken language1", "spoken language2"],
                    "soft_skills": ["skill1", "skill2"],
                    "other": ["other skill1", "other skill2"]
                },
                "work_experience": [
                    {
                        "company": "string",
                        "title": "string",
                        "start_date": "YYYY-MM",
                        "end_date": "YYYY-MM or Present",
                        "location": "Job location",
                        "description": ["bullet1", "bullet2"]
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
                "projects": [
                    {
                        "title": "string",
                        "description": ["desc1", "desc2"],
                        "url": "Project URL if available",
                        "technologies_used": ["tech1", "tech2"]
                    }
                ],
                "certifications": ["cert1", "cert2"],
                "awards_and_honors": ["award1", "award2"],
                "languages": ["language1", "language2"]
            }
            
            Tailoring Guidelines:
            - Contact Info: Preserve all contact information exactly as provided (name, email, phone, etc.)
            - Summary: Rewrite to directly address the specific role and company while maintaining authenticity
            - Skills: Prioritize skills that match the job requirements and industry, organize into categories
            - Work Experience: Enhance bullet points with strong action verbs and relevant keywords for the specific role
            - Education: Preserve all education information exactly as provided
            - Projects: Highlight technologies and outcomes that align with the job requirements and company focus
            - Certifications, Awards, Languages: Preserve all information exactly as provided
            
            Return ONLY the JSON object with tailored sections. No additional text.
            """),
        markdown=False,
        show_tool_calls=False,
    )

def clean_response_content(response_text: str) -> str:
    """
    Clean up the response content to handle markdown code blocks
    """
    import re
    
    # Remove markdown code blocks (```json ... ``` or ``` ... ```)
    response_text = re.sub(r'```json\s*\n?(.*?)\n?```', r'\1', response_text, flags=re.DOTALL)
    response_text = re.sub(r'```\s*\n?(.*?)\n?```', r'\1', response_text, flags=re.DOTALL)
    
    # Remove any leading/trailing whitespace
    return response_text.strip()

def parse_json_response(response_text: str) -> Optional[Dict]:
    """
    Parse the agent's response and extract JSON content with improved nested JSON handling
    """
    # Try to parse the response directly as JSON
    return json.loads(response_text)

   

async def tailor_resume(resume_data: Dict[str, Any], job_context: Dict[str, Any]) -> Optional[TailoredResume]:
    """
    Takes focused resume data and enhanced job context, then returns tailored sections.

    Args:
        resume_data (Dict[str, Any]): The user's focused resume data (skills, work_experience, projects).
        job_context (Dict[str, Any]): Enhanced job context including title, company, description, etc.

    Returns:
        TailoredResume: A validated Pydantic model containing the tailored resume sections, or None if parsing fails.
    """
    
    # Create the agent
    agent = create_resume_tailor_agent()
    
    # Extract and clean the job description text
    job_description_text = job_context.get("description", "").replace('\n', ' ')
    
    # Create the prompt with the focused resume sections and enhanced job context
    prompt = f"""
    Please tailor the following focused resume sections for the specific job opportunity. Follow all the rules and guidelines specified in your instructions.

    Resume Sections to Tailor:
    ---
    {json.dumps(resume_data, indent=2)}
    ---

    Job Context:
    ---
    Title: {job_context.get("title", "N/A")}
    Company: {job_context.get("company", "N/A")}
    Location: {job_context.get("location", "N/A")}
    Job Level: {job_context.get("job_level", "N/A")}
    Job Function: {job_context.get("job_function", "N/A")}
    Industry: {job_context.get("company_industry", "N/A")}
    Remote: {job_context.get("is_remote", False)}
    Job Type: {job_context.get("job_type", "N/A")}
    Required Skills: {job_context.get("skills", "N/A")}
    Experience Range: {job_context.get("experience_range", "N/A")}
    Company Size: {job_context.get("company_num_employees", "N/A")}
    Salary Range: {job_context.get("min_amount", "")} - {job_context.get("max_amount", "")} {job_context.get("currency", "")}
    
    Job Description:
    {job_description_text}
    
    Company Description:
    {job_context.get("company_description", "N/A")}
    ---

    CRITICAL REMINDERS:
    1. Return ONLY a valid JSON object with the tailored resume sections. Your response must start with {{ and end with }}. NO other text allowed.
    2. PRESERVE ALL CONTENT: Do not remove any bullet points, responsibilities, or achievements. Enhance them, don't delete them.
    3. Maintain the exact same number of bullet points in each section as the original resume.
    4. Use the job context (title, company, industry, level) to make informed tailoring decisions.
    """

    try:
        print("Sending resume to ResumeTailor-AI for processing...")
        response = await agent.arun(prompt)
        
        # Extract content from response object
        response_content = response.content if hasattr(response, 'content') else str(response)
        
        # Clean up the response content
        cleaned_content = clean_response_content(response_content)
        
        # Parse JSON from response
        tailored_data = parse_json_response(cleaned_content)
        
        if tailored_data:
            try:
                # Validate and convert to Pydantic model
                validated_resume = TailoredResume(**tailored_data)
                print("Successfully tailored and validated resume!")
                return validated_resume
            except Exception as validation_error:
                print(f"Validation error: {validation_error}")
                print("Attempting to fix common validation issues...")
                
        else:
            print("Failed to parse JSON from agent response.")
            return None

    except Exception as e:
        print(f"An unexpected error occurred while contacting the LLM: {e}")
        raise

# Example usage function
async def example_usage():
    """Example of how to use the resume tailor functions"""
    
    # Example job description
    job_description = """
    We are seeking a Senior Python Developer to join our team. The ideal candidate will have:
    - 5+ years of Python development experience
    - Experience with FastAPI, Django, or Flask
    - Knowledge of PostgreSQL and database design
    - Experience with cloud platforms (AWS, GCP)
    - Strong problem-solving skills
    - Experience with agile development methodologies
    """
    
    # Example focused resume data (what would be sent to the tailoring agent)
    focused_resume_example = {
        "summary": "Experienced software developer with 3+ years of experience in web development and database management. Skilled in Python, JavaScript, and modern frameworks.",
        "skills": {
            "Technical": ["Python", "JavaScript", "SQL"],
            "Programming Languages": ["Python", "JavaScript", "Java"],
            "Frameworks": ["Django", "React", "Node.js"],
            "Tools": ["Git", "Docker", "Linux"],
            "Databases": ["MySQL", "MongoDB"],
            "Other": ["Problem Solving", "Team Leadership"]
        },
        "work_experience": [
            {
                "company": "Example Corp",
                "title": "Software Developer",
                "start_date": "2020-01",
                "end_date": "Present",
                "description": ["Developed web applications using Python", "Collaborated with cross-functional teams"]
            }
        ],
        "projects": [
            {
                "title": "E-commerce Platform",
                "description": ["Built full-stack web application", "Implemented user authentication"],
                "technologies_used": ["Python", "Django", "PostgreSQL"]
            }
        ]
    }
    
    print("Resume tailor functions ready with Gemini 2.5 Flash!")
    print("Ready to tailor focused resume sections (summary, skills, work_experience, projects)")
    
    # Example usage with enhanced job context:
    # job_context = {
    #     "title": "Senior Python Developer",
    #     "company": "Tech Corp",
    #     "location": "San Francisco, CA",
    #     "job_level": "senior",
    #     "description": job_description,
    #     "company_industry": "Technology"
    # }
    # tailored_sections = await tailor_resume(focused_resume_example, job_context)
    
    return {"job_description": job_description, "focused_resume_example": focused_resume_example}

if __name__ == "__main__":
    # Test the resume tailor functions
    # Ensure you have 'agno' installed: pip install agno
    asyncio.run(example_usage())