from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import datetime
import qrcode
from PIL import Image

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        rut = request.form['rut']
        nombre = request.form['nombre']
        direccion = request.form['direccion']

        return generate_pdf(rut, nombre, direccion)
    return render_template('index.html')

def generate_pdf(rut, nombre, direccion):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Configuración de la carta
    width, height = letter
    margin = 72 # 1 pulgada de margen

    # Fecha actual
    fecha_actual = datetime.date.today().strftime("%d de %B de %Y")
    c.drawString(width - margin - c.stringWidth(fecha_actual), height - margin, fecha_actual)

    # Remitente (puedes personalizar esto)
    c.drawString(margin, height - margin - 50, "De: Tu Empresa S.A.")
    c.drawString(margin, height - margin - 65, "Dirección de la Empresa #123")
    c.drawString(margin, height - margin - 80, "Santiago, Chile")

    # Destinatario
    c.drawString(margin, height - margin - 120, f"Para: {nombre}")
    c.drawString(margin, height - margin - 135, f"RUT: {rut}")
    c.drawString(margin, height - margin - 150, f"Dirección: {direccion}")

    # Título de la carta
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - margin - 200, "CARTA DE CONFIRMACIÓN DE DATOS")

    # Contenido de la carta
    c.setFont("Helvetica", 12)
    y_position = height - margin - 250
    lines = [
        f"Estimado/a {nombre},",
        "",
        "Por medio de la presente, confirmamos la recepción y registro de sus datos en nuestro sistema.",
        "A continuación, detallamos la información proporcionada por usted:",
        "",
        f"   - RUT: {rut}",
        f"   - Nombre Completo: {nombre}",
        f"   - Dirección: {direccion}",
        "",
        "Agradecemos su confianza. Si tiene alguna duda o necesita realizar alguna",
        "modificación, por favor no dude en contactarnos.",
        "",
        "Atentamente,",
        "El equipo de Tu Empresa S.A."
    ]

    for line in lines:
        c.drawString(margin, y_position, line)
        y_position -= 15 # Espacio entre líneas

    # --- Generación y adición del QR de verificación ---
    verification_data = f"Documento validado para RUT: {rut}, Nombre: {nombre}"
    verification_url = f"https://www.ejemplo.com/verificar?id={rut}" # Reemplaza con tu URL de verificación real

    # Generar el código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Convertir la imagen PIL a un formato que reportlab pueda usar (BytesIO)
    img_buffer = io.BytesIO()
    img_qr.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    # *** CÓDIGO MOVIDO AQUÍ PARA CORREGIR UnboundLocalError ***
    # Ajusta las coordenadas (x, y) y el tamaño (ancho, alto) según tu diseño
    qr_x = width - margin - 150 # Posición X desde la derecha
    qr_y = margin + 50        # Posición Y desde abajo
    qr_size = 100             # Tamaño del QR (cuadrado)

    # Dibujar la imagen del QR en el PDF
    c.drawImage(ImageReader(img_buffer), qr_x, qr_y, width=qr_size, height=qr_size)

    # Añadir texto debajo del QR (opcional)
    c.setFont("Helvetica", 8)
    c.drawString(qr_x + 5, qr_y - 15, "Escanee para verificar")


    c.showPage()
    c.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='carta_verificacion.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)