# estándar
import os
import re
from random import randint
from datetime import datetime
import locale

# terceros
from dotenv import load_dotenv
from pydantic import BaseModel
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, ListFlowable,
    ListItem, PageBreak, HRFlowable, Preformatted
)

# crewai
from crewai import Agent, Task, Crew, Process, LLM
from crewai.flow.flow import Flow, listen, start
from crewai_tools import SerperDevTool
from crewai_tools import ScrapeWebsiteTool

# SCRAPE
os.environ['OPENAI_API_KEY'] = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

scrape_tool = ScrapeWebsiteTool()

# SERPER
os.environ['SERPER_API_KEY'] = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

serper_tool = SerperDevTool()

# CARGA VARIABLES DE ENTORNO
load_dotenv()

# LLM
llm = LLM(
    model = "openai/qwen3:4b",
    #model = "openai/qwen-mini",
    #model = "openai/deepseek-r1:7b",
    #model = "openai/llama",
    #model = "openai/gemma",
    base_url="https://api.poligpt.upv.es/",
    api_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
)

# AGENTES
investigador = Agent(
    role="Investigador Principal especializado en la recopilación, análisis y síntesis de información sobre {topic}",
    goal=(
        "Realizar una investigación rigurosa, profunda y actualizada sobre {topic}, abarcando sus dimensiones clave, avances recientes, desafíos presentes y perspectivas futuras. "
        "Para ello, utilizará de forma combinada y eficiente las herramientas de búsqueda web (serper_tool) para identificar fuentes relevantes y la extracción web (scrape_tool) para obtener información detallada y precisa. "
        "El resultado será un compendio bien estructurado, claro y preciso, con referencias verificables y pertinentes que respalden cada afirmación."
    ),
    backstory=(
        "Usted es un investigador con amplia experiencia en la identificación, validación y síntesis de información relevante sobre cualquier aspecto relacionado con {topic}. "
        "Aplica criterios exigentes de fiabilidad, actualidad y relevancia en la evaluación de fuentes, y domina el uso combinado de herramientas de búsqueda y extracción web para organizar grandes volúmenes de datos en contenidos comprensibles, útiles y bien estructurados."
    ),
    llm=llm,
    verbose=True,
    tools=[serper_tool, scrape_tool]
)

analista = Agent(
    role="Analista Técnico y Redactor Profesional de informes sobre {topic}",
    goal=(
        "Convertir los resultados de la investigación sobre {topic} en un informe estructurado, claro y profesional, "
        "siguiendo las directrices del modelo institucional proporcionado. "
        "Para asegurar la calidad y profundidad del análisis, utilizará combinadamente serper_tool para complementar información y scrape_tool para acceder a datos adicionales relevantes durante el proceso de redacción."
    ),
    backstory=(
        "Usted es un analista con experiencia en transformar hallazgos sobre {topic} en informes académicos y técnicos de alta calidad. "
        "Su trabajo se basa en seguir estándares formales establecidos, como los detallados en guías oficiales, "
        "y en la utilización eficiente y conjunta de herramientas de búsqueda y extracción web para enriquecer el contenido con información precisa y actualizada."
    ),
    llm=llm,
    verbose=True,
    tools=[serper_tool, scrape_tool]
)

verificador = Agent(
    role="Revisor de Calidad y Auditor de Contenidos especializados en {topic}",
    goal=(
        "Auditar el informe sobre {topic} para garantizar la precisión del contenido, la validez de las fuentes, la claridad estructural y la calidad editorial general. "
        "Utilizará de manera combinada serper_tool para verificar la actualidad y fiabilidad de la información, y scrape_tool para contrastar detalles y resolver posibles dudas técnicas o conceptuales durante la revisión. "
        "Detectará y corregirá errores, omisiones, inconsistencias o afirmaciones no respaldadas, asegurando que el contenido final sea riguroso, coherente y profesional."
    ),
    backstory=(
        "Usted es un auditor especializado en la validación de informes sobre {topic}, con sólida experiencia en revisión técnica, lógica argumentativa y corrección editorial. "
        "Examina cada aspecto del documento con atención crítica, apoyándose en la búsqueda y extracción web combinadas para asegurar que el resultado sea impecable en fondo y forma."
    ),
    llm=llm,
    verbose=True,
    tools=[serper_tool, scrape_tool]
)

formateador = Agent(
    role="Especialista en Maquetación Profesional de documentos sobre {topic}",
    goal=(
        "Diseñar y ensamblar el informe final sobre {topic} en un documento digital (Word o PDF) con presentación profesional, estructura clara y formato optimizado para su lectura y distribución. "
        "Aunque no requiere herramientas de búsqueda o extracción web, podrá consultar documentación de estilo y ejemplos si se le proporcionan."
    ),
    backstory=(
        "Usted es un experto en diseño editorial con experiencia en transformar contenido validado sobre {topic} en documentos visualmente claros, bien jerarquizados y listos para ser compartidos o impresos. "
        "Cuida la presentación visual, la coherencia tipográfica y la navegación del documento para que sea fácil de entender y atractivo para el lector."
    ),
    llm=llm,
    verbose=True,
    tools=[]
)

# TAREAS
task_investigacion = Task(
    description=(
        "Realizar una investigación exhaustiva y rigurosa sobre el tema '{topic}', empleando todos los recursos disponibles y pertinentes, "
        "especialmente la herramienta de extracción web (scrape_tool) para obtener información precisa, actualizada y de fuentes fidedignas. "
        "El objetivo es elaborar un documento profesional, claro y bien estructurado, que incluya las secciones: Introducción, Contexto o Antecedentes, Desarrollo, Resultados Clave, Discusión, Conclusiones y Perspectivas Futuras. "
        "Durante la investigación se debe aplicar un enfoque crítico y profesional, asegurando la validez y relevancia de las fuentes consultadas. "
        "Incluir un apartado final con referencias bibliográficas formateadas correctamente según el estilo APA, que respalden todas las afirmaciones y datos presentados."
    ),
    expected_output=(
        "Un documento de investigación profesional, claro, organizado y fundamentado sobre '{topic}', que reúna información actual y relevante con referencias verificadas en formato APA."
    ),
    agent=investigador,
    tools=[serper_tool, scrape_tool]
)

task_analisis = Task(
    description=(
        "A partir del documento de investigación sobre '{topic}', elaborar un análisis técnico o científico detallado y profesional. "
        "El informe debe presentar una estructura formal y clara: Título, Resumen Ejecutivo, Introducción, Desarrollo Analítico por secciones, Conclusiones y Recomendaciones si procede. "
        "La estructura y estilo deben ajustarse al modelo institucional contenido en el documento PDF proporcionado. "
        "El análisis debe basarse en la información obtenida, complementada con recursos como la extracción web (scrape_tool), manteniendo un alto estándar de calidad y rigor. "
        "El informe debe utilizar un lenguaje formal y preciso, apto para un público técnico o académico, e incluir referencias actualizadas y formateadas en APA que validen el contenido presentado."
    ),
    expected_output=(
        "Un informe técnico o científico con análisis estructurado, lenguaje profesional y argumentación sólida que profundice en los aspectos clave de '{topic}', "
        "incluyendo recomendaciones fundamentadas y referencias en formato APA conforme a los estándares institucionales."
    ),
    agent=analista,
    tools=[serper_tool, scrape_tool],
    context=[task_investigacion]
)

task_verificacion = Task(
    description=(
        "Revisar críticamente el informe elaborado sobre '{topic}', asegurando la coherencia interna, calidad y precisión de la información presentada, así como la claridad de redacción y estructura. "
        "Comprobar que los argumentos sean sólidos, las referencias estén correctamente citadas en formato APA y la terminología sea consistente. "
        "Utilizar la herramienta de extracción web (scrape_tool) y otros recursos para verificar datos, ampliar información o resolver dudas técnicas. "
        "El resultado debe ser un informe de revisión detallado con sugerencias de mejora o, si procede, la confirmación de que el documento está listo para formateo y distribución, respetando el formato profesional y las citas APA."
    ),
    expected_output=(
        "Un informe de verificación detallado que garantice la calidad, rigor y solidez del documento sobre '{topic}', o el documento corregido y anotado listo para su maquetación final, con referencias APA completas y adecuadas."
    ),
    agent=verificador,
    tools=[serper_tool, scrape_tool],
    context=[task_analisis]
)

task_formateo = Task(
    description=(
        "Diseñar y generar un documento final profesional basado en el informe validado sobre '{topic}'. "
        "Aplicar un estilo visual claro, uniforme y cuidado, incluyendo jerarquía tipográfica, márgenes adecuados, interlineado correcto, y estructura clara de títulos y subtítulos. "
        "Asegurar que las referencias bibliográficas estén formateadas correctamente en APA y sean fácilmente consultables. "
        "El resultado debe ser un documento presentable, distribuible y profesionalmente maquetado en formato PDF o DOCX."
    ),
    expected_output=(
        "Un archivo final en formato PDF o DOCX, maquetado profesionalmente, limpio, legible y estructurado para ser presentado o publicado sobre '{topic}', con referencias en formato APA."
    ),
    agent=formateador,
    tools=[],
    context=[task_verificacion]
)

# ESTADO ESTRUCTURADO
class DocumentState(BaseModel):
    topic: str = input("Introduce el tema de la investigación: ")
    investigacion: str = ""
    analisis: str = ""
    verificacion: str = ""

# LIMPIAR ARCHIVO TXT
def limpiar_txt_markdown(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = [l for l in lines if not l.strip() in ("```", '"""')]
    with open(txt_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

# AUXILIAR PDF
def _footer_canvas(canvas, doc, date_str):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    page_num_text = f"Página {doc.page}"
    canvas.drawString(doc.leftMargin, 10 * mm, date_str)
    canvas.drawRightString(doc.width + doc.leftMargin, 10 * mm, page_num_text)
    canvas.restoreState()

# GENERAR PDF
def generar_pdf(txt_path='archivo.txt',
                pdf_path='documento_final.pdf',
                imagen_path=None,
                titulo_portada="Informe Práctica 2",
                subtitulo_portada="Trabajo generado con crewAI"):
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            leftMargin=25*mm, rightMargin=25*mm,
                            topMargin=25*mm, bottomMargin=25*mm)

    styles = getSampleStyleSheet()
    base_font = 'Helvetica' 
    bold_font = base_font + '-Bold'
    italic_font = base_font + '-Oblique'
    bold_italic_font = base_font + '-BoldOblique'

    style_body = ParagraphStyle(
        'BodyText', parent=styles['BodyText'], fontName=base_font, 
        fontSize=11, leading=15, spaceAfter=3*mm, 
        alignment=TA_LEFT, firstLineIndent=0
    )

    estilos = {
        'CoverTitle': ParagraphStyle('CoverTitle', parent=styles['h1'], fontName=bold_font, 
                                      fontSize=34,
                                      alignment=TA_CENTER, spaceBefore=inch, spaceAfter=12*mm,
                                      textColor=colors.HexColor("#2C3E50")),
        'CoverSubtitle': ParagraphStyle('CoverSubtitle', parent=styles['h2'], fontName=base_font, fontSize=18,
                                        alignment=TA_CENTER, spaceAfter=5*mm, textColor=colors.HexColor("#34495E")),
        'CoverDate': ParagraphStyle('CoverDate', parent=styles['Normal'], fontName=italic_font, fontSize=12,
                                    alignment=TA_CENTER, spaceAfter=2*inch, textColor=colors.HexColor("#7F8C8D")),
        
        'h1': ParagraphStyle('h1', parent=styles['Heading1'], fontName=bold_font, fontSize=20, spaceBefore=10*mm, spaceAfter=6*mm, 
                             textColor=colors.HexColor("#2C3E50"), keepWithNext=True),
        'h2': ParagraphStyle('h2', parent=styles['Heading2'], fontName=bold_font, fontSize=16, spaceBefore=8*mm, spaceAfter=4*mm, 
                             textColor=colors.HexColor("#34495E"), keepWithNext=True),
        'h3': ParagraphStyle('h3', parent=styles['Heading3'], fontName=bold_font, fontSize=14, spaceBefore=6*mm, spaceAfter=3*mm, 
                             textColor=colors.HexColor("#7F8C8D"), keepWithNext=True),
        
        'body': style_body,

        'bullet': ParagraphStyle('bullet', parent=style_body,
                                 leftIndent=10*mm, bulletIndent=0*mm,
                                 spaceBefore=1*mm, spaceAfter=1*mm, bulletFontName=base_font, bulletFontSize=11),

        'numbered': ParagraphStyle('numbered', parent=style_body, 
                                   leftIndent=10*mm, bulletIndent=0*mm,
                                   spaceBefore=1*mm, spaceAfter=1*mm, firstLineIndent=0),

        'code': ParagraphStyle(
            'code', parent=styles['Code'], fontName='Courier', fontSize=9.5,
            textColor=colors.HexColor("#333333"), backColor=colors.HexColor("#F5F5F5"),
            borderColor=colors.HexColor("#E0E0E0"), borderWidth=0.5, borderPadding=6,
            leading=12, leftIndent=0*mm, rightIndent=0*mm, spaceBefore=3*mm, spaceAfter=3*mm,
            wordWrap='CJK', allowWidows=1, allowOrphans=1
        ),

        'blockquote': ParagraphStyle('blockquote', parent=style_body, 
                                     fontSize=10.5, textColor=colors.HexColor("#555555"),
                                     leftIndent=10*mm, spaceBefore=3*mm, spaceAfter=3*mm,
                                     borderLeftColor=colors.HexColor("#DDDDDD"), borderLeftWidth=2,
                                     borderPadding=(0, 0, 0, 5*mm)),
    }
    
    flowables = []

    original_locale_time = locale.getlocale(locale.LC_TIME) # Guarda el locale actual para LC_TIME
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
            except locale.Error:
                try:
                    locale.setlocale(locale.LC_TIME, 'Spanish')
                except locale.Error:
                    print("Advertencia: No se pudo configurar el locale a español para la fecha. Se usará el formato por defecto.")
    
    today_date_str = datetime.now().strftime("%d de %B de %Y")
    
    try:
        locale.setlocale(locale.LC_TIME, original_locale_time)
    except locale.Error:
        print("Advertencia: No se pudo restaurar el locale original para LC_TIME.")
    flowables.append(Paragraph(titulo_portada, estilos['CoverTitle']))
    flowables.append(Spacer(1, 0.5*inch))
    flowables.append(Paragraph(subtitulo_portada, estilos['CoverSubtitle']))
    flowables.append(Paragraph(f"Generado el: {today_date_str}", estilos['CoverDate'])) # Usará la fecha formateada
    flowables.append(PageBreak())

    if imagen_path and os.path.exists(imagen_path):
        try:
            img = Image(imagen_path, width=150*mm, height=100*mm)
            img.hAlign = 'CENTER'
            flowables.append(img)
            flowables.append(Spacer(1, 12*mm))
        except Exception as e:
            print(f"Advertencia: No se pudo cargar la imagen {imagen_path}: {e}")

    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            lines = [l.rstrip() for l in f]
    except FileNotFoundError:
        print(f"Error: El archivo {txt_path} no fue encontrado.")
        flowables.append(Paragraph(f"Error: El archivo de contenido '{txt_path}' no fue encontrado.", estilos['body']))
        try:
            doc.build(flowables, onFirstPage=lambda c, d: _footer_canvas(c, d, today_date_str),
                               onLaterPages=lambda c, d: _footer_canvas(c, d, today_date_str))
        except Exception as e_build:
            print(f"Error construyendo PDF de error: {e_build}")
        return

    idx = 0
    def apply_inline_markdown(text_md):
        processed_text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<font name="'+bold_italic_font+r'">\1</font>', text_md)
        processed_text = re.sub(r'\*\*(.+?)\*\*', r'<font name="'+bold_font+r'">\1</font>', processed_text)
        processed_text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<font name="'+italic_font+r'">\1</font>', processed_text)
        processed_text = re.sub(r'\*(.+?)\*', r'<font name="'+italic_font+r'">\1</font>', processed_text)
        processed_text = re.sub(r'~~(.+?)~~', r'<strike>\1</strike>', processed_text)
        processed_text = re.sub(r'`(.+?)`', r'<font face="Courier" color="#2E8B57">\1</font>', processed_text)
        return processed_text

    while idx < len(lines):
        line = lines[idx]

        if not line.strip() or line.strip() == ",,,":
            idx += 1
            continue

        if line.strip().startswith('```'):
            code_block_lines = []
            idx += 1
            while idx < len(lines) and not lines[idx].strip().startswith('```'):
                code_block_lines.append(lines[idx])
                idx += 1
            idx += 1 
            code_text = "\n".join(code_block_lines)
            code_text = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            flowables.append(Preformatted(code_text, estilos['code']))
            continue

        current_style_key = None
        text_content = line
        if line.startswith('# '):
            current_style_key = 'h1'
            text_content = line[2:]
        elif line.startswith('## '):
            current_style_key = 'h2'
            text_content = line[3:]
        elif line.startswith('### '):
            current_style_key = 'h3'
            text_content = line[4:]

        if current_style_key:
            text_content = apply_inline_markdown(text_content)
            flowables.append(Paragraph(text_content, estilos[current_style_key]))
            idx += 1
            continue
        
        if line.strip() in ['---', '***', '- - -', '___']:
            flowables.append(Spacer(1, 3*mm))
            flowables.append(HRFlowable(width="80%", thickness=0.5, color=colors.HexColor("#CCCCCC"),
                                        spaceBefore=1*mm, spaceAfter=1*mm, hAlign='CENTER', vAlign='BOTTOM', lineCap='round'))
            flowables.append(Spacer(1, 3*mm))
            idx += 1
            continue

        if line.startswith('> '):
            blockquote_lines = []
            while idx < len(lines) and lines[idx].startswith('> '):
                blockquote_lines.append(apply_inline_markdown(lines[idx][2:]))
                idx += 1
            flowables.append(Paragraph("<br/>".join(blockquote_lines), estilos['blockquote']))
            continue

        match_numbered = re.match(r'^\s*(\d+)\.\s+(.+)', line)
        if match_numbered:
            items = []
            start_number_val = None
            while idx < len(lines):
                current_line_match = re.match(r'^\s*(\d+)\.\s*(.+)', lines[idx])
                if not current_line_match:
                    break 
                
                num_str, contenido_item = current_line_match.groups()
                if start_number_val is None:
                    start_number_val = int(num_str)

                contenido_item = apply_inline_markdown(contenido_item)
                items.append(ListItem(Paragraph(contenido_item, estilos['numbered']),
                                      bulletText=f"{num_str}."))
                idx += 1
            
            if items:
                list_flowable = ListFlowable(items, bulletType='1', start=str(start_number_val) if start_number_val is not None else None)
                flowables.append(list_flowable)
            continue

        if line.lstrip().startswith(('- ', '* ')):
            items = []
            bullet_char = '•' 
            while idx < len(lines) and (lines[idx].lstrip().startswith('- ') or lines[idx].lstrip().startswith('* ')):
                contenido_item = lines[idx].lstrip()[2:]
                contenido_item = apply_inline_markdown(contenido_item)
                items.append(ListItem(Paragraph(contenido_item, estilos['bullet']), bulletText=bullet_char))
                idx += 1
            if items:
                flowables.append(ListFlowable(items, bulletType='bullet', bulletFontSize=estilos['bullet'].fontSize))
            continue

        text_content = apply_inline_markdown(line)
        flowables.append(Paragraph(text_content, estilos['body']))
        idx += 1

    try:
        doc.build(flowables, onFirstPage=lambda c, d: _footer_canvas(c, d, today_date_str),
                            onLaterPages=lambda c, d: _footer_canvas(c, d, today_date_str))
        print(f"PDF formateado y mejorado generado en: {pdf_path}")
    except Exception as e:
        print(f"Error al construir el PDF: {e}")
        import traceback
        traceback.print_exc()

# FLUJO SECUENCIAL
class DocumentFlow(Flow[DocumentState]):
    @start()
    def realizar_investigacion(self):
        print(f"Iniciando investigación sobre: {self.state.topic}")
        crew = Crew(
            agents=[investigador],
            tasks=[task_investigacion],
            process=Process.sequential,
            verbose=True
        )
        result = crew.kickoff(inputs={"topic": self.state.topic})
        self.state.investigacion = result.raw

    @listen(realizar_investigacion)
    def redactar_analisis(self):
        print("Analizando investigación y redactando informe estructurado...")
        crew = Crew(
            agents=[analista],
            tasks=[task_analisis],
            process=Process.sequential,
            verbose=True
        )
        result = crew.kickoff(inputs={
            "topic": self.state.topic,
            "investigacion": self.state.investigacion
        })
        self.state.analisis = result.raw

    @listen(redactar_analisis)
    def verificar_documento(self):
        print("Verificando precisión y calidad técnica del informe...")
        crew = Crew(
            agents=[verificador],
            tasks=[task_verificacion],
            process=Process.sequential,
            verbose=True
        )
        result = crew.kickoff(inputs={
            "topic": self.state.topic,
            "documento": self.state.analisis
        })
        self.state.verificacion = result.raw
        print("\nFlujo completado. Verificación final realizada.")
        print("\nDocumento final verificado:\n")
        print(self.state.analisis)

    @listen(verificar_documento)
    def generar_documento_final(self):
        print("Generando documento final")
        crew = Crew(
            agents=[formateador],
            tasks=[task_formateo],
            process=Process.sequential,
            verbose=True
        )
        result = crew.kickoff(inputs={
            "topic": self.state.topic,
            "documento": self.state.analisis
        })
        print("Documento final generado:", result.raw)

    @listen(generar_documento_final)
    def guardar_documento(self):
        with open("archivo.txt", "w", encoding="utf-8") as f:
            f.write(self.state.analisis)
        limpiar_txt_markdown("archivo.txt")  # <--- Limpieza antes de generar el PDF
        generar_pdf(txt_path="archivo.txt", pdf_path="documento_final.pdf")

def kickoff():
    flow = DocumentFlow(initial_state=DocumentState())
    flow.kickoff()

def plot():
    flow = DocumentFlow(initial_state=DocumentState())
    flow.plot("flujo_documento.png")

if __name__ == "__main__":
    kickoff()
    plot()
    
    