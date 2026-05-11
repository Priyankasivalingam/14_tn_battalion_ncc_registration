import qrcode

url = 'http://192.168.1.11:5000/'

img = qrcode.make(url)

img.save('ncc_qr.png')

print("QR Code Generated Successfully")