#!/usr/bin/env python3
"""Convert Markdown file to PDF. Tries pandoc, then wkhtmltopdf via pdfkit, then falls back to reportlab simple text PDF."""
import sys, subprocess, os
def run_cmd(cmd):
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except Exception as e:
        return False
def pandoc(md, out):
    return run_cmd(f"pandoc '{md}' -o '{out}'")
def wkhtmltopdf(md, out):
    try:
        import pdfkit, markdown
        html = markdown.markdown(open(md).read())
        pdfkit.from_string(html, out)
        return True
    except Exception as e:
        return False
def reportlab_fallback(md, out):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        text = open(md).read()
        c = canvas.Canvas(out, pagesize=letter)
        width, height = letter
        lines = text.split('\n')
        y = height - 72
        for line in lines:
            c.drawString(72, y, line[:100])
            y -= 12
            if y < 72:
                c.showPage(); y = height - 72
        c.save()
        return True
    except Exception as e:
        return False
if __name__=='__main__':
    if len(sys.argv)<3:
        print('Usage: md_to_pdf.py input.md output.pdf'); sys.exit(1)
    md=sys.argv[1]; out=sys.argv[2]
    if pandoc(md, out):
        print('WROTE', out); sys.exit(0)
    if wkhtmltopdf(md, out):
        print('WROTE', out); sys.exit(0)
    if reportlab_fallback(md, out):
        print('WROTE (fallback)', out); sys.exit(0)
    print('Failed to convert. Install pandoc or wkhtmltopdf or reportlab.'); sys.exit(2)
