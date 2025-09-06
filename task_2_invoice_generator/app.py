import os
from io import BytesIO

from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


app = Flask(__name__)

# The font name and file path. We assume the font file is in the same directory.
FONT_FILE_NAME = 'DejaVuSans.ttf'
FONT_FILE = os.path.join(os.path.dirname(__file__), FONT_FILE_NAME)
FONT_NAME = 'DejaVuSansFix' # Changed font name to avoid caching issues

# Register the font at application startup.
# We check for its existence to provide a clear error message if it's not found.
if os.path.exists(FONT_FILE):
    print(f"Font file found at: {FONT_FILE}")
    try:
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))
        print(f"Font '{FONT_NAME}' registered successfully.")
    except Exception as e:
        print(f"Error registering font: {e}")
        print("Please ensure the DejaVuSans.ttf file is not corrupted.")
        
else:
    print(f"Error: Font file not found at {FONT_FILE}")
    print("Please ensure the DejaVuSans.ttf file is in the same directory as app.py")


# This route serves the HTML form for the user to fill out.
@app.route('/')
def index():
    return render_template('invoice_form.html')

# This route processes the form data and generates the PDF invoice.
@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    # Get all the data submitted from the HTML form.
    invoice_number = request.form['invoice_number']
    bill_to = request.form['bill_to']
    date = request.form['date']
    item_descriptions = request.form.getlist('item_description[]')
    item_quantities = request.form.getlist('item_quantity[]')
    item_prices = request.form.getlist('item_price[]')
    currency = request.form['currency']
    
    # Set the exchange rate for USD to INR.
    usd_to_inr_rate = 83.5
    
    # Calculate the total cost for each item and the overall subtotal.
    subtotal = 0
    items_raw = []
    for desc, quant, price in zip(item_descriptions, item_quantities, item_prices):
        try:
            quantity = int(quant)
            item_price = float(price)
            item_total = quantity * item_price
            subtotal += item_total
            
            # Format the items with the correct currency symbol.
            if currency == 'USD':
                items_raw.append([desc, quantity, f"${item_price:.2f}", f"${item_total:.2f}"])
            else:
                items_raw.append([desc, quantity, f"₹{item_price:.2f}", f"₹{item_total:.2f}"])
        except (ValueError, TypeError):
            continue
            
    tax_rate = 0.08
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount

    # Convert totals to the other currency for display.
    if currency == 'USD':
        subtotal_inr = subtotal * usd_to_inr_rate
        tax_amount_inr = tax_amount * usd_to_inr_rate
        total_inr = total * usd_to_inr_rate
        subtotal_display = f"${subtotal:.2f} (₹{subtotal_inr:.2f})"
        tax_display = f"${tax_amount:.2f} (₹{tax_amount_inr:.2f})"
        total_display = f"<b>${total:.2f} (₹{total_inr:.2f})</b>"
    else:
        subtotal_usd = subtotal / usd_to_inr_rate
        tax_amount_usd = tax_amount / usd_to_inr_rate
        total_usd = total / usd_to_inr_rate
        subtotal_display = f"₹{subtotal:.2f} (${subtotal_usd:.2f})"
        tax_display = f"₹{tax_amount:.2f} (${tax_amount_usd:.2f})"
        total_display = f"<b>₹{total:.2f} (${total_usd:.2f})</b>"

    # Prepare to build the PDF document.
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Define a new style that uses the Unicode font for the totals.
    styles = getSampleStyleSheet()
    unicode_style = ParagraphStyle(
        'Normal',
        fontName=FONT_NAME,
        fontSize=12,
    )
    
    # Add a title and key details to the PDF.
    elements.append(Paragraph("<b>INVOICE</b>", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Invoice Number:</b> {invoice_number}", styles['Normal']))
    elements.append(Paragraph(f"<b>Date:</b> {date}", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Bill To:</b><br/>{bill_to.replace('\\n', '<br/>')}", styles['Normal']))
    elements.append(Spacer(1, 24))

    # Create the table for the items list.
    data = [['Description', 'Quantity', 'Price', 'Total']]
    
    # Wrap all currency cells in a Paragraph with the correct font.
    for item in items_raw:
        data.append([
            Paragraph(item[0], unicode_style),
            Paragraph(str(item[1]), unicode_style),
            Paragraph(item[2], unicode_style),
            Paragraph(item[3], unicode_style)
        ])
    
    # Add the totals to the bottom of the table.
    data.append(['', '', Paragraph('Subtotal:', unicode_style), Paragraph(subtotal_display, unicode_style)])
    data.append(['', '', Paragraph('Tax:', unicode_style), Paragraph(tax_display, unicode_style)])
    data.append(['', '', Paragraph('<b>Total:</b>', unicode_style), Paragraph(total_display, unicode_style)])

    table = Table(data)
    
    # Apply styling to the table.
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT')
    ])
    table.setStyle(style)
    elements.append(table)
    
    doc.build(elements)
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'invoice_{invoice_number}.pdf', mimetype='application/pdf')

# This block ensures the application runs when the script is executed directly.
if __name__ == '__main__':
    app.run(debug=True)




