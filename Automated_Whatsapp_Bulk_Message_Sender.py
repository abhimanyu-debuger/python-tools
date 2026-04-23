import pandas as pd
import pywhatkit as kit
import time

# ======================================================
# 🔁 SELECT MODE
# ======================================================
USE_EXCEL = True   # ✅ True = Excel | False = Manual list


# ======================================================
# 📄 EXCEL FORMAT (contacts.xlsx)
# ======================================================
# Your Excel MUST look like this:
#
#   contact        | message
#   ---------------|-------------------------
#   9752014643     | Hello, this is test
#   8888888888     | Meeting at 5 PM
#   7000000000     | Please check email
#
# ⚠️ Rules:
# - Column names EXACT: contact, message
# - No spaces in column names
# - Contact = 10 digit number (no +91 needed)
# ======================================================


# ======================================================
# 📥 LOAD DATA (BASED ON MODE)
# ======================================================
if USE_EXCEL:
    file_path = "contacts.xlsx"
    df = pd.read_excel(file_path)

    data = []
    for index, row in df.iterrows():
        data.append({
            "contact": str(row['contact']),
            "message": str(row['message'])
        })

else:
    # 🧾 MANUAL MODE (No Excel needed)
    data = [
        {"contact": "9752014643", "message": "Hello from code"},
        {"contact": "8888888888", "message": "Meeting at 5 PM"},
        {"contact": "7000000000", "message": "Test message"}
    ]


# ======================================================
# 📞 FUNCTION TO FORMAT NUMBER
# ======================================================
def format_phone(phone):
    phone = str(phone).strip().replace(" ", "").replace("-", "")

    # Add +91 if missing
    if not phone.startswith("+") and len(phone) == 10:
        phone = "+91" + phone

    return phone


# ======================================================
# 🚀 SEND MESSAGES
# ======================================================
for item in data:
    phone = format_phone(item["contact"])
    message = item["message"]

    try:
        print(f"Sending message to {phone}...")

        kit.sendwhatmsg_instantly(
            phone_no=phone,
            message=message,
            wait_time=10,
            tab_close=True
        )

        time.sleep(15)  # avoid WhatsApp block

    except Exception as e:
        print(f"Failed for {phone}: {e}")

print("✅ All messages processed!")