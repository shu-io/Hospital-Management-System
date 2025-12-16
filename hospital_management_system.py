import streamlit as st
import json
import os
from datetime import datetime
from io import BytesIO
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from reportlab.pdfgen import canvas
except ImportError:
    st.error("Please install reportlab: pip install reportlab")


def load_json(file_path, default_data):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        with open(file_path, 'w') as f:
            json.dump(default_data, f, indent=4)
        return default_data


def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


class MedicineInventory:
    def __init__(self, file_path):
        self.file_path = file_path
        self.medicines = load_json(file_path, self.get_default_medicines())

    def get_default_medicines(self):
        medicines_list = [
            "Ibupara", "Paracetamol 500mg", "Paracetamol 650 mg", "Dicyclomine hcl", "Cheston cold",
            "B.complex (mvbc)", "Diclofenac50mg", "Avil25mg", "Ceterizen 10 mg", "Pantop 40 mg",
            "Norfloxacin & Tinidazole", "Metronidazole", "Azithromycin 500mg", "Ciprofloxacin", "Ofloxacin",
            "Cefixime 200 mg", "Combit of fluconazole", "Ivermectin 12 mg", "Ors", "Luperamide",
            "Alprazolam 0.5", "Sorbitrat 5mg", "Amlodipine", "Tube miconazole", "Tube Diclofenac",
            "Tube fusidic acid", "Tube povidone", "Bandage 6 inch", "Bandage 4 inch", "Ivf.Ns 100ml",
            "Ivf.Ns 500 ml", "Ivf.DNS 500 ml", "Ivf.5D 500 ml", "Syringe 2 ml", "Syringe 5ml",
            "Syringe 10 ml", "Syringe 3 ml", "Hydrogen peroxide 500ml", "Microstrile 500ml",
            "Malti vitamin 200ml", "Paracetamol 60ml", "Cheston cold 60ml", "C-zen plus 60ml (ctz)",
            "Albendazole 10ml", "Amoxycillin suspension 30ml", "Ciprofloxacin eye drop 10ml",
            "Avil 75mg", "Hyoscine butylbromide 20mg (biscogen)", "Sodium bicarbonate 7.5 w/v",
            "Optineuronforte 3ml", "Diclofenac sodium 75mg/ml (Dynapar)", "Phenytoin sodium 50mg",
            "Paracetamol 150mg/ml", "Ondansetron 2ml", "Gentamycin 2ml", "Dopamine 40mg",
            "Oxytocin 1ml", "Adrenaline bitartrate 1ml", "Atropine sulphate 1ml", "Trenaxamic acid 500mg",
            "Tetanus (T.T.) 0.5ml", "Oxidocin"
        ]
        return {med: {"quantity": 50, "price": 10.0} for med in medicines_list}

    def add_medicine(self, name, quantity, price):
        if name in self.medicines:
            st.error(f"Medicine {name} already exists.")
            return
        self.medicines[name] = {"quantity": quantity, "price": price}
        self.save()

    def update_quantity(self, name, new_quantity):
        if name not in self.medicines:
            st.error(f"Medicine {name} not found.")
            return
        self.medicines[name]["quantity"] = new_quantity
        self.save()

    def delete_medicine(self, name):
        if name not in self.medicines:
            st.error(f"Medicine {name} not found.")
            return
        del self.medicines[name]
        self.save()

    def check_availability(self, name, required_qty):
        if name not in self.medicines:
            return False
        return self.medicines[name]["quantity"] >= required_qty

    def deduct_quantity(self, name, qty):
        if self.check_availability(name, qty):
            self.medicines[name]["quantity"] -= qty
            self.save()
            return True
        return False

    def get_low_stock(self):
        return {name: data for name, data in self.medicines.items() if data["quantity"] < 10}

    def save(self):
        save_json(self.file_path, self.medicines)


class PatientManager:
    def __init__(self, file_path, inventory):
        self.file_path = file_path
        self.inventory = inventory
        self.patients = load_json(file_path, {})

    def add_patient(self, name, age, gender):
        if name in self.patients:
            st.error(f"Patient {name} already exists.")
            return
        self.patients[name] = {"age": age,
                               "gender": gender, "prescriptions": []}
        self.save()

    def add_prescription(self, patient_name, medicines):
        if patient_name not in self.patients:
            st.error(f"Patient {patient_name} not found.")
            return
        prescription = {"date": str(datetime.now()), "medicines": medicines}
        for med, qty in medicines.items():
            if not self.inventory.check_availability(med, qty):
                st.error(f"Insufficient stock for {med}.")
                return
        for med, qty in medicines.items():
            self.inventory.deduct_quantity(med, qty)
        self.patients[patient_name]["prescriptions"].append(prescription)
        self.save()
        return prescription

    def get_patient_history(self, patient_name):
        if patient_name not in self.patients:
            return None
        return self.patients[patient_name]

    def save(self):
        save_json(self.file_path, self.patients)


def generate_professional_prescription_pdf(patient_name, patient_data, prescription, inventory):
    """Generate a professional medical prescription PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                            leftMargin=40, topMargin=60, bottomMargin=40)

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1F4E5F'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#626C71'),
        spaceAfter=20,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1F4E5F'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )

    # Header
    elements.append(Paragraph("LNMedico", title_style))
    elements.append(Paragraph("Healthcare Management System", subtitle_style))
    elements.append(Paragraph(
        "📍 Bhopal, Madhya Pradesh | 📞 +91-XXXXX-XXXXX | 📧 contact@lnmedico.com", subtitle_style))

    # Horizontal line
    elements.append(Spacer(1, 0.1*inch))

    # Patient Information
    elements.append(Paragraph("PRESCRIPTION RECEIPT", heading_style))

    # Patient details table
    patient_info = [
        ['Receipt No:', f"LNM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
         'Date:', datetime.now().strftime('%d/%m/%Y %I:%M %p')],
        ['Patient Name:', patient_name, 'Age:', str(patient_data['age'])],
        ['Gender:', patient_data['gender'],
            'Prescribed On:', prescription['date'][:10]]
    ]

    patient_table = Table(patient_info, colWidths=[
                          1.5*inch, 2.5*inch, 1*inch, 2*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4F8')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#E8F4F8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1F4E5F')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#C0E8F5'))
    ]))

    elements.append(patient_table)
    elements.append(Spacer(1, 0.3*inch))

    # Medicines prescribed
    elements.append(Paragraph("MEDICINES PRESCRIBED", heading_style))

    # Medicines table with prices
    medicine_data = [['S.No', 'Medicine Name',
                      'Quantity', 'Unit Price (₹)', 'Total (₹)']]

    total_amount = 0
    for idx, (med, qty) in enumerate(prescription['medicines'].items(), 1):
        price = inventory.medicines.get(med, {}).get('price', 0.0)
        item_total = price * qty
        total_amount += item_total
        medicine_data.append([
            str(idx),
            med,
            str(qty),
            f"₹{price:.2f}",
            f"₹{item_total:.2f}"
        ])

    # Add total row
    medicine_data.append(['', '', '', 'Grand Total:', f"₹{total_amount:.2f}"])

    medicine_table = Table(medicine_data, colWidths=[
                           0.6*inch, 3.5*inch, 1*inch, 1.3*inch, 1.3*inch])
    medicine_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#21808D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

        # Data rows
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1F4E5F')),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 9),
        ('TOPPADDING', (0, 1), (-1, -2), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 8),

        # Total row
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F4F8')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 11),
        ('ALIGN', (3, -1), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, -1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 10),

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#21808D'))
    ]))

    elements.append(medicine_table)
    elements.append(Spacer(1, 0.4*inch))

    # Instructions
    instructions_style = ParagraphStyle(
        'Instructions',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#626C71'),
        spaceAfter=6,
    )

    elements.append(Paragraph("IMPORTANT INSTRUCTIONS", heading_style))
    elements.append(Paragraph(
        "• Take medicines as prescribed by the physician", instructions_style))
    elements.append(Paragraph(
        "• Complete the full course of antibiotics if prescribed", instructions_style))
    elements.append(Paragraph(
        "• Store medicines in a cool, dry place away from direct sunlight", instructions_style))
    elements.append(
        Paragraph("• Keep medicines out of reach of children", instructions_style))

    elements.append(Spacer(1, 0.3*inch))

    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#626C71'),
        alignment=TA_CENTER,
    )

    elements.append(Paragraph("_" * 80, footer_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(
        "This is a computer-generated prescription receipt from LNMedico", footer_style))
    elements.append(Paragraph(
        "For any queries, please contact us at contact@lnmedico.com", footer_style))
    elements.append(
        Paragraph("Thank you for choosing LNMedico Healthcare", footer_style))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_inventory_pdf(inventory):
    """Generate professional inventory report PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                            leftMargin=40, topMargin=60, bottomMargin=40)

    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1F4E5F'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#626C71'),
        spaceAfter=20,
        alignment=TA_CENTER,
    )

    # Header
    elements.append(Paragraph("LNMedico", title_style))
    elements.append(Paragraph("Medicine Inventory Report", subtitle_style))
    elements.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))

    # Inventory table
    inventory_data = [['S.No', 'Medicine Name', 'Quantity',
                       'Unit Price (₹)', 'Stock Value (₹)', 'Status']]

    total_value = 0
    for idx, (med, data) in enumerate(sorted(inventory.medicines.items()), 1):
        stock_value = data['quantity'] * data['price']
        total_value += stock_value
        status = '⚠ Low Stock' if data['quantity'] < 10 else '✓ In Stock'

        inventory_data.append([
            str(idx),
            med,
            str(data['quantity']),
            f"₹{data['price']:.2f}",
            f"₹{stock_value:.2f}",
            status
        ])

    # Add total row
    inventory_data.append(
        ['', '', '', 'Total Inventory Value:', f"₹{total_value:.2f}", ''])

    inventory_table = Table(inventory_data, colWidths=[
                            0.5*inch, 2.8*inch, 0.9*inch, 1*inch, 1.1*inch, 1*inch])
    inventory_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#21808D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

        # Data rows
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1F4E5F')),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 8),
        ('TOPPADDING', (0, 1), (-1, -2), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 6),

        # Total row
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F4F8')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('ALIGN', (3, -1), (-1, -1), 'CENTER'),
        ('SPAN', (3, -1), (4, -1)),

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#21808D'))
    ]))

    elements.append(inventory_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_patient_history_pdf(patient_name, patient_data, inventory):
    """Generate professional patient history PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                            leftMargin=40, topMargin=60, bottomMargin=40)

    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1F4E5F'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#626C71'),
        spaceAfter=20,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1F4E5F'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )

    # Header
    elements.append(Paragraph("LNMedico", title_style))
    elements.append(Paragraph("Patient Medical History", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))

    # Patient info
    patient_info_data = [
        ['Patient Name:', patient_name, 'Age:', str(patient_data['age'])],
        ['Gender:', patient_data['gender'], 'Report Date:',
            datetime.now().strftime('%d/%m/%Y')]
    ]

    patient_info_table = Table(patient_info_data, colWidths=[
                               1.5*inch, 2.5*inch, 1.2*inch, 1.8*inch])
    patient_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4F8')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#E8F4F8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1F4E5F')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#C0E8F5'))
    ]))

    elements.append(patient_info_table)
    elements.append(Spacer(1, 0.3*inch))

    # Prescription history
    elements.append(Paragraph("PRESCRIPTION HISTORY", heading_style))

    if patient_data['prescriptions']:
        for idx, presc in enumerate(patient_data['prescriptions'], 1):
            elements.append(
                Paragraph(f"Prescription #{idx} - Date: {presc['date'][:19]}", heading_style))

            med_data = [['Medicine Name', 'Quantity',
                         'Unit Price (₹)', 'Total (₹)']]
            presc_total = 0

            for med, qty in presc['medicines'].items():
                price = inventory.medicines.get(med, {}).get('price', 0.0)
                item_total = price * qty
                presc_total += item_total
                med_data.append(
                    [med, str(qty), f"₹{price:.2f}", f"₹{item_total:.2f}"])

            med_data.append(['Total', '', '', f"₹{presc_total:.2f}"])

            med_table = Table(med_data, colWidths=[
                              3.5*inch, 1*inch, 1.2*inch, 1.3*inch])
            med_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#21808D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F4F8')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#21808D'))
            ]))

            elements.append(med_table)
            elements.append(Spacer(1, 0.2*inch))
    else:
        elements.append(
            Paragraph("No prescriptions on record", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_all_patients_pdf(patient_manager, inventory):
    """Generate comprehensive PDF report of all patients"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                            leftMargin=40, topMargin=60, bottomMargin=40)

    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1F4E5F'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#626C71'),
        spaceAfter=20,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1F4E5F'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )

    # Header
    elements.append(Paragraph("LNMedico", title_style))
    elements.append(
        Paragraph("Complete Patient Database Report", subtitle_style))
    elements.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}", subtitle_style))
    elements.append(Spacer(1, 0.3*inch))

    if not patient_manager.patients:
        elements.append(
            Paragraph("No patients registered in the system.", styles['Normal']))
    else:
        # Summary table
        elements.append(Paragraph("PATIENT SUMMARY", heading_style))
        summary_data = [['S.No', 'Patient Name', 'Age',
                         'Gender', 'Total Prescriptions', 'Total Spent (₹)']]

        grand_total = 0
        for idx, (name, data) in enumerate(sorted(patient_manager.patients.items()), 1):
            patient_total = 0
            for presc in data['prescriptions']:
                for med, qty in presc['medicines'].items():
                    price = inventory.medicines.get(med, {}).get('price', 0.0)
                    patient_total += price * qty

            grand_total += patient_total
            summary_data.append([
                str(idx),
                name,
                str(data['age']),
                data['gender'],
                str(len(data['prescriptions'])),
                f"₹{patient_total:.2f}"
            ])

        # Add total row
        summary_data.append(['', 'TOTAL', '', '', str(sum(len(p['prescriptions'])
                            for p in patient_manager.patients.values())), f"₹{grand_total:.2f}"])

        summary_table = Table(summary_data, colWidths=[
                              0.5*inch, 2.2*inch, 0.7*inch, 0.9*inch, 1.2*inch, 1.2*inch])
        summary_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#21808D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

            # Data rows
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1F4E5F')),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),

            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F4F8')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('ALIGN', (1, -1), (-1, -1), 'CENTER'),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#21808D'))
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, 0.4*inch))

        # Detailed patient information
        elements.append(Paragraph("DETAILED PATIENT RECORDS", heading_style))

        for idx, (patient_name, patient_data) in enumerate(sorted(patient_manager.patients.items()), 1):
            # Patient header
            patient_header_style = ParagraphStyle(
                'PatientHeader',
                parent=styles['Heading3'],
                fontSize=11,
                textColor=colors.HexColor('#21808D'),
                spaceAfter=8,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )

            elements.append(
                Paragraph(f"{idx}. {patient_name}", patient_header_style))

            # Patient basic info
            patient_info = [
                ['Age:', str(patient_data['age']), 'Gender:',
                 patient_data['gender']],
                ['Total Prescriptions:', str(
                    len(patient_data['prescriptions'])), 'Registration Status:', 'Active']
            ]

            patient_info_table = Table(patient_info, colWidths=[
                                       1.2*inch, 1.8*inch, 1.2*inch, 1.8*inch])
            patient_info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4F8')),
                ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#E8F4F8')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1F4E5F')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#C0E8F5'))
            ]))

            elements.append(patient_info_table)

            # Prescription history
            if patient_data['prescriptions']:
                elements.append(Spacer(1, 0.1*inch))

                presc_history_style = ParagraphStyle(
                    'PrescHistory',
                    parent=styles['Normal'],
                    fontSize=9,
                    textColor=colors.HexColor('#1F4E5F'),
                    spaceAfter=5,
                    fontName='Helvetica-Bold'
                )

                elements.append(
                    Paragraph("Prescription History:", presc_history_style))

                for presc_idx, presc in enumerate(patient_data['prescriptions'], 1):
                    presc_date = presc['date'][:19]
                    presc_total = sum(
                        inventory.medicines.get(
                            med, {}).get('price', 0.0) * qty
                        for med, qty in presc['medicines'].items()
                    )

                    presc_text = f"  • Prescription #{presc_idx} on {presc_date} - Total: ₹{presc_total:.2f}"
                    elements.append(Paragraph(presc_text, styles['Normal']))

                    # Medicine details
                    for med, qty in presc['medicines'].items():
                        price = inventory.medicines.get(
                            med, {}).get('price', 0.0)
                        med_text = f"    - {med}: {qty} units @ ₹{price:.2f}"
                        elements.append(Paragraph(med_text, styles['Normal']))
            else:
                elements.append(
                    Paragraph("  No prescriptions on record", styles['Normal']))

            elements.append(Spacer(1, 0.15*inch))

            # Add separator line between patients
            if idx < len(patient_manager.patients):
                elements.append(Paragraph("_" * 100, styles['Normal']))

    # Footer
    elements.append(Spacer(1, 0.3*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#626C71'),
        alignment=TA_CENTER,
    )

    elements.append(Paragraph("=" * 80, footer_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(
        Paragraph("LNMedico Healthcare Management System", footer_style))
    elements.append(
        Paragraph("Confidential Patient Database Report", footer_style))
    elements.append(Paragraph(
        f"Report Generated: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}", footer_style))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


# Initialize inventory and patient manager
inventory = MedicineInventory("medicines.json")
patient_manager = PatientManager("patients.json", inventory)

# Streamlit UI
st.set_page_config(page_title="LNMedico", layout="wide", page_icon="🏥")
st.title("🏥 LNMedico - Healthcare Management System")

# Sidebar
menu = st.sidebar.selectbox(
    "Navigation", ["Dashboard", "Inventory", "Patients", "Prescriptions", "Reports"])

if menu == "Dashboard":
    st.header("📊 Dashboard")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Medicines", len(inventory.medicines))
    with col2:
        st.metric("Total Patients", len(patient_manager.patients))
    with col3:
        low_stock_count = len(inventory.get_low_stock())
        st.metric("Low Stock Alerts", low_stock_count,
                  delta=None if low_stock_count == 0 else "⚠")

    st.divider()

    low_stock = inventory.get_low_stock()
    if low_stock:
        st.error("⚠ Low Stock Alert!")
        for med, data in low_stock.items():
            st.write(
                f"- *{med}*: {data['quantity']} units left (Price: ₹{data['price']})")
    else:
        st.success("✅ All medicines are sufficiently stocked.")

elif menu == "Inventory":
    st.header("💊 Medicine Inventory")

    st.subheader("Current Inventory")
    if inventory.medicines:
        inventory_df = [{"Name": k, "Quantity": v["quantity"], "Price (₹)": v["price"], "Stock Value (₹)": v["quantity"] * v["price"]}
                        for k, v in inventory.medicines.items()]
        st.dataframe(inventory_df, use_container_width=True)
    else:
        st.write("No medicines in inventory.")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("➕ Add New Medicine")
        with st.form("add_med"):
            name = st.text_input("Medicine Name")
            qty = st.number_input("Quantity", min_value=0)
            price = st.number_input("Price (₹)", min_value=0.0, format="%.2f")
            submitted = st.form_submit_button("Add Medicine")
            if submitted and name:
                inventory.add_medicine(name, qty, price)
                st.success("✅ Medicine added!")
                st.rerun()

    with col2:
        st.subheader("🔄 Update Quantity")
        with st.form("update_qty"):
            name = st.selectbox("Select Medicine", list(
                inventory.medicines.keys()))
            new_qty = st.number_input("New Quantity", min_value=0)
            submitted = st.form_submit_button("Update")
            if submitted:
                inventory.update_quantity(name, new_qty)
                st.success("✅ Quantity updated!")
                st.rerun()

    st.divider()

    st.subheader("🗑 Delete Medicine")
    with st.form("delete_med"):
        name = st.selectbox("Select Medicine to Delete", list(
            inventory.medicines.keys()), key="delete_select")
        submitted = st.form_submit_button("Delete")
        if submitted:
            inventory.delete_medicine(name)
            st.success("✅ Medicine deleted!")
            st.rerun()

elif menu == "Patients":
    st.header("👥 Patient Management")

    st.subheader("Registered Patients")
    if patient_manager.patients:
        patients_df = [{"Name": k, "Age": v["age"], "Gender": v["gender"], "Prescriptions": len(v["prescriptions"])}
                       for k, v in patient_manager.patients.items()]
        st.dataframe(patients_df, use_container_width=True)
    else:
        st.write("No patients registered.")

    st.divider()

    st.subheader("➕ Register New Patient")
    with st.form("register_patient"):
        name = st.text_input("Patient Name")
        age = st.number_input("Age", min_value=0, max_value=120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        submitted = st.form_submit_button("Register Patient")
        if submitted and name:
            patient_manager.add_patient(name, age, gender)
            st.success("✅ Patient registered!")
            st.rerun()

elif menu == "Prescriptions":
    st.header("📋 Prescription Management")

    if not patient_manager.patients:
        st.warning("⚠ No patients registered. Please register a patient first.")
    else:
        st.subheader("Create New Prescription")
        with st.form("create_prescription"):
            patient_name = st.selectbox(
                "Select Patient", list(patient_manager.patients.keys()))
            medicines = {}
            num_meds = st.number_input(
                "Number of Medicines", min_value=1, max_value=10, value=1)

            for i in range(num_meds):
                col1, col2 = st.columns([3, 1])
                with col1:
                    med = st.selectbox(
                        f"Medicine {i+1}", list(inventory.medicines.keys()), key=f"med_{i}")
                with col2:
                    qty = st.number_input(
                        f"Qty", min_value=1, key=f"qty_{i}", value=1)
                if med in medicines:
                    medicines[med] += qty
                else:
                    medicines[med] = qty

            submitted = st.form_submit_button(
                "Create Prescription & Generate PDF")
            if submitted:
                prescription = patient_manager.add_prescription(
                    patient_name, medicines)
                if prescription:
                    st.success("✅ Prescription created successfully!")

                    # Generate PDF
                    patient_data = patient_manager.get_patient_history(
                        patient_name)
                    pdf_buffer = generate_professional_prescription_pdf(
                        patient_name, patient_data, prescription, inventory)

                    st.download_button(
                        label="📄 Download Prescription PDF",
                        data=pdf_buffer,
                        file_name=f"LNMedico_Prescription_{patient_name}{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf",
                        mime="application/pdf",
                        type="primary"
                    )

    st.divider()

    st.subheader("📜 View Patient History")
    if patient_manager.patients:
        patient_name = st.selectbox("Select Patient for History", list(
            patient_manager.patients.keys()), key="history_select")
        if patient_name:
            history = patient_manager.get_patient_history(patient_name)
            if history:
                st.write(
                    f"*Age:* {history['age']} | *Gender:* {history['gender']}")

                if history["prescriptions"]:
                    st.subheader("Prescription History")
                    for idx, presc in enumerate(history["prescriptions"], 1):
                        with st.expander(f"Prescription #{idx} - {presc['date'][:19]}"):
                            medicines_df = [{"Medicine": med, "Quantity": qty, "Price (₹)": inventory.medicines.get(med, {}).get('price', 0.0)}
                                            for med, qty in presc["medicines"].items()]
                            st.table(medicines_df)

                    # Download full history
                    pdf_buffer = generate_patient_history_pdf(
                        patient_name, history, inventory)
                    st.download_button(
                        label="📄 Download Complete Medical History",
                        data=pdf_buffer,
                        file_name=f"LNMedico_History_{patient_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.info("No prescriptions on record.")

elif menu == "Reports":
    st.header("📊 Reports & Export")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Inventory Report")
        st.write("Export complete medicine inventory with stock values")
        pdf_buffer = generate_inventory_pdf(inventory)
        st.download_button(
            label="📄 Download Inventory PDF Report",
            data=pdf_buffer,
            file_name=f"LNMedico_Inventory_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            type="primary"
        )

    with col2:
        st.subheader("👥 Patient Database Report")
        st.write("Export all patient records in professional PDF format")
        pdf_buffer = generate_all_patients_pdf(patient_manager, inventory)
        st.download_button(
            label="📄 Download Patients Database PDF",
            data=pdf_buffer,
            file_name=f"LNMedico_All_Patients_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            type="primary"
        )

    st.divider()

    st.subheader("📈 Quick Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        total_medicines = len(inventory.medicines)
        st.metric("Total Medicines", total_medicines)

    with col2:
        total_stock_value = sum(data['quantity'] * data['price']
                                for data in inventory.medicines.values())
        st.metric("Total Inventory Value", f"₹{total_stock_value:,.2f}")

    with col3:
        total_prescriptions = sum(len(p['prescriptions'])
                                  for p in patient_manager.patients.values())
        st.metric("Total Prescriptions", total_prescriptions)
