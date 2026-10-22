import docx
from pathlib import Path
import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from generate_expanded_dissertation import (
    DOCS_DIR, TARGET_DOCX, FINAL_DOCX,
    IMG_LOGO, IMG_ARCH, IMG_CLASS, IMG_USECASE, IMG_WORKFLOW, IMG_GANTT,
    IMG_DASH, IMG_BATCH, IMG_AI, IMG_POS,
    set_cell_background, set_cell_margins, set_table_borders, add_field,
    add_custom_heading, add_body_p, add_bullet_p, add_numbered_p,
    add_caption, add_figure, add_styled_table, add_code_block
)

from text_chapters_1_to_3 import append_expanded_chapters_1_to_3
from text_chapters_4_to_5 import append_expanded_chapters_4_to_5
from text_chapters_6_to_8 import append_expanded_chapters_6_to_8_and_refs

def main():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.25)
        s.right_margin = Inches(1.0)

    # Section 1 (Front Matter)
    sec1 = doc.sections[0]
    sectPr1 = sec1._sectPr
    sectPr1.append(parse_xml(r'<w:pgNumType %s w:fmt="lowerRoman" w:start="1"/>' % nsdecls('w')))
    footer1 = sec1.footer
    p_f1 = footer1.paragraphs[0]
    p_f1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(p_f1, "PAGE")

    # Page 1: Cover
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

    # Declaration
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

    # Certificate
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

    # Acknowledgement
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

    # Executive Summary
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

    # Placeholders for TOC, Figures, Tables, Abbreviations, Symbols
    add_custom_heading(doc, "CONTENTS", level=1)
    p_toc = doc.add_paragraph("Table of Contents Placeholder - To be dynamically synchronized.")
    doc.add_page_break()
    doc.add_page_break()

    add_custom_heading(doc, "List of Figures", level=1)
    p_lof = doc.add_paragraph("List of Figures Placeholder.")
    doc.add_page_break()

    add_custom_heading(doc, "List of Tables", level=1)
    p_lot = doc.add_paragraph("List of Tables Placeholder.")
    doc.add_page_break()

    add_custom_heading(doc, "List of Abbreviations", level=1)
    p_loa = doc.add_paragraph("List of Abbreviations Placeholder.")
    doc.add_page_break()

    add_custom_heading(doc, "Symbols and Notations", level=1)
    p_sym = doc.add_paragraph("Symbols and Notations Placeholder.")

    # Section 2 (Body: Decimal Numerals 1, 2, 3...)
    sec2 = doc.add_section()
    sec2.header.is_linked_to_previous = False
    sec2.footer.is_linked_to_previous = False
    sectPr2 = sec2._sectPr
    sectPr2.append(parse_xml(r'<w:pgNumType %s w:fmt="decimal" w:start="1"/>' % nsdecls('w')))
    footer2 = sec2.footer
    p_f2 = footer2.paragraphs[0]
    p_f2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(p_f2, "PAGE")

    # Append Body Chapters
    append_expanded_chapters_1_to_3(doc, add_custom_heading, add_body_p, add_bullet_p, add_numbered_p, add_styled_table, add_caption)
    append_expanded_chapters_4_to_5(doc, add_custom_heading, add_body_p, add_bullet_p, add_numbered_p, add_styled_table, add_caption, add_figure, IMG_ARCH, IMG_CLASS, IMG_USECASE, IMG_GANTT)
    append_expanded_chapters_6_to_8_and_refs(doc, add_custom_heading, add_body_p, add_bullet_p, add_numbered_p, add_styled_table, add_caption, add_code_block, add_figure, IMG_WORKFLOW, IMG_DASH, IMG_BATCH, IMG_AI, IMG_POS)

    test_path = DOCS_DIR / "test_expanded.docx"
    doc.save(str(test_path))
    print("Test document built at", test_path)

if __name__ == "__main__":
    main()
