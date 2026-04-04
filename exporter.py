from fpdf import FPDF
import datetime

class AuditPDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 12)
        self.cell(0, 10, 'LexiGuard AI - Proprietary Audit Report', 0, 1, 'R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_report(user, doc_name, summary, chat_history):
    pdf = AuditPDF()
    pdf.add_page()
    
    # Title Section
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, "Document Audit Results", ln=True)
    
    # Metadata Table
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 7, f"Lead Auditor: {user}", ln=True)
    pdf.cell(0, 7, f"Analyzed File: {doc_name}", ln=True)
    pdf.cell(0, 7, f"Audit Date: {datetime.datetime.now().strftime('%B %d, %Y')}", ln=True)
    pdf.ln(10)
    
    # Executive Summary
    pdf.set_font("Arial", 'B', 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "Executive Risk Summary", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_font("Arial", size=11)
    # Clean summary text for PDF encoding
    clean_summary = summary.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 7, txt=clean_summary)
    pdf.ln(10)
    
    # Q&A History
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Full Audit Intelligence (Q&A)", ln=True, fill=True)
    pdf.ln(2)
    
    for role, msg in chat_history:
        pdf.set_font("Arial", 'B', 10)
        label = "QUERY:" if role == "user" else "FINDING:"
        pdf.cell(0, 7, txt=label, ln=True)
        
        pdf.set_font("Arial", size=10)
        clean_msg = msg.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 6, txt=clean_msg)
        pdf.ln(4)

    # Return as bytes
    return pdf.output(dest='S')