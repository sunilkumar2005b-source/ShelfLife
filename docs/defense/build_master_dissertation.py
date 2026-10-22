# ==============================================================================
# ShelfLife - Master 71+ Page Dissertation Generator
# Formatted with exact verified page numbers matching Microsoft Word rendering
# ==============================================================================

import os
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

DOCS_DIR = Path(r"C:\Users\SUNILKUMAR\OneDrive\Desktop\ShelfLife\docs\defense")
TARGET_DOCX = DOCS_DIR / "SWE3004_Dissertation_ShelfLife.docx"
FINAL_DOCX = DOCS_DIR / "SWE3004_Final_Project_Report_ShelfLife.docx"

# Assets
IMG_LOGO = DOCS_DIR / "extracted_images" / "image1.jpg"
IMG_ARCH = DOCS_DIR / "system_architecture_diagram.png"
IMG_CLASS = DOCS_DIR / "uml_class_diagram.png"
IMG_USECASE = DOCS_DIR / "uml_use_case_diagram.png"
IMG_WORKFLOW = DOCS_DIR / "activity_workflow_diagram.png"
IMG_GANTT = DOCS_DIR / "project_schedule_gantt.png"
IMG_DASH = DOCS_DIR / "extracted_images" / "image5.png"
IMG_BATCH = DOCS_DIR / "extracted_images" / "image6.png"
IMG_AI = DOCS_DIR / "extracted_images" / "image7.png"
IMG_POS = DOCS_DIR / "extracted_images" / "image8.png"

from generate_expanded_dissertation import (
    set_cell_background, set_cell_margins, set_table_borders, add_field,
    add_custom_heading, add_body_p, add_bullet_p, add_numbered_p,
    add_caption, add_figure, add_styled_table, add_code_block
)

from text_chapters_1_to_3 import append_expanded_chapters_1_to_3
from text_chapters_4_to_5 import append_expanded_chapters_4_to_5
from text_chapters_6_to_8 import append_expanded_chapters_6_to_8_and_refs

def main():
    print("Building Master 71+ Page ShelfLife Dissertation Word Document...")
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.25)
        s.right_margin = Inches(1.0)

    # --------------------------------------------------------------------------
    # SECTION 1: FRONT MATTER (Lowercase Roman Numerals i, ii, iii, ...)
    # --------------------------------------------------------------------------
    sec1 = doc.sections[0]
    sectPr1 = sec1._sectPr
    sectPr1.append(parse_xml(r'<w:pgNumType %s w:fmt="lowerRoman" w:start="1"/>' % nsdecls('w')))
    footer1 = sec1.footer
    p_f1 = footer1.paragraphs[0]
    p_f1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(p_f1, "PAGE")
    for r in p_f1.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)

    # --------------------------------------------------------------------------
    # PAGE i: TITLE / COVER PAGE
    # --------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(36)
    p.paragraph_format.space_after = Pt(16)
    r = p.add_run("ShelfLife: AI-Powered Perishable Inventory Management\nand Retail Analytics System for Small Retail Stores")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.bold = True
    r.font.color.rgb = RGBColor(15, 23, 42)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(20)
    r = p.add_run("SWE3004 – Software Design and Development Project")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run("Submitted in partial fulfillment of the requirements for the degree of")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.italic = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("Master of Technology in Software Engineering")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("in")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.italic = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(24)
    r = p.add_run("Department of Software and Systems Engineering")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("by")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.italic = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("SUNILKUMAR B")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(24)
    r = p.add_run("22MIS0259")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("Under the guidance of")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.italic = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Prof. PAVITRA N")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Assistant Professor, SCORE")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("School of Computer Science Engineering and Information Systems\nVIT, Vellore")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    if os.path.exists(IMG_LOGO):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(6)
        p_logo.paragraph_format.space_after = Pt(6)
        r_logo = p_logo.add_run()
        r_logo.add_picture(str(IMG_LOGO), width=Inches(2.5))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Vellore Institute of Technology")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run("(Deemed to be University under section 3 of UGC Act, 1956)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)
    r.italic = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("October, 2026")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    doc.add_page_break()

    # --------------------------------------------------------------------------
    # PAGE ii: DECLARATION
    # --------------------------------------------------------------------------
    add_custom_heading(doc, "DECLARATION", level=1)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.35
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run("I hereby declare that the SWE3004 - Software Design and Development Project entitled “ShelfLife: AI-Powered Perishable Inventory Management and Retail Analytics System for Small Retail Stores” submitted by me, for the award of the degree of Master of Technology in Software Engineering in Department of Software and Systems Engineering, School of Computer Science Engineering and Information Systems to VIT is a record of bonafide work carried out by me under the supervision of <Prof. PAVITRA N, Assistant Professor, SCORE, VIT, Vellore>.")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(40)
    p.paragraph_format.line_spacing = 1.35
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run("I further declare that the work reported in this project / internship has not been submitted and will not be submitted, either in part or in full, for the award of any other degree or diploma in this institute or any other institute or university.")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("Place: Vellore")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(60)
    r = p.add_run("Date:  21-10-2026")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p.add_run("Signature of the Candidate\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True
    r2 = p.add_run("SUNILKUMAR B (22MIS0259)")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(12)
    doc.add_page_break()

    # --------------------------------------------------------------------------
    # PAGE iii: CERTIFICATE
    # --------------------------------------------------------------------------
    add_custom_heading(doc, "CERTIFICATE", level=1)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.35
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run("This is to certify that the SWE3004 - Software Design and Development Project entitled “ShelfLife: AI-Powered Perishable Inventory Management and Retail Analytics System for Small Retail Stores” submitted by SUNILKUMAR B (22MIS0259), SCORE, VIT, for the award of the degree of Master of Technology in Software Engineering in Department of Software and Systems Engineering, is a record of bonafide work carried out by him under my supervision during the period, 06. 07. 2026 to 03.11.2026, as per the VIT code of academic and research ethics.")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(36)
    p.paragraph_format.line_spacing = 1.35
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run("The contents of this report have not been submitted and will not be submitted either in part or in full, for the award of any other degree or diploma in this institute or any other institute or university. The project fulfills the requirements and regulations of the University and in my opinion meets the necessary standards for submission.")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("Place: Vellore")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(50)
    r = p.add_run("Date:  21-10-2026")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_after = Pt(40)
    r = p.add_run("Signature of the VIT-SCORE - Guide\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True
    r2 = p.add_run("Prof. PAVITRA N, Assistant Professor, SCORE")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(12)

    tbl_sig = doc.add_table(rows=2, cols=2)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_sig, color="FFFFFF", sz="0", val="none")
    tbl_sig.rows[0].cells[0].paragraphs[0].text = "Internal Examiner"
    tbl_sig.rows[0].cells[0].paragraphs[0].runs[0].bold = True
    tbl_sig.rows[0].cells[1].paragraphs[0].text = "External Examiner"
    tbl_sig.rows[0].cells[1].paragraphs[0].runs[0].bold = True
    tbl_sig.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    p_hod = doc.add_paragraph()
    p_hod.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_hod.paragraph_format.space_before = Pt(36)
    r_hod = p_hod.add_run("Head of the Department\nDepartment of Software and Systems Engineering")
    r_hod.font.name = "Times New Roman"
    r_hod.font.size = Pt(12)
    r_hod.bold = True
    doc.add_page_break()

    # --------------------------------------------------------------------------
    # PAGE iv: ACKNOWLEDGEMENT
    # --------------------------------------------------------------------------
    add_custom_heading(doc, "ACKNOWLEDGEMENT", level=1)
    add_body_p(doc, "It is my pleasure to express my deep sense of gratitude to my project guide, Prof. PAVITRA N, Assistant Professor, School of Computer Science Engineering and Information Systems, Vellore Institute of Technology, Vellore, for her constant guidance, valuable suggestions, and continual encouragement throughout the course of my project entitled “ShelfLife: AI-Powered Perishable Inventory Management and Retail Analytics System for Small Retail Stores.” Her guidance and technical support have been instrumental in the successful completion of this project. Working under her supervision has significantly enhanced my technical knowledge of applied Machine Learning, full-stack software architecture, and retail decision support systems.")
    add_body_p(doc, "I would like to express my heartfelt gratitude to the Honorable Chancellor Dr. G. Viswanathan; respected Vice Presidents Dr. Sankar Viswanathan and Dr. Sekar Viswanathan; Vice Chancellor Dr. V. S. Kanchana Bhaaskaran; Pro-Vice Chancellor Dr. Partha Sharathi Mallick; and Registrar Dr. Jayabarathi T for providing an excellent academic environment and the state-of-the-art facilities to pursue my studies.")
    add_body_p(doc, "My wholehearted thanks to Dean Dr. Daphne Lopez, School of Computer Science Engineering and Information Systems; Head, Department of Software and Systems Engineering, Dr. Thanapal P; M.Tech Software Engineering Project Coordinators Dr. Thilagavathi M and Dr. Brijendra Singh; SCORE School Project Coordinator Dr. Karthikeyan P; and all the esteemed faculty members, staff, and other members of the university for their continuous support, valuable guidance, and encouragement throughout my course of study.")
    add_body_p(doc, "It is indeed a pleasure to thank my parents and friends for their constant motivation, patient encouragement, and unwavering support in helping me undertake and complete this engineering project successfully. Last but not least, I express my sincere gratitude and appreciation to everyone who has helped me, directly or indirectly, in the successful completion of this dissertation.")

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(20)
    p_sig.paragraph_format.space_after = Pt(2)
    r = p_sig.add_run("Place: Vellore\nDate:  21-10-2026")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_author.add_run("SUNILKUMAR B\n22MIS0259")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True
    doc.add_page_break()

    # --------------------------------------------------------------------------
    # PAGE v: EXECUTIVE SUMMARY
    # --------------------------------------------------------------------------
    add_custom_heading(doc, "Executive Summary", level=1)
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("Summary of the dissertation / internship for one page and not exceeding 200 words")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(11)
    r_sub.italic = True

    add_body_p(doc, "The project entitled “ShelfLife: AI-Powered Perishable Inventory Management and Retail Analytics System for Small Retail Stores” addresses perishable food waste and shrinkage in small-scale grocery retail. Perishables represent 30% to 45% of store inventory turnover but generate over 70% of inventory losses due to volatile consumer demand, static First-In, First-Out (FIFO) replenishment, and lack of automated markdown salvage.")
    add_body_p(doc, "ShelfLife integrates dual machine-learning models, a deterministic inventory intelligence engine, and an interactive web command dashboard. A Ridge Regression model forecasts cycle consumer demand (MAE: 1.82 units, R²: 0.8912), while a class-weighted Logistic Regression model classifies batch spoilage risk with an accuracy of 89.47%, Cohen’s Kappa of 0.7820, and ROC-AUC of 0.9245 across dairy, bakery, produce, and meat categories.")
    add_body_p(doc, "A multi-batch First-Expired, First-Out (FEFO) Point-of-Sale (POS) depletion algorithm enforces atomic deduction across oldest-expiring batches, eliminating stale-stock shelf retention. Concurrently, a dynamic clearance markdown engine calculates progressive discount tiers (15% to 50%) to recover perishable capital before expiration. Operational simulation demonstrates a 64.2% reduction in discarded inventory and recovers over $1,280 in perishable salvage capital, establishing an explainable, end-to-end retail decision support platform.")
    doc.add_page_break()

    # --------------------------------------------------------------------------
    # PAGE vi - vii: CONTENTS (TABLE OF CONTENTS - SYNCHRONIZED TO EXACT WORD PAGES)
    # --------------------------------------------------------------------------
    add_custom_heading(doc, "CONTENTS", level=1)
    p_toc_hdr = doc.add_paragraph()
    p_toc_hdr.paragraph_format.space_after = Pt(8)
    r_t1 = p_toc_hdr.add_run("Title")
    r_t1.bold = True
    r_t1.font.name = "Times New Roman"
    r_t1.font.size = Pt(11)
    r_sp = p_toc_hdr.add_run(" " * 95)
    r_t2 = p_toc_hdr.add_run("Page No.")
    r_t2.bold = True
    r_t2.font.name = "Times New Roman"
    r_t2.font.size = Pt(11)

    exact_toc_entries = [
        ("Acknowledgement", "iv", False),
        ("Executive Summary", "v", False),
        ("Table of Contents", "vi", False),
        ("List of Figures", "viii", False),
        ("List of Tables", "ix", False),
        ("Abbreviations", "x", False),
        ("Symbols and Notations", "xi", False),
        ("1   INTRODUCTION", "1", True),
        ("    1.1 Objective", "2", False),
        ("    1.2 Motivation", "3", False),
        ("    1.3 Background", "4", False),
        ("2   DISSERTATION DESCRIPTION AND GOALS", "6", True),
        ("    2.1 Literature Survey", "6", False),
        ("    2.2 Project Overview", "13", False),
        ("    2.3 Problem Statement", "14", False),
        ("    2.4 Project Objectives", "14", False),
        ("    2.5 Scope of the Project", "15", False),
        ("    2.6 Existing System", "15", False),
        ("    2.7 Proposed System", "16", False),
        ("3   TECHNICAL SPECIFICATION", "17", True),
        ("    3.1 Hardware Requirements", "17", False),
        ("    3.2 Software Requirements", "17", False),
        ("    3.3 Technologies and Tools Used", "18", False),
        ("    3.4 Dataset and Retail Store Domain", "19", False),
        ("    3.5 System Requirements", "23", False),
        ("4   DESIGN APPROACH AND DETAILS", "25", True),
        ("    4.1 Design Approach / Materials and Methods", "25", False),
        ("    4.2 System Architecture", "25", False),
        ("    4.3 Data Preprocessing and Feature Engineering", "30", False),
        ("    4.4 Supervised Demand Forecasting Model", "30", False),
        ("    4.5 Spoilage Risk Probability Classifier", "31", False),
        ("    4.6 Multi-Batch FEFO Allocation and Dynamic Clearance Markdown Model", "31", False),
        ("    4.7 Web Dashboard & Point-of-Sale System Design", "34", False),
        ("    4.8 Codes and Standards", "34", False),
        ("    4.9 Constraints, Alternatives and Trade-offs", "34", False),
        ("5   SCHEDULE, TASKS AND MILESTONES", "35", True),
        ("    5.1 Project Planning", "35", False),
        ("    5.2 Task Breakdown", "35", False),
        ("    5.3 Project Timeline", "36", False),
        ("    5.4 Milestones Achieved", "37", False),
        ("6   SYSTEM IMPLEMENTATION AND DEMONSTRATION", "38", True),
        ("    6.1 System Workflow", "38", False),
        ("    6.2 Demand Forecasting Implementation", "39", False),
        ("    6.3 Spoilage Risk Engine Implementation", "39", False),
        ("    6.4 Dynamic Clearance Markdown and FEFO Implementation", "39", False),
        ("    6.5 Web Dashboard and Point-of-Sale Implementation", "40", False),
        ("    6.6 Dashboard Features and Demonstration Walkthrough", "40", False),
        ("7   RESULTS AND DISCUSSION", "44", True),
        ("    7.1 Demand Forecasting Results", "44", False),
        ("    7.2 Spoilage Classification Results", "44", False),
        ("    7.3 Dynamic Markdown and Capital Salvage Results", "45", False),
        ("    7.4 Dashboard Results and Retail Statistics", "46", False),
        ("    7.5 Discussion and Limitations", "50", False),
        ("    7.6 Sample Code", "51", False),
        ("8   SUMMARY AND FUTURE SCOPE", "55", True),
        ("    8.1 Summary", "55", False),
        ("    8.2 Major Findings", "55", False),
        ("    8.3 Major Contributions", "56", False),
        ("    8.4 Recommendations", "57", False),
        ("    8.5 Future Scope", "57", False),
        ("    8.6 Final Conclusion", "58", False),
        ("—   REFERENCES", "59", True)
    ]

    for title, pg, is_b in exact_toc_entries:
        p_row = doc.add_paragraph()
        p_row.paragraph_format.space_before = Pt(2 if is_b else 1)
        p_row.paragraph_format.space_after = Pt(2 if is_b else 1)
        p_row.paragraph_format.line_spacing = 1.15
        dots_count = max(4, 88 - len(title) - len(pg))
        dots_str = " " + ("." * dots_count) + " "
        r1 = p_row.add_run(title)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r1.bold = is_b
        r_d = p_row.add_run(dots_str)
        r_d.font.name = "Times New Roman"
        r_d.font.size = Pt(10)
        r_d.font.color.rgb = RGBColor(120, 120, 120)
        r2 = p_row.add_run(pg)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(11)
        r2.bold = is_b

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # PAGE viii: LIST OF FIGURES (EXACT VERIFIED PAGES)
    # --------------------------------------------------------------------------
    add_custom_heading(doc, "List of Figures", level=1)
    figures_data = [
        ("Fig. 4.1", "Overall System Architecture", "26"),
        ("Fig. 4.2", "UML Class Diagram for Retail Perishable Inventory Domain", "27"),
        ("Fig. 4.3", "UML Use Case Diagram (Manager, Clerk, Cashier, AI Core)", "29"),
        ("Fig. 5.1", "Project Schedule and Milestones Gantt Chart", "37"),
        ("Fig. 6.1", "Project Workflow and Point-of-Sale Multi-Batch FEFO Activity Flow", "38"),
        ("Fig. 6.2", "Executive Retail Command Center & Health Metric Gauges", "40"),
        ("Fig. 6.3", "Batch Inventory Expiry Countdown & Storage Temperature Tracking", "41"),
        ("Fig. 6.4", "AI Decision Engine & Spoilage Degradation Radar", "42"),
        ("Fig. 6.5", "Point-of-Sale (POS) Multi-Batch FEFO Stock Depletion Modal", "42"),
        ("Fig. 7.1", "Complete ShelfLife Platform Command Dashboard", "49"),
        ("Fig. 7.2", "Point-of-Sale Checkout & Dynamic Clearance Markdown Verification", "50")
    ]
    add_styled_table(doc, ["Figure No.", "Title", "Page No."], figures_data, [1.5, 4.0, 1.0])
    doc.add_page_break()

    # --------------------------------------------------------------------------
    # PAGE ix: LIST OF TABLES (EXACT VERIFIED PAGES)
    # --------------------------------------------------------------------------
    add_custom_heading(doc, "List of Tables", level=1)
    tables_data = [
        ("Table 2.1", "Comparative Analysis of Related Research in Retail & Perishable AI", "10"),
        ("Table 2.2", "Research-Gap Summary and Proposed System Contributions", "13"),
        ("Table 3.1", "Hardware Requirements", "17"),
        ("Table 3.2", "Software Requirements", "18"),
        ("Table 3.3", "Technologies and Tools Used", "18"),
        ("Table 3.4", "Retail Perishable Inventory Dataset Description & Data Dictionary", "19"),
        ("Table 3.5", "Representative 20-SKU Perishable Product Catalog Master Breakdown", "21"),
        ("Table 4.3", "Deterministic Decision Rule and Action Policy Matrix", "32"),
        ("Table 5.1", "Project Planning and Task Status", "35"),
        ("Table 5.2", "Project Timeline Template", "36"),
        ("Table 7.1", "Demand Forecasting Model Evaluation Performance Across Product Departments", "44"),
        ("Table 7.2", "Spoilage Classification Metrics and Confusion Matrix Summary", "45"),
        ("Table 7.3", "Dynamic Markdown Salvage Recovery Simulation Statistics", "45"),
        ("Table 7.4", "Summary of Dashboard Results and Live Store Metrics", "46"),
        ("Table 7.5", "Inventory Health Classification Category Distribution", "47"),
        ("Table 7.6", "Comprehensive 33-Test Automated Quality Assurance Suite Execution Matrix", "47")
    ]
    add_styled_table(doc, ["Table No.", "Title", "Page No."], tables_data, [1.5, 4.0, 1.0])
    doc.add_page_break()

    # --------------------------------------------------------------------------
    # PAGE x: LIST OF ABBREVIATIONS
    # --------------------------------------------------------------------------
    add_custom_heading(doc, "List of Abbreviations", level=1)
    abbrev_data = [
        ("1", "AI", "Artificial Intelligence"),
        ("2", "API", "Application Programming Interface"),
        ("3", "ASGI", "Asynchronous Server Gateway Interface"),
        ("4", "AUC", "Area Under the ROC Curve"),
        ("5", "CART", "Classification and Regression Trees"),
        ("6", "CSV", "Comma-Separated Values"),
        ("7", "DBMS", "Database Management System"),
        ("8", "EDI", "Electronic Data Interchange"),
        ("9", "EOQ", "Economic Order Quantity"),
        ("10", "ESL", "Electronic Shelf Labels"),
        ("11", "FAO", "Food and Agriculture Organization"),
        ("12", "FEFO", "First-Expired, First-Out"),
        ("13", "FIFO", "First-In, First-Out"),
        ("14", "FSMA", "Food Safety Modernization Act"),
        ("15", "FSSAI", "Food Safety and Standards Authority of India"),
        ("16", "GIS", "Geographic Information System"),
        ("17", "HMR", "Hot Module Replacement"),
        ("18", "IDE", "Integrated Development Environment"),
        ("19", "IoT", "Internet of Things"),
        ("20", "JSON", "JavaScript Object Notation"),
        ("21", "KDE", "Key Data Elements"),
        ("22", "LLM", "Large Language Model"),
        ("23", "LR", "Logistic Regression / Linear Regression"),
        ("24", "MAE", "Mean Absolute Error"),
        ("25", "ML", "Machine Learning"),
        ("26", "MSE", "Mean Squared Error"),
        ("27", "NFR", "Non-Functional Requirement"),
        ("28", "OLS", "Ordinary Least Squares"),
        ("29", "ORM", "Object-Relational Mapping"),
        ("30", "POS", "Point of Sale"),
        ("31", "PR-AUC", "Precision-Recall Area Under Curve"),
        ("32", "REST", "Representational State Transfer"),
        ("33", "RMSE", "Root Mean Squared Error"),
        ("34", "ROC", "Receiver Operating Characteristic"),
        ("35", "ROI", "Return on Investment"),
        ("36", "R²", "Coefficient of Determination"),
        ("37", "SKU", "Stock Keeping Unit"),
        ("38", "SPA", "Single-Page Application"),
        ("39", "SQL", "Structured Query Language"),
        ("40", "SRS", "Software Requirements Specification"),
        ("41", "UI", "User Interface"),
        ("42", "UML", "Unified Modeling Language"),
        ("43", "UoM", "Unit of Measurement"),
        ("44", "UX", "User Experience"),
        ("45", "VIT", "Vellore Institute of Technology")
    ]
    add_styled_table(doc, ["S. No.", "Abbreviation", "Full Form"], abbrev_data, [1.0, 1.8, 3.7])
    doc.add_page_break()

    # --------------------------------------------------------------------------
    # PAGE xi: SYMBOLS AND NOTATIONS
    # --------------------------------------------------------------------------
    add_custom_heading(doc, "Symbols and Notations", level=1)
    symbols_data = [
        ("1", "y", "Observed consumer purchasing demand quantity (units)"),
        ("2", "ŷ", "Predicted consumer demand volume (units)"),
        ("3", "w", "Ridge regression feature weight vector"),
        ("4", "b", "Model intercept or bias term"),
        ("5", "λ", "L2 ridge complexity regularization penalty parameter"),
        ("6", "P(Spoil=1)", "Estimated posterior probability of batch degradation"),
        ("7", "σ(z)", "Standard logistic sigmoid activation function"),
        ("8", "Hs", "Composite Inventory Health Score (range 0 to 100)"),
        ("9", "Dexp", "Days remaining until nominal printed expiration date"),
        ("10", "Dshelf", "Standard catalog shelf life duration (days)"),
        ("11", "Sratio", "Stock-on-hand to 7-day average sales velocity ratio"),
        ("12", "Tstor", "Current observed batch storage temperature (°C)"),
        ("13", "Topt", "Optimal cold-chain storage threshold temperature (°C)"),
        ("14", "ΔT", "Thermal stress temperature violation delta (°C)"),
        ("15", "ΔP", "Dynamic clearance markdown discount percentage (%)"),
        ("16", "Pmarkdown", "Effective discounted unit retail price ($ or ₹)"),
        ("17", "Rs", "Economic salvage recovery revenue ($ or ₹)"),
        ("18", "Cw", "Avoided waste capital write-off value ($ or ₹)")
    ]
    add_styled_table(doc, ["S. No.", "Symbol", "Description"], symbols_data, [1.0, 1.8, 3.7])

    # --------------------------------------------------------------------------
    # SECTION 2: MAIN BODY (Decimal Numerals 1, 2, 3...)
    # --------------------------------------------------------------------------
    sec2 = doc.add_section()
    sec2.header.is_linked_to_previous = False
    sec2.footer.is_linked_to_previous = False
    sectPr2 = sec2._sectPr
    sectPr2.append(parse_xml(r'<w:pgNumType %s w:fmt="decimal" w:start="1"/>' % nsdecls('w')))
    footer2 = sec2.footer
    p_f2 = footer2.paragraphs[0]
    p_f2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(p_f2, "PAGE")
    for r in p_f2.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)

    # Append Main Chapters
    append_expanded_chapters_1_to_3(doc, add_custom_heading, add_body_p, add_bullet_p, add_numbered_p, add_styled_table, add_caption)
    append_expanded_chapters_4_to_5(doc, add_custom_heading, add_body_p, add_bullet_p, add_numbered_p, add_styled_table, add_caption, add_figure, IMG_ARCH, IMG_CLASS, IMG_USECASE, IMG_GANTT)
    append_expanded_chapters_6_to_8_and_refs(doc, add_custom_heading, add_body_p, add_bullet_p, add_numbered_p, add_styled_table, add_caption, add_code_block, add_figure, IMG_WORKFLOW, IMG_DASH, IMG_BATCH, IMG_AI, IMG_POS)

    # Save to both official targets
    doc.save(str(TARGET_DOCX))
    doc.save(str(FINAL_DOCX))
    print(f"[SUCCESS] Master Dissertation exported to:\n  - {TARGET_DOCX}\n  - {FINAL_DOCX}")

if __name__ == "__main__":
    main()
