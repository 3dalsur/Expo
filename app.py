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
        rol = request.form['rol']
        rut = request.form['rut']
        nombre = request.form['nombre']
        siac = request.form['siac']

        return generate_pdf(rol, rut, nombre, siac)
    return render_template('index.html')

def generate_pdf(rol, rut, nombre, siac):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Configuración de la carta
    width, height = letter
    margin = 72 # 1 pulgada de margen

    # Fecha actual
    fecha_actual = datetime.date.today().strftime("%d de %B de %Y")
    #c.drawString(width - margin - c.stringWidth(fecha_actual), height - margin, fecha_actual)

    # Remitente (puedes personalizar esto)
    #c.drawString(margin, height - margin - 50, "De: Tu Empresa S.A.")
    #c.drawString(margin, height - margin - 65, "Dirección de la Empresa #123")
    #c.drawString(margin, height - margin - 80, "Santiago, Chile")

    # Destinatario
    #c.drawString(margin, height - margin - 120, f"Para: {nombre}")
    #c.drawString(margin, height - margin - 135, f"RUT: {rut}")
    #c.drawString(margin, height - margin - 150, f"Dirección: {direccion}")

    # Título de la carta
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - margin - 50, "INFORME DE EXPROPIACION")
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - margin - 65, "DIRECCION DE VIALIDAD")
    c.drawCentredString(width / 2, height - margin - 80, "REGION DE LOS RIOS")
    # Contenido de la carta
    c.setFont("Helvetica", 12)
    y_position = height - margin - 150
    lines = [
        f"Informe de Expropiacion N°{nombre},",
        "",
        "1. La direccion Regional de Vialidad informa que, a la fecha de este documento y de.",
        "   acuerdo a los antecedentes que actualmente existen de los proyectos de esta direccion, la",
        "   propiedad ubicada en la comuna de VALDIVIA, Región de Los Riós, identificada con el Rol de",
        f"   Avaluo SII N° {rol}, no se encontraria afecta a expropiacion con motivo de futuro",
        "   proyecto en el sector.",
        "",
        "2. Este documento no exime a la propiedada del cumplimiento de las obligaciones principales",
        "   emanadas de los instrumentos de Planificacion Territorial vigentes o de otros proyectos,",
        "   por lo tanto el interesado debera consultar en los organismos pertinentes sobre la materia.",
        "",
        f"3. Se otorga a peticion de: {nombre}, RUT {rut}, por su solicitud",
        f"   SIAC N° {siac} y para los fines que estime convenientes.",
        "",
        "4. Este informe no acredita dominio de la propiedad y la informacion contenida en el se ha",
        "   determinado en base a los antecedentes del inmueble proporcionados por el interesado,",
        "   de modo que cualquier inexactitud de los mismos no es responsabilidad de este servicio",
        "",
        "5. El presente documento no es garantia de que el predio no pueda ser expropiado",
        "   futuro.",
        "",
        "",
        "",
        f"Valdivia, {fecha_actual}.",
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