from flask import Flask, request, render_template, send_file
import qrcode
import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import requests

app = Flask(__name__)

QR_IMAGE_PATH = "static/qr.png"
PDF_PATH = "static/qr.pdf"

def is_valid_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code < 400
    except:
        return False

@app.route("/", methods=["GET", "POST"])
def home():
    qr_code_path = None
    title = ""
    name = ""
    error = ""

    if request.method == "POST":
        link = request.form["link"]
        title = request.form.get("title", "")
        name = request.form.get("name", "")

        if not is_valid_url(link):
            error = "❌ Invalid or unreachable URL. Please enter a real, working website link."
            return render_template("index.html", qr_code=None, title=title, name=name, error=error)

        qr_img = qrcode.make(link).convert("RGB")
        width, height = qr_img.size
        new_height = height + 100
        img_with_text = Image.new("RGB", (width, new_height), "white")
        draw = ImageDraw.Draw(img_with_text)

        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        draw.text((width // 2 - draw.textlength(title, font=font) // 2, 10), title, font=font, fill="black")
        img_with_text.paste(qr_img, (0, 40))
        draw.text((width // 2 - draw.textlength(name, font=font) // 2, height + 50), name, font=font, fill="black")

        os.makedirs("static", exist_ok=True)
        img_with_text.save(QR_IMAGE_PATH)
        qr_code_path = QR_IMAGE_PATH

    return render_template("index.html", qr_code=qr_code_path, title=title, name=name, error=error)


@app.route("/download/<filetype>")
def download(filetype):
    if not os.path.exists(QR_IMAGE_PATH):
        return "QR code not found", 404

    if filetype == "image":
        return send_file(QR_IMAGE_PATH, as_attachment=True)
    elif filetype == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.image(QR_IMAGE_PATH, x=30, y=30, w=150)
        pdf.output(PDF_PATH)
        return send_file(PDF_PATH, as_attachment=True)
    else:
        return "Invalid file type", 400

if __name__ == "__main__":
    app.run(debug=True)