from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = "Contacts"
ws.append(["Row", "Name", "Phone", "Message", "Status"])

ws.column_dimensions["A"].width = 8
ws.column_dimensions["B"].width = 14
ws.column_dimensions["C"].width = 18
ws.column_dimensions["D"].width = 24
ws.column_dimensions["E"].width = 12

ws["C2"].number_format = "@"

out = "contacts_template.xlsx"
wb.save(out)
print(f"Wrote {out}")
