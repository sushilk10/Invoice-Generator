"""
Upgraded Invoice Generator
Tkinter + ReportLab + Enhanced UI/UX + Edit/Delete Features
FIXED: NameError: name 'ACCENT_BLUE' is not defined
"""

import os
import csv
import datetime
import subprocess
import platform
from tkinter import (
    Tk, StringVar, IntVar, DoubleVar, Toplevel,
    Label, Entry, Button, Frame, LEFT, RIGHT, X, Y, BOTH, TOP, BOTTOM, END, W, E, CENTER, filedialog, Text, Canvas
)
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk 

# Conditional import for pywin32 (for Windows printing)
try:
    import win32api
    import win32print
    WIN32_AVAILABLE = True
except ImportError:
    win32api = None
    win32print = None
    WIN32_AVAILABLE = False

import fitz # PyMuPDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------- Config ----------
INVOICE_DIR = "invoices"
INVOICE_CSV = os.path.join(INVOICE_DIR, "invoices.csv")
os.makedirs(INVOICE_DIR, exist_ok=True)

# ---------- Helper Functions ----------
def currency_fmt(x):
    """Formats a float/string into a currency string (e.g., ₹1,234.56)"""
    try:
        if isinstance(x, str):
            x = x.replace('₹', '').replace(',', '').strip()
        # Formatting with comma separators
        return f"₹{float(x):,.2f}"
    except Exception:
        return "₹0.00"

def currency_to_float(x):
    """Converts a currency string back to a float"""
    try:
        if isinstance(x, str):
            return float(x.replace('₹', '').replace(',', '').strip())
        return float(x)
    except Exception:
        return 0.0

def next_invoice_number():
    n = 1
    if os.path.exists(INVOICE_CSV):
        try:
            with open(INVOICE_CSV, newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))
                if len(rows) > 1:
                    # Get the last invoice number from the first column and increment
                    n = int(rows[-1][0]) + 1
        except Exception:
            # Fallback in case CSV is corrupted
            n = len([f for f in os.listdir(INVOICE_DIR) if f.startswith("Invoice_") and f.endswith(".pdf")]) + 1
    return n

def generate_pdf(invoice_number, date_str, seller_info, buyer_info, items, subtotal, tax_percent, tax_amount, total_amount, notes="", pdf_path=None):
    if pdf_path is None:
        pdf_path = os.path.join(INVOICE_DIR, f"Invoice_{invoice_number:04d}.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    story = []

    # Title and Metadata
    story.append(Paragraph("<b>INVOICE</b>", styles['Title']))
    story.append(Spacer(1, 6))
    meta_table_data = [["Invoice No:", f"{invoice_number:04d}", "Date:", date_str]]
    meta = Table(meta_table_data, colWidths=[60*mm, 60*mm, 30*mm, 30*mm])
    story.append(meta)
    story.append(Spacer(1, 12))

    # Seller/Buyer Info
    seller_par = Paragraph(f"<b>Seller:</b><br/>{seller_info.replace(chr(10), '<br/>')}", styles['Normal'])
    buyer_par = Paragraph(f"<b>Buyer:</b><br/>{buyer_info.replace(chr(10), '<br/>')}", styles['Normal'])
    party_table = Table([[seller_par, buyer_par]], colWidths=[90*mm, 90*mm])
    party_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(party_table)
    story.append(Spacer(1, 12))

    # Items Table
    data = [["#", "Description", "Qty", "Unit Price", "Total"]]
    for idx, it in enumerate(items, start=1):
        line_total = it['qty']*it['unit_price']
        # IMPORTANT: Use currency_fmt for financial values in the PDF table
        data.append([str(idx), it['desc'], str(it['qty']), currency_fmt(it['unit_price']), currency_fmt(line_total)])

    # Totals in Table
    # ENHANCEMENT: Clearly label Subtotal, Tax, and Total
    data.append(["", "", "", "Subtotal:", currency_fmt(subtotal)])
    data.append(["", "", "", f"Tax ({tax_percent:.2f}%):", currency_fmt(tax_amount)]) 
    data.append(["", "", "", "GRAND TOTAL:", currency_fmt(total_amount)])

    table = Table(data, colWidths=[15*mm, 95*mm, 20*mm, 30*mm, 30*mm])
    last_row = len(data) - 1
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,last_row-3), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (2,1), (4,last_row-3), 'CENTER'),
        ('ALIGN', (3,1), (4,last_row-3), 'RIGHT'), # Align Price/Total columns right

        # Totals Section Styling
        ('ALIGN', (3,last_row-2), (3,last_row), 'LEFT'),  # Align labels (Subtotal, Tax, Total) to the LEFT of the 4th column
        ('ALIGN', (4,last_row-2), (4,last_row), 'RIGHT'), # Align amounts to the RIGHT of the 5th column
        
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (3,last_row-2), (3,last_row-2), 'Helvetica-Bold'),
        ('FONTNAME', (3,last_row-1), (3,last_row-1), 'Helvetica-Bold'),
        ('FONTNAME', (3,last_row), (4,last_row), 'Helvetica-Bold'), # Make total amount and label bold
        ('LINEBELOW', (3,last_row-1), (4,last_row-1), 1, colors.black), # Line above Total
        ('LINEABOVE', (3,last_row), (4,last_row), 1.5, colors.black), # Double Line under Total
    ]))
    story.append(table)
    story.append(Spacer(1,12))

    # Notes
    if notes.strip():
        story.append(Paragraph(f"<b>Notes:</b><br/>{notes.replace(chr(10), '<br/>')}", styles['Normal']))
        story.append(Spacer(1,12))

    story.append(Paragraph("Thank you for your business!", styles['Normal']))
    doc.build(story)
    return pdf_path

# ... (print_pdf and preview_pdf functions remain the same as the user's working versions) ...

def print_pdf(file_path, printer_name=None):
    try:
        system = platform.system()
        if system == "Windows":
            if WIN32_AVAILABLE:
                if printer_name is None:
                    printer_name = win32print.GetDefaultPrinter()

                win32api.ShellExecute(
                    0,
                    "printto",
                    file_path,
                    f'"{printer_name}"',
                    ".",
                    0
                )
                messagebox.showinfo("Printing Success", f"Invoice sent to **{printer_name}** via Standard Print method.")
            else:
                messagebox.showwarning("Missing pywin32", "pywin32 not installed.\nCannot print directly on Windows.")
        
        elif system in ["Linux", "Darwin"]:
            subprocess.call(["lp", file_path])
            messagebox.showinfo("Printing", "Invoice sent to default system printer ('lp' command used).")
        else:
            messagebox.showinfo("Print Error", f"Unsupported OS.\nPDF saved at {file_path}")
    except Exception as e:
        messagebox.showerror("Print Error", f"Could not print automatically.\nPDF saved at {file_path}\nError: {e}")

def preview_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        page = doc.load_page(0)
        # Use a higher resolution for a better preview
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0)) 
        
        img_data = pix.samples
        img = Image.frombytes("RGB", [pix.width, pix.height], img_data)

        top = Toplevel()
        top.title("Invoice Preview")
        top.configure(bg='#333333') # Dark background for the preview window
        
        tk_img = ImageTk.PhotoImage(img)
        
        # Use a fixed canvas size for better control over the preview
        canvas = Canvas(top, width=700, height=800, bg='#444444')
        v_scroll = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
        h_scroll = ttk.Scrollbar(top, orient="horizontal", command=canvas.xview)
        
        v_scroll.pack(side=RIGHT, fill=Y)
        h_scroll.pack(side=BOTTOM, fill=X)
        canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)

        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        img_frame = Frame(canvas, bg='white', relief='raised', bd=1) 
        # Center the image frame within the canvas
        canvas.create_window((10, 10), window=img_frame, anchor="nw", tags="image_frame")
        
        preview_label = Label(img_frame, image=tk_img, bg='white')
        preview_label.pack(padx=15, pady=15)

        img_frame.update_idletasks()
        # Set scrollregion based on image frame size
        canvas.config(scrollregion=canvas.bbox("all")) 

        top.image = tk_img
        
        top.update_idletasks()
        w = top.winfo_screenwidth()
        h = top.winfo_screenheight()
        size = tuple(int(_) for _ in top.geometry().split('+')[0].split('x'))
        x = w/2 - size[0]/2
        y = h/2 - size[1]/2
        top.geometry("+%d+%d" % (x, y))

    except Exception as e:
        messagebox.showerror("Preview Error", f"Cannot preview PDF:\n{e}\n\nEnsure 'Pillow' (pip install Pillow) and 'PyMuPDF' (pip install PyMuPDF) are installed.")


# ---------- Main App ----------
class InvoiceApp:
    def __init__(self, root):
        self.root = root
        root.title("Invoice Generator Pro")
        root.geometry("1100x800")
        
        # --- UI Variables ---
        self.seller_text = StringVar(value="Your Business Name\n123 Business St\nCity, State, ZIP\nPhone: (555) 123-4567\nEmail: info@yourbusiness.com")
        self.buyer_name = StringVar()
        self.buyer_address = StringVar()
        self.invoice_number = IntVar(value=next_invoice_number())
        self.invoice_date = StringVar(value=datetime.date.today().isoformat())
        self.tax_percent = DoubleVar(value=18.0)
        self.subtotal = StringVar(value=currency_fmt(0.0))
        self.tax_amount = StringVar(value=currency_fmt(0.0))
        self.total_amount = StringVar(value=currency_fmt(0.0))
        self.items = []
        self.last_pdf_path = None 

        # --- Color Palette (DEFINED AS INSTANCE VARIABLES FOR GLOBAL ACCESS) ---
        self.BG_MAIN = '#e9eef2'
        self.BG_CARD = '#ffffff'
        self.BG_LIGHT = '#f7f9fa' # Subtle background for controls
        self.ACCENT_BLUE = '#1e88e5' # Primary action color
        self.ACCENT_DARK = '#005cb2' 
        self.TEXT_COLOR = '#333333'
        
        self.root.configure(bg=self.BG_MAIN) # Set root background

        self.setup_styles()
        self.build_ui()
        self.update_totals()
        
        self.root.bind("<KeyRelease>", self._recalculate_on_key_release)
        self.tree.bind("<Double-1>", self._on_item_double_click)

    def _recalculate_on_key_release(self, event):
        # Only recalculate if key is released in the tax entry or a text widget
        if event.widget == self.tax_entry or isinstance(event.widget, Entry):
            self.update_totals()

    def _on_item_double_click(self, event):
        # Open edit dialog on double click
        self.open_edit_item_dialog()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam') 
        
        # --- Base Styles (Uses self. variables) ---
        style.configure('TFrame', background=self.BG_MAIN)
        style.configure('TLabel', background=self.BG_CARD, foreground=self.TEXT_COLOR, font=('Helvetica', 10))
        
        # --- Card-like Frames (Simulating layered depth) ---
        style.configure('Card.TFrame', background=self.BG_CARD, borderwidth=1, relief='flat')
        style.configure('Card.TLabelframe', background=self.BG_CARD, bordercolor='#dddddd', relief='solid', padding=5)
        style.configure('Card.TLabelframe.Label', background=self.BG_CARD, foreground=self.TEXT_COLOR, font=('Helvetica', 11, 'bold'))
        
        # --- Entry/Text Styles ---
        style.configure('TEntry', fieldbackground=self.BG_LIGHT, borderwidth=0, relief='flat', padding=5)
        
        # --- Accent Button (Call to Action) ---
        style.configure('Accent.TButton', background=self.ACCENT_BLUE, foreground=self.BG_CARD, 
                        font=('Helvetica', 10, 'bold'), borderwidth=0, relief='flat', padding=[10, 5])
        style.map('Accent.TButton', 
                   background=[('active', self.ACCENT_DARK), ('pressed', self.ACCENT_DARK)], 
                   foreground=[('active', 'white'), ('pressed', 'white')])

        # --- Secondary Button ---
        style.configure('TButton', background=self.BG_LIGHT, foreground=self.TEXT_COLOR, 
                        font=('Helvetica', 10), borderwidth=0, relief='flat', padding=[10, 5])
        style.map('TButton', 
                   background=[('active', '#cccccc'), ('pressed', '#aaaaaa')])
                   
        # --- Treeview Styling ---
        style.configure("Treeview", 
                        background=self.BG_CARD,
                        foreground=self.TEXT_COLOR,
                        fieldbackground=self.BG_CARD,
                        rowheight=28,
                        borderwidth=0)
        style.map('Treeview', 
                   background=[('selected', self.ACCENT_BLUE)], 
                   foreground=[('selected', 'white')])
        style.configure("Treeview.Heading", 
                        font=('Helvetica', 10, 'bold'),
                        background=self.BG_LIGHT,
                        foreground=self.TEXT_COLOR,
                        padding=5)

    # ------------------------------------------------------------------
    # ---------- Build UI (Dynamic Layout with Modern Style) ----------
    # ------------------------------------------------------------------
    def build_ui(self):
        
        main_frame = ttk.Frame(self.root, padding="20", style='TFrame')
        main_frame.pack(fill=BOTH, expand=True)
        
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Row 0: Top Frame (Seller/Meta) - Use Card Style
        top_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=10)
        top_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        top_frame.grid_columnconfigure(0, weight=1) 
        top_frame.grid_columnconfigure(1, weight=0)

        seller_frame = ttk.LabelFrame(top_frame, text="Seller (Your Company Info)", padding="10", style='Card.TLabelframe')
        seller_frame.grid(row=0, column=0, sticky='nsew', padx=5)
        seller_frame.grid_columnconfigure(0, weight=1)
        seller_frame.grid_rowconfigure(0, weight=1)
        
        self.seller_entry = Text(seller_frame, height=5, bg='#f9f9f9', fg=self.TEXT_COLOR, font=('Helvetica', 10), relief='flat', padx=5, pady=5)
        self.seller_entry.insert("1.0", self.seller_text.get())
        self.seller_entry.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
        self.seller_entry.bind('<FocusOut>', lambda e: self.seller_text.set(self.seller_entry.get("1.0", END).strip()))

        meta_frame = ttk.LabelFrame(top_frame, text="Invoice Details", padding="10", style='Card.TLabelframe')
        meta_frame.grid(row=0, column=1, sticky='ne', padx=5)
        
        # Use simple label for numbers, bold for better distinction
        ttk.Label(meta_frame, text="Invoice No:", style='TLabel').grid(row=0, column=0, sticky=E, padx=5, pady=2)
        ttk.Label(meta_frame, textvariable=self.invoice_number, font=('Helvetica', 12, 'bold'), style='TLabel', foreground=self.ACCENT_BLUE).grid(row=0, column=1, sticky=W)
        ttk.Label(meta_frame, text="Date:", style='TLabel').grid(row=1, column=0, sticky=E, padx=5, pady=2)
        ttk.Entry(meta_frame, textvariable=self.invoice_date, width=15, font=('Helvetica', 10), style='TEntry').grid(row=1, column=1, sticky=W)

        # Row 1: Buyer Frame - Use Card Style
        buyer_frame = ttk.LabelFrame(main_frame, text="Buyer Details", padding="10", style='Card.TLabelframe')
        buyer_frame.grid(row=1, column=0, sticky='ew', pady=15)
        buyer_frame.grid_columnconfigure(1, weight=1)
        buyer_frame.grid_columnconfigure(3, weight=3)

        ttk.Label(buyer_frame, text="Name:", style='TLabel', background=self.BG_CARD).grid(row=0, column=0, sticky=W, padx=5, pady=2)
        ttk.Entry(buyer_frame, textvariable=self.buyer_name, width=40, font=('Helvetica', 10), style='TEntry').grid(row=0, column=1, sticky='ew', padx=4)
        ttk.Label(buyer_frame, text="Address:", style='TLabel', background=self.BG_CARD).grid(row=1, column=0, sticky=W, padx=5, pady=2)
        ttk.Entry(buyer_frame, textvariable=self.buyer_address, width=80, font=('Helvetica', 10), style='TEntry').grid(row=1, column=1, sticky='ew', padx=4, columnspan=3)

        # Row 2: Items Treeview - Use Card Style
        items_frame = ttk.LabelFrame(main_frame, text="Items/Services", padding="10", style='Card.TLabelframe')
        items_frame.grid(row=2, column=0, sticky='nsew', pady=15)
        items_frame.grid_columnconfigure(0, weight=1)
        items_frame.grid_rowconfigure(0, weight=1)
        
        columns = ("desc", "qty", "unit", "total")
        self.tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=12, selectmode='browse')
        
        self.tree.heading("desc", text="Description", anchor=W)
        self.tree.heading("qty", text="Qty", anchor=CENTER)
        self.tree.heading("unit", text="Unit Price", anchor=E)
        self.tree.heading("total", text="Total", anchor=E)
        
        self.tree.column("desc", anchor=W, width=350, stretch=True)
        self.tree.column("qty", anchor=CENTER, width=70, stretch=False)
        self.tree.column("unit", anchor=E, width=120, stretch=False)
        self.tree.column("total", anchor=E, width=120, stretch=False)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        
        vsb = ttk.Scrollbar(items_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=vsb.set)

        # Row 3: Item Action Buttons
        btn_frame = ttk.Frame(main_frame, style='TFrame')
        btn_frame.grid(row=3, column=0, sticky='w', pady=(5, 15))
        
        ttk.Button(btn_frame, text="➕ Add Item", command=self.open_add_item_dialog, style='TButton').pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Edit Selected", command=self.open_edit_item_dialog, style='TButton').pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="➖ Remove Selected", command=self.remove_selected, style='TButton').pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Clear All Items", command=self.clear_items, style='TButton').pack(side=LEFT, padx=5)

        # Row 4: Totals and Notes
        bottom_row_frame = ttk.Frame(main_frame, style='TFrame')
        bottom_row_frame.grid(row=4, column=0, sticky='ew', pady=(0, 15))
        bottom_row_frame.grid_columnconfigure(0, weight=1)
        bottom_row_frame.grid_columnconfigure(1, weight=0)
        
        notes_frame = ttk.LabelFrame(bottom_row_frame, text="Notes/Terms", padding="10", style='Card.TLabelframe')
        notes_frame.grid(row=0, column=0, sticky='nsew', padx=5)
        notes_frame.grid_columnconfigure(0, weight=1)
        notes_frame.grid_rowconfigure(0, weight=1)
        
        self.notes_text_widget = Text(notes_frame, height=5, wrap='word', bg='#f9f9f9', fg=self.TEXT_COLOR, font=('Helvetica', 10), relief='flat', padx=5, pady=5)
        self.notes_text_widget.grid(row=0, column=0, sticky='nsew')
        
        totals_frame = ttk.LabelFrame(bottom_row_frame, text="Summary", padding="10", style='Card.TLabelframe')
        totals_frame.grid(row=0, column=1, sticky='se', padx=5)
        
        row_idx = 0
        ttk.Label(totals_frame, text="Subtotal:", font=('Helvetica', 10), background=self.BG_CARD).grid(row=row_idx, column=0, sticky=E, padx=5, pady=2)
        ttk.Label(totals_frame, textvariable=self.subtotal, width=15, anchor=E, font=('Helvetica', 10, 'bold'), background=self.BG_CARD).grid(row=row_idx, column=1, sticky=E)
        
        row_idx += 1
        ttk.Label(totals_frame, text="Tax %:", font=('Helvetica', 10), background=self.BG_CARD).grid(row=row_idx, column=0, sticky=E, padx=5, pady=2)
        self.tax_entry = ttk.Entry(totals_frame, textvariable=self.tax_percent, width=6, font=('Helvetica', 10), style='TEntry')
        self.tax_entry.grid(row=row_idx, column=1, sticky=E)
        
        row_idx += 1
        ttk.Label(totals_frame, text="Tax Amount:", font=('Helvetica', 10), background=self.BG_CARD).grid(row=row_idx, column=0, sticky=E, padx=5, pady=2)
        ttk.Label(totals_frame, textvariable=self.tax_amount, width=15, anchor=E, font=('Helvetica', 10), background=self.BG_CARD).grid(row=row_idx, column=1, sticky=E)
        
        row_idx += 1
        ttk.Separator(totals_frame, orient='horizontal').grid(row=row_idx, column=0, columnspan=2, sticky='ew', pady=5)
        
        row_idx += 1
        ttk.Label(totals_frame, text="GRAND TOTAL:", font=('Helvetica', 14, 'bold'), background=self.BG_CARD).grid(row=row_idx, column=0, sticky=E, padx=5, pady=2)
        # Highlight total amount (Uses self.ACCENT_BLUE, which is now defined)
        ttk.Label(totals_frame, textvariable=self.total_amount, font=('Helvetica', 14, 'bold'), width=15, anchor=E, foreground=self.ACCENT_BLUE, background=self.BG_CARD).grid(row=row_idx, column=1, sticky=E)

        # Row 5: Final Action buttons
        action_frame = ttk.Frame(main_frame, style='TFrame')
        action_frame.grid(row=5, column=0, sticky='ew', pady=(10, 0))
        
        gen_btn = ttk.Button(action_frame, text="💾 Generate & Save PDF", command=self.on_generate_pdf, width=25, style='Accent.TButton')
        gen_btn.pack(side=RIGHT, padx=4)
        
        print_btn = ttk.Button(action_frame, text="🖨️ Print Invoice", command=self.on_print_invoice_wrapper, width=20, style='Accent.TButton')
        print_btn.pack(side=RIGHT, padx=4)
        
        preview_btn = ttk.Button(action_frame, text="🔎 Preview Invoice", command=self.on_preview_invoice, width=20, style='Accent.TButton')
        preview_btn.pack(side=RIGHT, padx=4)
        
        reset_btn = ttk.Button(action_frame, text="🔄 Reset All", command=self.reset_all, width=12, style='TButton')
        reset_btn.pack(side=LEFT)
    # ------------------------------------------------------------------
    # ---------- End of build_ui ----------
    # ------------------------------------------------------------------

    # --- Item management ---
    
    def open_add_item_dialog(self):
        self._open_item_dialog(is_edit=False)

    def open_edit_item_dialog(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Edit Item", "Please select an item row to edit.")
            return
        
        item_index = self.tree.index(sel[0])
        initial_data = self.items[item_index]
        
        self._open_item_dialog(is_edit=True, index=item_index, initial_data=initial_data)

    def _open_item_dialog(self, is_edit, index=None, initial_data=None):
        dialog = Toplevel(self.root)
        dialog.title("Edit Item" if is_edit else "Add Item")
        dialog.configure(bg=self.BG_LIGHT)
        dialog.transient(self.root) # Keep dialog on top
        dialog.grab_set() # Modal behavior

        # Centering the dialog
        dialog.update_idletasks()
        w = dialog.winfo_screenwidth()
        h = dialog.winfo_screenheight()
        size = tuple(int(_) for _ in dialog.geometry().split('+')[0].split('x'))
        x = w/2 - size[0]/2
        y = h/2 - size[1]/2
        dialog.geometry("+%d+%d" % (x, y))

        frame = ttk.Frame(dialog, padding="15", style='Card.TFrame')
        frame.pack(fill=BOTH, expand=True)

        # Variables for the fields
        desc = StringVar(value=initial_data['desc'] if is_edit else "")
        qty = IntVar(value=initial_data['qty'] if is_edit else 1)
        unit_price = DoubleVar(value=initial_data['unit_price'] if is_edit else 0.0)

        # Widgets setup
        ttk.Label(frame, text="Description", font=('Helvetica', 10), background=self.BG_CARD).grid(row=0, column=0, sticky=W, pady=5, padx=5)
        desc_entry = ttk.Entry(frame, textvariable=desc, width=50, font=('Helvetica', 10), style='TEntry')
        desc_entry.grid(row=0, column=1, padx=6, pady=4, columnspan=2)
        
        ttk.Label(frame, text="Quantity", font=('Helvetica', 10), background=self.BG_CARD).grid(row=1, column=0, sticky=W, pady=5, padx=5)
        ttk.Entry(frame, textvariable=qty, width=10, font=('Helvetica', 10), style='TEntry').grid(row=1, column=1, sticky=W, padx=6, pady=4)
        
        ttk.Label(frame, text="Unit Price (₹)", font=('Helvetica', 10), background=self.BG_CARD).grid(row=2, column=0, sticky=W, pady=5, padx=5)
        ttk.Entry(frame, textvariable=unit_price, width=15, font=('Helvetica', 10), style='TEntry').grid(row=2, column=1, sticky=W, padx=6, pady=4)

        def save_item():
            d = desc.get().strip()
            try:
                q = int(qty.get())
                p = float(unit_price.get())
            except Exception:
                messagebox.showerror("Invalid input", "Quantity must be an integer and unit price must be numeric.")
                return
            if not d:
                messagebox.showerror("Invalid input", "Please enter a description.")
                return
            
            if q <= 0 or p < 0:
                messagebox.showerror("Invalid input", "Quantity must be positive and Unit Price cannot be negative.")
                return

            new_item = {"desc": d, "qty": q, "unit_price": p}
            
            if is_edit:
                self.items[index] = new_item
            else:
                self.items.append(new_item)
                
            self.refresh_items()
            dialog.destroy()

        button_text = "Save Changes" if is_edit else "Add Item"
        ttk.Button(frame, text=button_text, command=save_item, style='Accent.TButton').grid(row=3, column=1, sticky="e", pady=15, padx=6)
        
        desc_entry.focus_set()
        self.root.wait_window(dialog) # Wait for dialog to close


    def refresh_items(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        for it in self.items:
            line_total = it['qty'] * it['unit_price']
            self.tree.insert("", END, values=(
                it['desc'], 
                it['qty'], 
                currency_fmt(it['unit_price']), 
                currency_fmt(line_total)
            ))
        self.update_totals()

    def remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Remove", "Please select a row to remove.")
            return
        
        idx = self.tree.index(sel[0])
        del self.items[idx]
        self.refresh_items()

    def clear_items(self):
        if messagebox.askyesno("Clear Items", "Remove all items?"):
            self.items = []
            self.refresh_items()
    
    # --- Other methods ---

    def update_totals(self):
        try:
            tax_p = float(self.tax_percent.get())
        except ValueError:
            tax_p = 0.0
            
        s = sum(it['qty']*it['unit_price'] for it in self.items)
        
        # Use StringVars for formatted currency display in the UI
        self.subtotal.set(currency_fmt(s))
        
        tax_amt = s * tax_p/100.0
        self.tax_amount.set(currency_fmt(tax_amt))
        
        total = s + tax_amt
        self.total_amount.set(currency_fmt(total))

    def on_generate_pdf(self, skip_message=False):
        self.seller_text.set(self.seller_entry.get("1.0", END).strip())
        
        seller = self.seller_text.get().strip()
        buyer_name = self.buyer_name.get().strip()
        buyer_address = self.buyer_address.get().strip()
        
        if not seller or not buyer_name or not buyer_address:
            messagebox.showwarning("Missing info", "Seller Info, Buyer Name, and Address cannot be empty.")
            return

        inv_no = self.invoice_number.get()
        date_str = self.invoice_date.get()
        buyer = f"{buyer_name}\n{buyer_address}"
        
        try:
            subtotal_val = sum(it['qty']*it['unit_price'] for it in self.items) 
            tax_p_val = float(self.tax_percent.get())
            tax_amount_val = subtotal_val * tax_p_val/100.0
            total_val = subtotal_val + tax_amount_val
        except ValueError:
            messagebox.showerror("Calculation Error", "Invalid numeric value in tax percentage. Please correct it.")
            return

        notes = self.notes_text_widget.get("1.0", END).strip()
        pdf_path = os.path.join(INVOICE_DIR, f"Invoice_{inv_no:04d}.pdf")
        
        try:
            generate_pdf(inv_no, date_str, seller, buyer, self.items, subtotal_val, tax_p_val, tax_amount_val, total_val, notes, pdf_path)
        except Exception as e:
            messagebox.showerror("PDF Error", f"Failed to generate PDF:\n{e}")
            return
        
        self.save_invoice_data(inv_no, date_str, buyer_name, subtotal_val, tax_amount_val, total_val)
        
        if not skip_message:
            messagebox.showinfo("PDF Generated", f"Invoice saved to:\n{pdf_path}")
        
        # Increment to the next number only upon successful generation
        self.invoice_number.set(next_invoice_number())
        
    def on_print_invoice_wrapper(self):
        if not self.items:
            messagebox.showinfo("Print", "No items to print.")
            return
        
        current_inv_no = self.invoice_number.get()
        self.on_generate_pdf(skip_message=True)
        
        last_pdf = os.path.join(INVOICE_DIR, f"Invoice_{current_inv_no:04d}.pdf")
        
        if os.path.exists(last_pdf):
            self.last_pdf_path = last_pdf
            self.open_printer_selection_dialog()
        else:
            messagebox.showerror("Print Error", "Could not find the generated PDF to print.")
            self.last_pdf_path = None

    def on_preview_invoice(self):
        if not self.items:
            messagebox.showinfo("Preview", "No items to preview.")
            return
            
        current_inv_no = self.invoice_number.get()
        self.on_generate_pdf(skip_message=True) 
        
        last_pdf = os.path.join(INVOICE_DIR, f"Invoice_{current_inv_no:04d}.pdf")
        
        if os.path.exists(last_pdf):
            preview_pdf(last_pdf)
        else:
            messagebox.showerror("Preview Error", "Could not find the generated PDF to preview.")

    def open_printer_selection_dialog(self):
        
        if platform.system() != "Windows" or not WIN32_AVAILABLE:
            print_pdf(self.last_pdf_path)
            return

        try:
            printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
            default_printer = win32print.GetDefaultPrinter()
        except Exception:
            print_pdf(self.last_pdf_path)
            return

        if not printers:
            print_pdf(self.last_pdf_path)
            return

        dialog = Toplevel(self.root)
        dialog.title("Select Printer")
        dialog.configure(bg=self.BG_LIGHT)
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="15", style='Card.TFrame')
        frame.pack(fill=BOTH, expand=True)

        ttk.Label(frame, text="Choose a Printer:", font=('Helvetica', 12, 'bold'), background=self.BG_CARD).pack(pady=10)

        selected_printer = StringVar(value=default_printer if default_printer in printers else printers[0])

        printer_combobox = ttk.Combobox(frame, textvariable=selected_printer, values=printers, state='readonly', width=50, font=('Helvetica', 10))
        printer_combobox.pack(pady=10, padx=20)

        def confirm_print():
            printer_name = selected_printer.get()
            dialog.destroy()
            print_pdf(self.last_pdf_path, printer_name)

        def cancel_dialog():
            dialog.destroy()

        button_frame = ttk.Frame(frame, style='Card.TFrame')
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Print", command=confirm_print, style='Accent.TButton', width=15).pack(side=LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=cancel_dialog, style='TButton', width=15).pack(side=LEFT, padx=10)

        dialog.update_idletasks()
        w = dialog.winfo_screenwidth()
        h = dialog.winfo_screenheight()
        size = tuple(int(_) for _ in dialog.geometry().split('+')[0].split('x'))
        x = w/2 - size[0]/2
        y = h/2 - size[1]/2
        dialog.geometry("+%d+%d" % (x, y))

        self.root.wait_window(dialog)

    def save_invoice_data(self, inv_no, date_str, buyer, subtotal, tax, total):
        fieldnames = ["invoice_no", "date", "buyer", "subtotal", "tax", "total"]
        write_header = not os.path.exists(INVOICE_CSV)
        try:
            with open(INVOICE_CSV,"a",newline="",encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()
                writer.writerow({"invoice_no": inv_no,"date":date_str,"buyer":buyer,"subtotal":subtotal,"tax":tax,"total":total})
        except Exception as e:
            messagebox.showwarning("CSV Error", f"Cannot save invoice record:\n{e}")

    def reset_all(self):
        if messagebox.askyesno("Reset", "Reset all fields and items?"):
            self.items = []
            self.refresh_items()
            self.buyer_name.set("")
            self.buyer_address.set("")
            self.invoice_number.set(next_invoice_number())
            self.invoice_date.set(datetime.date.today().isoformat())
            self.notes_text_widget.delete("1.0", END)
            self.tax_percent.set(18.0) 
            self.update_totals()

# ---------- Run App ----------
if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("Pillow library not found. PDF Preview will not work.")
        print("Install it with: pip install Pillow")

    root = Tk()
    app = InvoiceApp(root)
    root.mainloop()