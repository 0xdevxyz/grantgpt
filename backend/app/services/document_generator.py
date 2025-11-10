"""
Document Generation Service - PDF and DOCX export
"""
from typing import Dict, Any
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import pdfkit
from datetime import datetime
import os


class DocumentGenerator:
    """Service for generating professional grant application documents"""
    
    def __init__(self):
        self.storage_dir = "/app/storage/documents"
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def generate_docx(
        self,
        application_id: str,
        application_data: Dict[str, Any],
        sections: Dict[str, str]
    ) -> str:
        """
        Generate DOCX document for grant application
        
        Args:
            application_id: Application ID
            application_data: Application metadata
            sections: Generated content sections
            
        Returns:
            File path to generated DOCX
        """
        doc = Document()
        
        # Set document properties
        doc.core_properties.title = application_data.get("project_title", "Förderantrag")
        doc.core_properties.author = "GrantGPT"
        doc.core_properties.created = datetime.now()
        
        # Title Page
        self._add_title_page(doc, application_data)
        doc.add_page_break()
        
        # Table of Contents
        self._add_table_of_contents(doc, sections)
        doc.add_page_break()
        
        # Content Sections
        section_order = [
            ("project_description", "1. Projektbeschreibung"),
            ("market_analysis", "2. Marktanalyse"),
            ("technical_feasibility", "3. Technische Machbarkeit"),
            ("work_plan", "4. Arbeitsplan"),
            ("utilization_plan", "5. Verwertungsplan"),
            ("financial_plan", "6. Finanzplan"),
            ("risk_management", "7. Risikomanagement")
        ]
        
        for section_key, section_title in section_order:
            if section_key in sections:
                self._add_section(doc, section_title, sections[section_key])
                doc.add_page_break()
        
        # Save document
        filename = f"{application_id}.docx"
        filepath = os.path.join(self.storage_dir, filename)
        doc.save(filepath)
        
        return filepath
    
    def generate_pdf(
        self,
        application_id: str,
        application_data: Dict[str, Any],
        sections: Dict[str, str]
    ) -> str:
        """
        Generate PDF document for grant application
        
        Args:
            application_id: Application ID
            application_data: Application metadata
            sections: Generated content sections
            
        Returns:
            File path to generated PDF
        """
        # First generate HTML
        html_content = self._generate_html(application_data, sections)
        
        # Convert to PDF
        filename = f"{application_id}.pdf"
        filepath = os.path.join(self.storage_dir, filename)
        
        options = {
            'page-size': 'A4',
            'margin-top': '2cm',
            'margin-right': '2cm',
            'margin-bottom': '2cm',
            'margin-left': '2cm',
            'encoding': 'UTF-8',
            'enable-local-file-access': None
        }
        
        try:
            pdfkit.from_string(html_content, filepath, options=options)
        except Exception as e:
            print(f"PDF generation failed, falling back to basic method: {e}")
            # Fallback: Save HTML and try again
            html_file = filepath.replace('.pdf', '.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            pdfkit.from_file(html_file, filepath, options=options)
            os.remove(html_file)
        
        return filepath
    
    def _add_title_page(self, doc: Document, application_data: Dict[str, Any]):
        """Add title page to document"""
        # Title
        title = doc.add_paragraph()
        title_run = title.add_run(application_data.get("project_title", "Förderantrag"))
        title_run.font.size = Pt(24)
        title_run.font.bold = True
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add some space
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Subtitle
        subtitle = doc.add_paragraph()
        subtitle_run = subtitle.add_run("Förderantrag")
        subtitle_run.font.size = Pt(16)
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()
        
        # Grant name
        if "grant_name" in application_data:
            grant = doc.add_paragraph()
            grant_run = grant.add_run(f"Förderprogramm: {application_data['grant_name']}")
            grant_run.font.size = Pt(14)
            grant.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add space
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Applicant info
        info = doc.add_paragraph()
        info.add_run("Antragsteller:\n").bold = True
        info.add_run(f"{application_data.get('company_name', 'Firma')}\n")
        if "company_location" in application_data:
            info.add_run(f"{application_data['company_location']}\n")
        
        doc.add_paragraph()
        
        # Date
        date_p = doc.add_paragraph()
        date_p.add_run(f"Datum: {datetime.now().strftime('%d.%m.%Y')}")
        date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    def _add_table_of_contents(self, doc: Document, sections: Dict[str, str]):
        """Add table of contents"""
        heading = doc.add_heading("Inhaltsverzeichnis", level=1)
        
        toc_entries = [
            "1. Projektbeschreibung",
            "2. Marktanalyse",
            "3. Technische Machbarkeit",
            "4. Arbeitsplan",
            "5. Verwertungsplan",
            "6. Finanzplan",
            "7. Risikomanagement"
        ]
        
        for entry in toc_entries:
            p = doc.add_paragraph(entry, style='List Number')
    
    def _add_section(self, doc: Document, title: str, content: str):
        """Add a content section"""
        # Section heading
        doc.add_heading(title, level=1)
        
        # Section content (split by paragraphs)
        paragraphs = content.split('\n\n')
        for para_text in paragraphs:
            if para_text.strip():
                # Check if it's a subheading (starts with ##)
                if para_text.strip().startswith('##'):
                    heading_text = para_text.strip().lstrip('#').strip()
                    doc.add_heading(heading_text, level=2)
                else:
                    p = doc.add_paragraph(para_text.strip())
                    p.style.font.size = Pt(11)
    
    def _generate_html(
        self,
        application_data: Dict[str, Any],
        sections: Dict[str, str]
    ) -> str:
        """Generate HTML for PDF conversion"""
        html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            font-size: 18pt;
            font-weight: bold;
            margin-top: 20pt;
            margin-bottom: 12pt;
            page-break-after: avoid;
        }}
        h2 {{
            font-size: 14pt;
            font-weight: bold;
            margin-top: 16pt;
            margin-bottom: 8pt;
            page-break-after: avoid;
        }}
        p {{
            margin-bottom: 10pt;
            text-align: justify;
        }}
        .title-page {{
            text-align: center;
            page-break-after: always;
        }}
        .title {{
            font-size: 24pt;
            font-weight: bold;
            margin-top: 100pt;
        }}
        .subtitle {{
            font-size: 16pt;
            margin-top: 20pt;
        }}
    </style>
</head>
<body>
    <div class="title-page">
        <div class="title">{application_data.get('project_title', 'Förderantrag')}</div>
        <div class="subtitle">Förderantrag</div>
        <p style="margin-top: 50pt;">
            <strong>Antragsteller:</strong><br>
            {application_data.get('company_name', 'Firma')}<br>
            {application_data.get('company_location', '')}
        </p>
        <p>Datum: {datetime.now().strftime('%d.%m.%Y')}</p>
    </div>
    
    <h1>Inhaltsverzeichnis</h1>
    <ol>
        <li>Projektbeschreibung</li>
        <li>Marktanalyse</li>
        <li>Technische Machbarkeit</li>
        <li>Arbeitsplan</li>
        <li>Verwertungsplan</li>
        <li>Finanzplan</li>
        <li>Risikomanagement</li>
    </ol>
    <div style="page-break-after: always;"></div>
"""
        
        # Add sections
        section_order = [
            ("project_description", "1. Projektbeschreibung"),
            ("market_analysis", "2. Marktanalyse"),
            ("technical_feasibility", "3. Technische Machbarkeit"),
            ("work_plan", "4. Arbeitsplan"),
            ("utilization_plan", "5. Verwertungsplan"),
            ("financial_plan", "6. Finanzplan"),
            ("risk_management", "7. Risikomanagement")
        ]
        
        for section_key, section_title in section_order:
            if section_key in sections:
                content = sections[section_key]
                # Simple markdown to HTML conversion
                content = content.replace('\n\n', '</p><p>')
                content = f"<p>{content}</p>"
                
                html += f"""
    <h1>{section_title}</h1>
    {content}
    <div style="page-break-after: always;"></div>
"""
        
        html += """
</body>
</html>
"""
        return html


# Singleton instance
document_generator = DocumentGenerator()

