"""Generate a sample Excel file for testing."""
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = "Contacts"
ws.append(["Name", "PhoneNumber", "Message"])
ws.append(["Alice Johnson", "+14155551234", "Hello {Name}, check out our spring sale!"])
ws.append(["Bob Smith", "+447911123456", "Hi {Name}, exclusive deal just for you 🎉"])
ws.append(["Carlos García", "+5215512345678", "¡Hola {Name}! Tenemos ofertas especiales"])
ws.append(["Diana Chen", "+8613812345678", "Hello {Name}, VIP member discount inside"])
ws.append(["Fatima Ali", "+923001234567", "Hello {Name}, limited time offer!"])
ws.append(["Hans Mueller", "+4915112345678", ""])
ws.append(["Yuki Tanaka", "+819012345678", ""])
ws.append(["Invalid Row", "not-a-number", "This should fail validation"])
ws.append(["Empty Phone", "", "This should also fail"])

wb.save("sample_contacts.xlsx")
print("Created sample_contacts.xlsx")
