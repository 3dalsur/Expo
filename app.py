from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import datetime
import qrcode
from PIL import Image
import random  # Importar el módulo random

# Importaciones adicionales para justificación de párrafos
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as PlatypusImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.units import inch

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

    # Usar SimpleDocTemplate para manejar el flujo de texto y justificación
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []

    # Configuración de estilos
    styles = getSampleStyleSheet()
    # Estilo para títulos centrados
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        alignment=1, # 1 es para centrado
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=1, # 1 es para centrado
    )
    # Estilo para texto de cuerpo justificado
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        alignment=TA_JUSTIFY, # TA_JUSTIFY para justificación completa
        spaceAfter=12
    )
    # Estilo para las líneas sin justificar (ej. fechas)
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        spaceAfter=12
    )

    # Fecha actual
    fecha_actual = datetime.date.today().strftime("%d de %B de %Y")
    
    # Generar un número aleatorio de 6 dígitos
    numero_aleatorio = random.randint(100000, 999999)

    # Títulos
    story.append(Paragraph("INFORME DE EXPROPIACION", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("DIRECCION DE VIALIDAD", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("REGION DE LOS RIOS", subtitle_style))
    story.append(Spacer(1, 24))

    # Párrafos del contenido con justificación
    p1_text = f"Informe de Expropiacion N° {numero_aleatorio},<br/><br/>1. La direccion Regional de Vialidad informa que, a la fecha de este documento y de acuerdo a los antecedentes que actualmente existen de los proyectos de esta direccion, la propiedad ubicada en la comuna de VALDIVIA, Región de Los Riós, identificada con el Rol de Avaluo SII N° {rol}, no se encontraria afecta a expropiacion con motivo de futuro proyecto en el sector."
    p2_text = "2. Este documento no exime a la propiedad del cumplimiento de las obligaciones principales emanadas de los instrumentos de Planificacion Territorial vigentes o de otros proyectos, por lo tanto el interesado debera consultar en los organismos pertinentes sobre la materia."
    p3_text = f"3. Se otorga a peticion de: {nombre}, RUT {rut}, por su solicitud SIAC N° {siac} y para los fines que estime convenientes."
    p4_text = "4. Este informe no acredita dominio de la propiedad y la informacion contenida en el se ha determinado en base a los antecedentes del inmueble proporcionados por el interesado, de modo que cualquier inexactitud de los mismos no es responsabilidad de este servicio"
    p5_text = "5. El presente documento no es garantia de que el predio no pueda ser expropiado futuro."
    p6_text = f"Nro. {numero_aleatorio}"

    story.append(Paragraph(p1_text, body_style))
    story.append(Paragraph(p2_text, body_style))
    story.append(Paragraph(p3_text, body_style))
    story.append(Paragraph(p4_text, body_style))
    story.append(Paragraph(p5_text, body_style))
    story.append(Spacer(1, 12)) # Espacio antes de la fecha y el número
    story.append(Paragraph(p6_text, normal_style))
    
    story.append(Spacer(1, 24))

    # Fecha al final
    story.append(Paragraph(f"Valdivia, {fecha_actual}.", normal_style))

    # --- Generación y adición del QR de verificación ---
    verification_url = f"https://labsurconsultores.cl/valida_doc/"
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
    
    # Agregar la imagen del QR al documento
    qr_image = PlatypusImage(img_buffer, width=100, height=100)
    
    story.append(Spacer(1, 50)) # Espacio para el QR
    story.append(qr_image)
    story.append(Paragraph("Escanee para verificar", styles['Normal']))

    # Construir el documento
    doc.build(story)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='carta_verificacion.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)