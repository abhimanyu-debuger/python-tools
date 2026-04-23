import qrcode
import os

def generate_qr(data, filename="qrcode.png", box_size=10, border=4):
    qr = qrcode.QRCode(
        version=None,  # automatic size
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    
    return filename


if __name__ == "__main__":
    link = "https://www.simplexengg.in/home/landing"  # 🔗 change here
    
    file = generate_qr(link, "my_qrcode.png")
    
    print(f"✅ QR Code generated: {file}")
    print(f"📂 Location: {os.path.abspath(file)}")

    # Optional: auto open image
    try:
        os.startfile(file)  # Windows
    except:
        pass