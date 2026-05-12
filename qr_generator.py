import qrcode

# YOUR WEBSITE LINK
url = "https://14tnbattalionnccregistration-production.up.railway.app/"

# CREATE QR
qr = qrcode.make(url)

# SAVE QR IMAGE
qr.save("ncc_qr.png")

print("QR Code Generated Successfully")