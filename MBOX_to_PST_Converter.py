import os
import mailbox
import email
import datetime
import email.utils
import win32com.client

def mbox_to_pst(mbox_path, pst_path, pst_name="ConvertedMBOX"):
    mbox_path = os.path.abspath(mbox_path)
    pst_path = os.path.abspath(pst_path)

    if not os.path.exists(mbox_path):
        raise FileNotFoundError(f"MBOX file not found: {mbox_path}")

    print(f"✅ Input MBOX: {mbox_path}")
    print(f"✅ Output PST: {pst_path}")

    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

    # Create PST
    print("📦 Creating PST file...")
    outlook.AddStoreEx(pst_path, 3)
    pst_folder = None
    for store in outlook.Stores:
        if os.path.abspath(store.FilePath).lower() == pst_path.lower():
            pst_folder = store.GetRootFolder()
            break

    if not pst_folder:
        raise Exception("Failed to attach PST to Outlook session.")

    pst_folder.Name = pst_name
    inbox_folder = pst_folder.Folders.Add("Imported Emails")

    # Open MBOX file
    mbox = mailbox.mbox(mbox_path)
    total = len(mbox)
    print(f"📬 Total messages to import: {total}\n")

    for idx, message in enumerate(mbox, start=1):
        try:
            msg = email.message_from_bytes(message.as_bytes())
            subject = msg.get('subject', '(No Subject)')
            body_text = ""
            html_body = ""
            attachments = []

            # Parse message date
            date_str = msg.get('date')
            parsed_date = None
            if date_str:
                try:
                    parsed_tuple = email.utils.parsedate_tz(date_str)
                    if parsed_tuple:
                        parsed_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(parsed_tuple))
                except Exception:
                    parsed_date = None

            # Extract message body and attachments
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in disposition:
                        body_text += part.get_payload(decode=True).decode(errors="ignore")
                    elif content_type == "text/html" and "attachment" not in disposition:
                        html_body += part.get_payload(decode=True).decode(errors="ignore")
                    elif "attachment" in disposition:
                        filename = part.get_filename()
                        if filename:
                            attachments.append((filename, part.get_payload(decode=True)))
            else:
                content_type = msg.get_content_type()
                if content_type == "text/html":
                    html_body = msg.get_payload(decode=True).decode(errors="ignore")
                else:
                    body_text = msg.get_payload(decode=True).decode(errors="ignore")

            # Create Outlook mail item
            mail_item = outlook.Application.CreateItem(0)
            mail_item.Subject = subject
            mail_item.To = msg.get('to', '')
            mail_item.CC = msg.get('cc', '')
            mail_item.BCC = msg.get('bcc', '')

            # Assign HTML or plain body
            if html_body.strip():
                mail_item.HTMLBody = html_body
            else:
                mail_item.Body = body_text.strip() or "(Empty Body)"

            # Add attachments
            for filename, filedata in attachments:
                temp_path = os.path.join(os.getenv("TEMP"), filename)
                with open(temp_path, "wb") as f:
                    f.write(filedata)
                mail_item.Attachments.Add(temp_path)
                os.remove(temp_path)

            # ✅ Use ReceivedTime instead of SentOn
            if parsed_date:
                try:
                    mail_item.ReceivedTime = parsed_date
                except Exception:
                    pass

            # Save and move mail
            mail_item.Save()
            mail_item.Move(inbox_folder)

            print(f"[{idx}/{total}] Imported: {subject}")

        except Exception as e:
            print(f"❌ Error importing message {idx}: {e}")

    print(f"\n✅ Conversion complete! PST file is ready at:\n{pst_path}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    mbox_path = r"janmejay.verma_Email--archive@simplexengg.in-5l5rjW.mbox"
    pst_path = r"janmejay.verma_Email--archive@simplexengg.in-5l5rjW.pst"
    mbox_to_pst(mbox_path, pst_path)