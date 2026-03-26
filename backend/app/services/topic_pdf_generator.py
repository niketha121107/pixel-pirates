"""
Topic PDF Generator
Generates study material PDFs for all topics with comprehensive explanations
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.colors import HexColor

logger = logging.getLogger(__name__)


class TopicPDFGenerator:
    """Generate professional PDFs for topics"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1a1a2e'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#16213e'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            textColor=HexColor('#2d3561')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=HexColor('#2d3561'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
    
    def generate_topic_pdf(
        self,
        topic: Dict[str, Any],
        output_path: str
    ) -> bool:
        """Generate a comprehensive PDF for a single topic"""
        try:
            logger.info(f"Generating topic PDF: {output_path}")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            topic_name = topic.get('name') or topic.get('topicName', 'Study Material')
            language = topic.get('language', 'Unknown')
            difficulty = topic.get('difficulty', 'Unknown')
            overview = topic.get('overview', '')
            
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch,
                title=topic_name,
                author="Pixel Pirates"
            )
            
            story = []
            
            # Title
            story.append(Paragraph(topic_name, self.styles['CustomTitle']))
            story.append(Spacer(1, 0.15*inch))
            
            # Metadata
            metadata = f"""
            <font size=9 color="#666666">
            <b>Language:</b> {language} | <b>Difficulty:</b> {difficulty}<br/>
            <b>Generated:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
            </font>
            """
            story.append(Paragraph(metadata, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Overview
            if overview:
                story.append(Paragraph("Overview", self.styles['CustomHeading']))
                story.append(Paragraph(overview, self.styles['CustomBody']))
                story.append(Spacer(1, 0.2*inch))
            
            # Explanations (all styles)
            explanations = topic.get('explanations', {})
            if explanations:
                story.append(Paragraph("Study Material", self.styles['CustomHeading']))
                story.append(Spacer(1, 0.1*inch))
                
                explanation_order = ['simplified', 'logical', 'visual', 'analogy']
                for style in explanation_order:
                    if style in explanations:
                        content = explanations[style]
                        
                        # Get text content
                        if isinstance(content, dict):
                            text = content.get('content', '')
                            style_title = content.get('title', f"{style.capitalize()} Explanation")
                        else:
                            text = str(content)
                            style_title = f"{style.capitalize()} Explanation"
                        
                        if text and len(text.strip()) > 10:
                            story.append(Paragraph(style_title, self.styles['SubHeading']))
                            
                            # Clean up text - remove extra whitespace and bullet points
                            text = text.replace('\n\n', '<br/>')
                            text = text.replace('\n', ' ')
                            # Remove bullet points
                            text = text.replace('•', '-').replace('◦', '-')
                            # Escape special HTML characters
                            text = text.replace('&', '&amp;')
                            text = text.strip()
                            
                            if text:
                                story.append(Paragraph(text, self.styles['CustomBody']))
                                story.append(Spacer(1, 0.15*inch))
                
                story.append(PageBreak())
            
            # Key Notes
            key_notes = topic.get('key_notes', '')
            if key_notes:
                story.append(Paragraph("Key Points", self.styles['CustomHeading']))
                story.append(Paragraph(key_notes, self.styles['CustomBody']))
                story.append(Spacer(1, 0.2*inch))
            
            # Study Material
            study_material = topic.get('study_material', {})
            if study_material and isinstance(study_material, dict):
                story.append(Paragraph("Comprehensive Study Guide", self.styles['CustomHeading']))
                story.append(Spacer(1, 0.1*inch))
                
                if 'overview' in study_material:
                    story.append(Paragraph("Overview", self.styles['SubHeading']))
                    story.append(Paragraph(study_material['overview'], self.styles['CustomBody']))
                    story.append(Spacer(1, 0.1*inch))
                
                if 'explanation' in study_material:
                    story.append(Paragraph("Detailed Explanation", self.styles['SubHeading']))
                    story.append(Paragraph(study_material['explanation'], self.styles['CustomBody']))
                    story.append(Spacer(1, 0.1*inch))
                
                if 'syntax' in study_material:
                    story.append(Paragraph("Syntax", self.styles['SubHeading']))
                    story.append(Paragraph(study_material['syntax'], self.styles['CustomBody']))
                    story.append(Spacer(1, 0.1*inch))
                
                if 'example' in study_material:
                    story.append(Paragraph("Code Example", self.styles['SubHeading']))
                    code_text = study_material['example']
                    # Format code in monospace
                    story.append(Paragraph(
                        f"<font face='Courier' size='9'>{code_text.replace('<', '&lt;').replace('>', '&gt;')}</font>",
                        self.styles['Normal']
                    ))
                    story.append(Spacer(1, 0.1*inch))
                
                if 'advantages' in study_material:
                    advantages = study_material['advantages']
                    if isinstance(advantages, str) and advantages:
                        story.append(Paragraph("Advantages", self.styles['SubHeading']))
                        story.append(Paragraph(advantages, self.styles['CustomBody']))
                        story.append(Spacer(1, 0.1*inch))
                
                if 'disadvantages' in study_material:
                    disadvantages = study_material['disadvantages']
                    if isinstance(disadvantages, str) and disadvantages:
                        story.append(Paragraph("Disadvantages", self.styles['SubHeading']))
                        story.append(Paragraph(disadvantages, self.styles['CustomBody']))
                        story.append(Spacer(1, 0.1*inch))
            
            # Add footer
            story.append(Spacer(1, 0.2*inch))
            footer = f"<font size='8' color='#999999'>Pixel Pirates Learning Platform | {topic_name}</font>"
            story.append(Paragraph(footer, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            logger.info(f"✅ Topic PDF generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating topic PDF: {e}", exc_info=True)
            return False


# Global instance
topic_pdf_generator = TopicPDFGenerator()
