# 🧾 Invoice Generator (Tkinter + ReportLab)

### 💡 Overview
A modern desktop-based **Invoice Generator** built using **Python (Tkinter + ReportLab)**.  
It features a sleek user interface, automatic invoice numbering, real-time tax and total calculation, and integrated PDF preview & printing.

---

## ⚙️ Usage Guide

### 🏢 Seller Info
- Edit the **multi-line text box (top-left corner)** to enter your company’s details.  
  *(These details will automatically appear in the generated PDF.)*

### 👤 Buyer Details
- Enter the **client’s name and address** in the provided fields.

### 📅 Invoice Details
- **Invoice No.** and **Date** are displayed automatically.  
- The **Invoice Number** increments automatically after each PDF generation.

### 🧾 Add Items
- Click **➕ Add Item** to open a dialog box.  
- Enter **Description**, **Quantity**, and **Unit Price**.  
- Double-click any existing item in the list to **edit** it instantly.

### 💰 Tax Rate
- Enter your desired tax percentage (e.g., `18.0`) in the **Summary Box**.  
- All totals update **instantly** as you modify values.

---

## 🧭 Actions

| Action | Description |
|--------|--------------|
| 💾 **Generate & Save PDF** | Creates and saves a professional PDF in the `/invoices` folder and logs it in a CSV file. |
| 🔎 **Preview Invoice** | Opens a **preview window** to view the invoice before saving. |
| 🖨️ **Print Invoice** | Saves the PDF and sends it to a **selected printer** automatically. |
| 🔄 **Reset All** | Clears all buyer details and item lists for a **fresh invoice**. |

---

## 🌟 Features

- 🖥️ **Modern UI/UX** — Clean, multi-pane layout styled with the *clam theme* and enhanced modern colors.  
- 📊 **Financial Breakdown** — Professional invoice design with **Subtotal, Tax, and Grand Total** sections.  
- ✏️ **Item Management** — Add, edit, or remove line items easily.  
- ⚡ **Auto Calculations** — Real-time tax and total updates as you modify items or rates.  
- 📄 **PDF Generation** — High-quality, print-ready invoices using **ReportLab**.  
- 📈 **Invoice Tracking** — Automatically logs key details (invoice no., date, buyer, total) into `records.csv`.  
- 👁️ **Preview & Print** — Built-in invoice preview and direct printing feature.  
- 🔢 **Auto Numbering** — Invoice numbers increment automatically after each generation.  

---

## 🚀 How to Run

### 🪟 For Windows Users

```bash
# Step 1: Create a virtual environment
python -m venv .env

# Step 2: Activate the virtual environment
.env\Scripts\activate

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Run the application
python invoice_app.py
