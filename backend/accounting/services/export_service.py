import openpyxl
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from ..models import ReferenceDefinition

class ExportService:
    @staticmethod
    def export_to_excel(queryset, model_name, filename="export.xlsx"):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Export"

        # Headers
        ref_defs = ReferenceDefinition.objects.filter(model_name=model_name, is_active=True).values_list('field_key', flat=True)
        ref_keys = list(ref_defs)

        headers = ['ID', 'Number', 'Date']
        if model_name == 'voucher':
            headers.extend(['Type', 'Status', 'Narration'])
        elif model_name == 'invoice':
            headers.extend(['Type', 'Status', 'Partner', 'Total'])

        headers.extend(ref_keys)
        ws.append(headers)

        for obj in queryset:
            row = [obj.id]
            if model_name == 'voucher':
                row.extend([
                    str(obj.voucher_number), 
                    str(obj.voucher_date), 
                    str(obj.voucher_type), 
                    str(obj.status), 
                    str(obj.narration)
                ])
            elif model_name == 'invoice':
                row.extend([
                    str(obj.invoice_number), 
                    str(obj.invoice_date), 
                    str(obj.invoice_type), 
                    str(obj.status), 
                    str(obj.partner) if obj.partner else '', 
                    str(obj.total_amount)
                ])
            
            # JSON Fields
            refs = getattr(obj, 'user_references', {}) or {}
            for key in ref_keys:
                row.append(str(refs.get(key, '')))
            
            ws.append(row)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        wb.save(response)
        return response

    @staticmethod
    def export_to_pdf(queryset, model_name, filename="export.pdf"):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        
        p = canvas.Canvas(response, pagesize=A4)
        p.setTitle(f"Export {model_name}")
        p.drawString(50, 800, f"Export: {model_name.capitalize()}s")
        p.line(50, 795, 550, 795)
        
        y = 770
        p.setFont("Helvetica", 10)
        
        for obj in queryset:
            if model_name == 'voucher':
                text = f"{obj.voucher_number} | {obj.voucher_date} | {obj.voucher_type} | {obj.status}"
            else:
                text = f"{obj.invoice_number} | {obj.invoice_date} | {obj.status} | {obj.total_amount}"
            
            p.drawString(50, y, text)
            
            # Show refs
            refs = getattr(obj, 'user_references', {}) or {}
            if refs:
                ref_text = "Refs: " + ", ".join([f"{k}: {v}" for k, v in refs.items()])
                p.setFont("Helvetica", 8)
                p.setFillColorRGB(0.4, 0.4, 0.4)
                p.drawString(60, y - 12, ref_text)
                p.setFont("Helvetica", 10)
                p.setFillColorRGB(0, 0, 0)
                y -= 15
            
            y -= 20
            if y < 50:
                p.showPage()
                p.setFont("Helvetica", 10)
                y = 800
        
        p.save()
        return response
