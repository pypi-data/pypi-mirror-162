import requests

def generateQR(text):
    response = requests.get(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={text}")

    with open("Result1.jpg", "wb") as f:
        f.write(response.content)