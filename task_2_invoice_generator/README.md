Invoice Generator
This is a Python-based web application built with Flask that generates professional PDF invoices. Users can input invoice details, item descriptions, quantities, and prices, and the application will create a clean, printable PDF with calculated totals.

A key feature of this application is its ability to correctly render both the US Dollar ($) and Indian Rupee (₹) symbols in the generated PDF, which was achieved by using a Unicode-compatible font.

Setup and Installation
To run this application, follow these steps:

Clone the repository: If you haven't already, clone the project from GitHub.

Install dependencies: Make sure you have Python installed, then install the required libraries.

pip install Flask reportlab

Download the font: This application requires a Unicode font to display the Rupee symbol correctly. Download the DejaVuSans.ttf file from the official DejaVu project and place it in the same directory as the app.py file.

Run the application:

python app.py

Usage
Open your web browser and navigate to http://127.0.0.1:5000.

Fill in the invoice details and item information on the form.

Click the "Generate Invoice" button to download the PDF.