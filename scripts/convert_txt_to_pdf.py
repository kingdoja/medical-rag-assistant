#!/usr/bin/env python
"""Convert text files to PDF for ingestion testing.

This script converts the sample autonomous driving text documents to PDF format
so they can be ingested by the RAG system.
"""

import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Ensure project root is on sys.path
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
sys.path.insert(0, str(_REPO_ROOT))


def convert_txt_to_pdf(txt_path: Path, pdf_path: Path) -> None:
    """Convert a text file to PDF.
    
    Args:
        txt_path: Path to input text file
        pdf_path: Path to output PDF file
    """
    # Read the text file
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Try to use a font that supports Chinese characters
    try:
        # Try to register a Chinese font (you may need to adjust the path)
        # For Windows, you can use SimSun or Microsoft YaHei
        # For Linux, you can use WenQuanYi or Noto Sans CJK
        # For macOS, you can use PingFang or Heiti
        
        # This is a fallback - the PDF will be created but Chinese may not render correctly
        # In production, you should install proper Chinese fonts
        pass
    except:
        pass
    
    # Process content line by line
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            elements.append(Spacer(1, 0.2*inch))
            continue
        
        # Detect headers (lines starting with #)
        if line.startswith('# '):
            # H1
            style = ParagraphStyle(
                'CustomH1',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=12,
                textColor='#000000',
            )
            text = line[2:].strip()
            elements.append(Paragraph(text, style))
        elif line.startswith('## '):
            # H2
            style = ParagraphStyle(
                'CustomH2',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=10,
                textColor='#000000',
            )
            text = line[3:].strip()
            elements.append(Paragraph(text, style))
        elif line.startswith('### '):
            # H3
            style = ParagraphStyle(
                'CustomH3',
                parent=styles['Heading3'],
                fontSize=12,
                spaceAfter=8,
                textColor='#000000',
            )
            text = line[4:].strip()
            elements.append(Paragraph(text, style))
        elif line.startswith('- ') or line.startswith('* '):
            # Bullet point
            style = ParagraphStyle(
                'CustomBullet',
                parent=styles['Normal'],
                fontSize=10,
                leftIndent=20,
                spaceAfter=6,
            )
            text = '• ' + line[2:].strip()
            elements.append(Paragraph(text, style))
        elif line.startswith('```'):
            # Code block marker - skip
            continue
        else:
            # Normal paragraph
            style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
            )
            # Escape special characters for reportlab
            text = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            elements.append(Paragraph(text, style))
    
    # Build PDF
    doc.build(elements)
    print(f"[OK] Converted: {txt_path.name} -> {pdf_path.name}")


def main():
    """Main entry point."""
    print("[*] Converting text files to PDF...")
    print("=" * 60)
    
    # Define source and target directories
    demo_data_dir = _REPO_ROOT / "demo-data-ad"
    
    # Find all .txt files
    txt_files = list(demo_data_dir.rglob("*.txt"))
    
    if not txt_files:
        print("[WARN] No .txt files found in demo-data-ad/")
        return 0
    
    print(f"[INFO] Found {len(txt_files)} text file(s)")
    
    # Convert each file
    success_count = 0
    for txt_path in txt_files:
        try:
            # Create PDF path (same location, .pdf extension)
            pdf_path = txt_path.with_suffix('.pdf')
            
            # Convert
            convert_txt_to_pdf(txt_path, pdf_path)
            success_count += 1
            
        except Exception as e:
            print(f"[FAIL] Error converting {txt_path.name}: {e}")
    
    print("=" * 60)
    print(f"[INFO] Conversion complete: {success_count}/{len(txt_files)} successful")
    
    return 0 if success_count == len(txt_files) else 1


if __name__ == "__main__":
    sys.exit(main())
