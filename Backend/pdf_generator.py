import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

class ResumePDFGenerator:
    """
    A service for generating professional PDF resumes from JSON data using ReportLab
    """
    
    def __init__(self):
        """Initialize the PDF generator"""
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom styles for the resume"""
        # Name/Header style
        self.styles.add(ParagraphStyle(
            name='ResumeTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        ))
        
        # Contact info style
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=12,
            textColor=colors.grey
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=6,
            spaceBefore=12,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        ))
        
        # Job title style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceAfter=2,
            textColor=colors.black
        ))
        
        # Company/Date style
        self.styles.add(ParagraphStyle(
            name='CompanyDate',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            textColor=colors.darkgrey,
            fontName='Helvetica-Oblique'
        ))
        
        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=3,
            textColor=colors.black
        ))
        
        # Skills style
        self.styles.add(ParagraphStyle(
            name='Skills',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            textColor=colors.black
        ))
    
    def generate_pdf(self, 
                     resume_data: Dict[str, Any], 
                     output_path: str) -> bool:
        """
        Generate a PDF resume from JSON data
        
        Args:
            resume_data (Dict[str, Any]): Resume data in JSON format
            output_path (str): Path where the PDF should be saved
            
        Returns:
            bool: True if PDF was generated successfully, False otherwise
        """
        try:
            # Create the PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch,
                leftMargin=0.75*inch,
                rightMargin=0.75*inch
            )
            
            # Build the story (content)
            story = []
            
            # Add header
            self._add_header(story, resume_data.get('contact_info', {}))
            
            # Add professional summary
            if resume_data.get('summary'):
                self._add_professional_summary(story, resume_data['summary'])
            
            # Add work experience
            if resume_data.get('work_experience'):
                self._add_work_experience(story, resume_data['work_experience'])
            
            # Add skills
            if resume_data.get('skills'):
                self._add_skills(story, resume_data['skills'])
            
            # Add education
            if resume_data.get('education'):
                self._add_education(story, resume_data['education'])
            
            # Add certifications
            if resume_data.get('certifications'):
                self._add_certifications(story, resume_data['certifications'])
            
            # Add projects
            if resume_data.get('projects'):
                self._add_projects(story, resume_data['projects'])
            
            # Build the PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
    
    def _add_header(self, story: List, contact_info: Dict[str, Any]):
        """Add header with name and contact information"""
        # Name
        name = contact_info.get('name', 'Your Name')
        story.append(Paragraph(name, self.styles['ResumeTitle']))
        
        # Contact information
        contact_parts = []
        if contact_info.get('email'):
            contact_parts.append(contact_info['email'])
        if contact_info.get('phone'):
            contact_parts.append(contact_info['phone'])
        if contact_info.get('location'):
            contact_parts.append(contact_info['location'])
        if contact_info.get('linkedin'):
            # Create clickable link for LinkedIn
            linkedin_url = contact_info['linkedin']
            contact_parts.append(f'<link href="{linkedin_url}"><font color="blue">LinkedIn</font></link>')
        if contact_info.get('github'):
            # Create clickable link for GitHub
            github_url = contact_info['github']
            contact_parts.append(f'<link href="{github_url}"><font color="blue">GitHub</font></link>')
        
        if contact_parts:
            contact_text = ' • '.join(contact_parts)
            story.append(Paragraph(contact_text, self.styles['ContactInfo']))
    
    def _add_professional_summary(self, story: List, summary: str):
        """Add professional summary section"""
        story.append(Paragraph("PROFESSIONAL SUMMARY", self.styles['SectionHeading']))
        story.append(Paragraph(summary, self.styles['Normal']))
        story.append(Spacer(1, 6))
    
    def _format_date(self, date_str: str) -> str:
        """Format date string to include short month names"""
        if not date_str or date_str.lower() == 'present':
            return date_str
        
        try:
            # Handle different date formats
            if '-' in date_str:
                parts = date_str.split('-')
                if len(parts) >= 2:
                    year = parts[0]
                    month_num = int(parts[1])
                    
                    # Map month numbers to short month names
                    month_names = {
                        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
                    }
                    
                    if month_num in month_names:
                        return f"{year}-{month_names[month_num]}"
            
            # If we can't parse it, return as is
            return date_str
        except (ValueError, IndexError):
            # If there's any error parsing, return the original string
            return date_str

    def _add_work_experience(self, story: List, experience: List[Dict[str, Any]]):
        """Add work experience section"""
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", self.styles['SectionHeading']))
        
        for job in experience:
            # Job title
            title = job.get('title') or job.get('position', 'Position')
            story.append(Paragraph(title, self.styles['JobTitle']))
            
            # Company and dates
            company = job.get('company', 'Company')
            start_date = self._format_date(job.get('start_date', ''))
            end_date = self._format_date(job.get('end_date', 'Present'))
            location = job.get('location', '')
            
            company_info = f"{company}"
            if location:
                company_info += f" • {location}"
            if start_date:
                company_info += f" • {start_date} - {end_date}"
            
            story.append(Paragraph(company_info, self.styles['CompanyDate']))
            
            # Responsibilities/Description
            if job.get('description'):
                # Handle description as list of strings
                if isinstance(job['description'], list):
                    for responsibility in job['description']:
                        bullet_text = f"• {responsibility}"
                        story.append(Paragraph(bullet_text, self.styles['BulletPoint']))
                else:
                    # Handle description as string
                    bullet_text = f"• {job['description']}"
                    story.append(Paragraph(bullet_text, self.styles['BulletPoint']))
            
            # Handle legacy 'responsibilities' field if present
            if job.get('responsibilities'):
                for responsibility in job['responsibilities']:
                    bullet_text = f"• {responsibility}"
                    story.append(Paragraph(bullet_text, self.styles['BulletPoint']))
            
            story.append(Spacer(1, 8))
    
    def _add_skills(self, story: List, skills: Any):
        """Add skills section"""
        story.append(Paragraph("SKILLS", self.styles['SectionHeading']))
        
        if isinstance(skills, dict):
            # Categorized skills
            for category, skill_list in skills.items():
                if skill_list:  # Only add non-empty categories
                    # Remove underscores and capitalize the category heading
                    formatted_category = category.replace('_', ' ').title()
                    category_text = f"<b>{formatted_category}:</b> "
                    if isinstance(skill_list, list):
                        category_text += ', '.join(skill_list)
                    else:
                        category_text += str(skill_list)
                    story.append(Paragraph(category_text, self.styles['Skills']))
        elif isinstance(skills, list):
            # Simple skill list
            skills_text = ', '.join(skills)
            story.append(Paragraph(skills_text, self.styles['Skills']))
        
        story.append(Spacer(1, 6))
    
    def _add_education(self, story: List, education: List[Dict[str, Any]]):
        """Add education section"""
        story.append(Paragraph("EDUCATION", self.styles['SectionHeading']))
        
        for edu in education:
            # Degree/Title
            degree = edu.get('degree') or edu.get('title', 'Degree')
            story.append(Paragraph(degree, self.styles['JobTitle']))
            
            # Institution and date
            institution = edu.get('institution') or edu.get('school', 'Institution')
            grad_date = self._format_date(edu.get('graduation_date') or edu.get('end_date', ''))
            gpa = edu.get('gpa', '')
            major = edu.get('major', '')
            
            edu_info = institution
            if major:
                edu_info += f" • {major}"
            if grad_date:
                edu_info += f" • {grad_date}"
            if gpa:
                edu_info += f" • GPA: {gpa}"
            
            story.append(Paragraph(edu_info, self.styles['CompanyDate']))
            story.append(Spacer(1, 6))
    
    def _add_certifications(self, story: List, certifications: List):
        """Add certifications section"""
        story.append(Paragraph("CERTIFICATIONS", self.styles['SectionHeading']))
        
        for cert in certifications:
            if isinstance(cert, dict):
                cert_name = cert.get('title') or cert.get('name', str(cert))
                issuer = cert.get('issuer', '')
                date = self._format_date(cert.get('date', ''))
                description = cert.get('description', '')
                
                cert_text = cert_name
                if issuer:
                    cert_text += f" - {issuer}"
                if date:
                    cert_text += f" ({date})"
                if description:
                    cert_text += f" - {description}"
            else:
                cert_text = str(cert)
            
            story.append(Paragraph(f"• {cert_text}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 6))
    
    def _add_projects(self, story: List, projects: List[Dict[str, Any]]):
        """Add projects section"""
        story.append(Paragraph("PROJECTS", self.styles['SectionHeading']))
        
        for project in projects:
            # Project name
            name = project.get('title') or project.get('name', 'Project')
            story.append(Paragraph(name, self.styles['JobTitle']))
            
            # Project dates if available
            start_date = self._format_date(project.get('start_date', ''))
            end_date = self._format_date(project.get('end_date', ''))
            completion_date = self._format_date(project.get('completion_date', ''))
            
            if start_date or end_date or completion_date:
                date_info = []
                if start_date and end_date:
                    date_info.append(f"{start_date} - {end_date}")
                elif start_date:
                    date_info.append(f"Started: {start_date}")
                elif completion_date:
                    date_info.append(f"Completed: {completion_date}")
                
                if date_info:
                    story.append(Paragraph(date_info[0], self.styles['CompanyDate']))
            
            # Description
            if project.get('description'):
                # Handle description as list of strings
                if isinstance(project['description'], list):
                    for desc in project['description']:
                        story.append(Paragraph(f"• {desc}", self.styles['BulletPoint']))
                else:
                    # Handle description as string
                    story.append(Paragraph(project['description'], self.styles['Normal']))
            
            # Technologies
            if project.get('technologies_used'):
                if isinstance(project['technologies_used'], list) and project['technologies_used']:
                    tech_text = f"<b>Technologies:</b> {', '.join(project['technologies_used'])}"
                    story.append(Paragraph(tech_text, self.styles['Skills']))
                elif isinstance(project['technologies_used'], str):
                    tech_text = f"<b>Technologies:</b> {project['technologies_used']}"
                    story.append(Paragraph(tech_text, self.styles['Skills']))
            
            # URL if available
            if project.get('url'):
                project_url = project['url']
                url_text = f"<b>URL:</b> <link href=\"{project_url}\"><font color=\"blue\">Link</font></link>"
                story.append(Paragraph(url_text, self.styles['Skills']))
            
            story.append(Spacer(1, 6))

def create_pdf_from_json(json_file_path: str, output_pdf_path: str) -> bool:
    """
    Convenience function to create PDF from JSON file
    
    Args:
        json_file_path (str): Path to the JSON resume file
        output_pdf_path (str): Path where the PDF should be saved
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        
        generator = ResumePDFGenerator()
        return generator.generate_pdf(resume_data, output_pdf_path)
        
    except Exception as e:
        print(f"Error creating PDF from JSON: {e}")
        return False 