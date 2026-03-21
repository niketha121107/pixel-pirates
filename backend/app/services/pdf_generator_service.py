"""
PDF Generator for Study Materials
Creates professional, formatted PDFs based on learning level
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.colors import HexColor

logger = logging.getLogger(__name__)

class AdaptivePDFGenerator:
    """Generate adaptive PDFs based on learning level"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for different sections"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=HexColor('#1a1a2e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#16213e'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body styles for different levels
        self.styles.add(ParagraphStyle(
            name='BeginnerBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            textColor=HexColor('#2d3561')
        ))
        
        self.styles.add(ParagraphStyle(
            name='IntermediateBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            leading=15,
            alignment=TA_JUSTIFY,
            textColor=HexColor('#2d3561')
        ))
        
        self.styles.add(ParagraphStyle(
            name='AdvancedBody',
            parent=self.styles['BodyText'],
            fontSize=9,
            leading=14,
            alignment=TA_JUSTIFY,
            textColor=HexColor('#2d3561')
        ))
        
        self.styles.add(ParagraphStyle(
            name='ExpertBody',
            parent=self.styles['BodyText'],
            fontSize=9,
            leading=13,
            alignment=TA_JUSTIFY,
            textColor=HexColor('#1a1a1a')
        ))
        
        # Code style (only if not already defined)
        if 'CustomCode' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomCode',
                fontName='Courier',
                fontSize=8,
                textColor=HexColor('#e94560'),
                backColor=HexColor('#f9f9f9'),
                leftIndent=20,
                rightIndent=20
            ))
    
    def generate_pdf(
        self,
        study_material: Dict[str, Any],
        output_path: str
    ) -> bool:
        """Generate PDF from study material"""
        
        try:
            logger.info(f"Generating PDF: {output_path}")
            
            topic = study_material.get('topic', 'Study Material')
            learning_level = study_material.get('learning_level', 'adaptive')
            
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch,
                title=topic,
                author="Pixel Pirates"
            )
            
            # Build story (content)
            story = []
            
            # Add title
            story.append(Paragraph(topic, self.styles['CustomTitle']))
            story.append(Spacer(1, 0.2*inch))
            
            # Add metadata
            metadata = f"""
            <font size=9>
            <b>Learning Level:</b> {learning_level.upper()}<br/>
            <b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
            <b>Regeneration Count:</b> {study_material.get('regeneration_count', 0)}
            </font>
            """
            story.append(Paragraph(metadata, self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Add explanations section
            explanations = study_material.get('explanations', {})
            if explanations:
                story.append(Paragraph("Study Material", self.styles['CustomHeading']))
                story.append(Spacer(1, 0.1*inch))
                
                # Add main explanation for current level
                main_explanation = explanations.get(learning_level, {})
                if main_explanation:
                    content = main_explanation.get('content', '')
                    body_style = f'{learning_level.capitalize()}Body' if learning_level != 'adaptive' else 'BeginnerBody'
                    
                    # Clean and format content
                    for paragraph in content.split('\n\n'):
                        if paragraph.strip():
                            story.append(Paragraph(paragraph.strip(), self.styles.get(body_style, self.styles['BodyText'])))
                            story.append(Spacer(1, 0.1*inch))
            
            # Add key concepts
            concepts = study_material.get('key_concepts', [])
            if concepts:
                story.append(PageBreak())
                story.append(Paragraph("Key Concepts", self.styles['CustomHeading']))
                story.append(Spacer(1, 0.1*inch))
                
                # Create concepts table
                concept_data = [["Concept", "Definition", "Importance"]]
                for concept in concepts[:10]:
                    concept_data.append([
                        Paragraph(concept.get('name', ''), self.styles['Normal']),
                        Paragraph(concept.get('definition', ''), self.styles['Normal']),
                        Paragraph(concept.get('importance', ''), self.styles['Normal'])
                    ])
                
                table = Table(concept_data, colWidths=[1.5*inch, 2*inch, 2*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#16213e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f9f9f9')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f5f5f5')])
                ]))
                story.append(table)
            
            # Add practice questions
            questions = study_material.get('practice_questions', [])
            if questions:
                story.append(PageBreak())
                story.append(Paragraph("Practice Questions", self.styles['CustomHeading']))
                story.append(Spacer(1, 0.1*inch))
                
                for idx, question in enumerate(questions[:15], 1):
                    q_text = f"<b>Q{idx} ({question.get('difficulty', 'medium').upper()}):</b> {question.get('question', '')}"
                    story.append(Paragraph(q_text, self.styles['BodyText']))
                    
                    answer = f"<b>Answer:</b> {question.get('correct_answer', '')}"
                    story.append(Paragraph(answer, self.styles['BodyText']))
                    
                    explanation = f"<b>Explanation:</b> {question.get('explanation', '')}"
                    story.append(Paragraph(explanation, self.styles['Normal']))
                    
                    story.append(Spacer(1, 0.15*inch))
            
            # Add real-world examples
            examples = study_material.get('real_world_examples', [])
            if examples:
                story.append(PageBreak())
                story.append(Paragraph("Real-World Examples", self.styles['CustomHeading']))
                story.append(Spacer(1, 0.1*inch))
                
                for idx, example in enumerate(examples, 1):
                    story.append(Paragraph(f"<b>Example {idx}:</b> {example.get('scenario', '')}", self.styles['BodyText']))
                    story.append(Paragraph(f"<b>Application:</b> {example.get('application', '')}", self.styles['BodyText']))
                    story.append(Paragraph(f"<b>Outcome:</b> {example.get('outcome', '')}", self.styles['BodyText']))
                    story.append(Spacer(1, 0.15*inch))
            
            # Build PDF
            doc.build(story)
            logger.info(f"✅ PDF generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return False
    
    def generate_comparison_pdf(
        self,
        study_materials: Dict[str, Dict[str, Any]],
        output_path: str
    ) -> bool:
        """Generate comparison PDF showing all 4 explanation levels"""
        
        try:
            logger.info(f"Generating comparison PDF: {output_path}")
            
            if not study_materials or len(study_materials) == 0:
                logger.error("No materials to compare")
                return False
            
            first_material = next(iter(study_materials.values()))
            topic = first_material.get('topic', 'Study Material')
            
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch,
                title=f"{topic} - Comparison",
                author="Pixel Pirates"
            )
            
            story = []
            
            # Title
            story.append(Paragraph(f"{topic} - All Learning Levels", self.styles['CustomTitle']))
            story.append(Spacer(1, 0.2*inch))
            
            # Add each level side by side
            for level in ['beginner', 'intermediate', 'advanced', 'expert']:
                story.append(PageBreak())
                story.append(Paragraph(f"{level.upper()} Level", self.styles['CustomHeading']))
                story.append(Spacer(1, 0.1*inch))
                
                material = study_materials.get(level, {})
                explanations = material.get('explanations', {})
                explanation = explanations.get(level, {})
                
                content = explanation.get('content', 'No content available')
                body_style = f'{level.capitalize()}Body'
                
                # Add content in smaller paragraphs
                for para in content.split('\n\n'):
                    if para.strip():
                        story.append(Paragraph(para.strip(), self.styles.get(body_style, self.styles['BodyText'])))
                        story.append(Spacer(1, 0.08*inch))
            
            # Build PDF
            doc.build(story)
            logger.info(f"✅ Comparison PDF generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating comparison PDF: {e}")
            return False

# Global instance
pdf_generator = AdaptivePDFGenerator()
