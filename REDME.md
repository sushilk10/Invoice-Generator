Usage

-- Seller Info: Edit the multi-line text box at the top left to enter your company's full details (this goes into the PDF).
-- Buyer Details: Enter the client's name and address.
-- Invoice Details: Check the Invoice No. and Date. The Invoice No. automatically increments after a PDF is generated.
-- Add Items: Click the ➕ Add Item button to open a dialog where you can enter the description, quantity, and unit price for an item. Double-click an item in the list to edit it.
-- Tax Rate: Enter the desired tax percentage (e.g., 18.0) in the "Summary" box. Totals update instantly.

Actions:

-- 💾 Generate & Save PDF: Creates the final PDF, saves it to the invoices folder, and records the transaction in the CSV log.
-- 🔎 Preview Invoice: Opens a separate window to view the PDF before saving.
-- 🖨️ Print Invoice: Saves the PDF and attempts to send it to a selected printer.
-- 🔄 Reset All: Clears all buyer details and item lists for a new invoice.

Features 

-- Modern UI/UX: A clean, multi-pane layout styled with a clam theme and enhanced colors for a modern, layered look.
-- Clear Financial Breakdown: The generated PDF clearly labels Subtotal, Tax ($\dots\%$) and GRAND TOTAL for professional invoicing.
-- Item Management: Easily add, edit, and remove line items from the invoice.
-- Automatic Calculation: Calculates Tax Amount and Grand Total in real-time based on the item list and specified tax rate.
-- PDF Generation: Uses ReportLab to create high-quality, print-ready PDF invoices.
-- Invoice Tracking: Automatically saves essential invoice details (number, date, buyer, total) to a CSV file for record-keeping.
-- Preview & Print: Includes features to preview the generated PDF before saving/printing and a utility to send the invoice directly to a printer.-- Automatic Numbering: Automatically increments the invoice number for new invoices.


How to Run
Navigate to the directory containing the invoice_app.py file.

Execute the script using Python:
"Bash"
-- python -m venv .env (Tip this is for Windows User)
-- .env\Scripts\activate
-- pip install -r requirements.txt
-- python invoice_app.py
