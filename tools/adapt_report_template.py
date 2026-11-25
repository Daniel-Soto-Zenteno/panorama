"""Adapt the report to the supplied INACAP DOCX while preserving its package furniture."""
import copy
import hashlib
import io
import argparse
import shutil
import re
import runpy
import subprocess
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Image, Spacer, PageBreak, Preformatted
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT/'.local/formato'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--template', type=Path, required=True, help='Plantilla INACAP original en DOCX')
REFERENCE = parser.parse_args().template.resolve()
TMP.mkdir(parents=True, exist_ok=True)
OUTPUT = ROOT/'docs/Informe_Evaluacion_3_Panorama_Formato_INACAP.docx'
POPLER = shutil.which('pdftoppm')
if not POPLER:
    raise SystemExit('Instala Poppler y agrega pdftoppm al PATH.')
reference_hash = hashlib.sha256(REFERENCE.read_bytes()).hexdigest()

# Reuse the report's structured source; do not extract prose from a PDF.
captured=[]
original_build=SimpleDocTemplate.build
SimpleDocTemplate.build=lambda self, flowables, **kwargs: captured.extend(flowables)
try:
    source=runpy.run_path(str(ROOT/'tools/build_report.py'))
finally:
    SimpleDocTemplate.build=original_build

doc=Document(REFERENCE)
body=doc._element.body
samples=[copy.deepcopy(p._p) for p in doc.paragraphs]
section=copy.deepcopy(doc.sections[0]._sectPr)
for child in list(body):
    if child.tag != qn('w:sectPr'):
        body.remove(child)

def set_prop(parent,tag,attrs):
    old=parent.find(qn(tag))
    if old is None:old=OxmlElement(tag);parent.append(old)
    for k,v in attrs.items():old.set(qn(k),str(v))
    return old

def run_style(run,font='Tahoma',size=11,bold=False,color='000000'):
    rp=run._r.get_or_add_rPr()
    set_prop(rp,'w:rFonts',{'w:ascii':font,'w:hAnsi':font,'w:cs':font,'w:eastAsia':font})
    set_prop(rp,'w:sz',{'w:val':round(size*2)})
    set_prop(rp,'w:szCs',{'w:val':round(size*2)})
    set_prop(rp,'w:color',{'w:val':color})
    if bold:set_prop(rp,'w:b',{})

def paragraph(text='',role='body',keep=False):
    p=doc.add_paragraph()
    idx={'body':25,'heading':26,'subheading':27,'caption':25,'code':25,'cell':25}[role]
    props=copy.deepcopy(samples[idx].find(qn('w:pPr')))
    p._p.insert(0,props)
    for old in list(props):
        if old.tag==qn('w:pStyle'):props.remove(old)
    if role=='heading':
        p.style=doc.styles['Heading 1'];p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next=True
    elif role=='subheading':
        p.style=doc.styles['Heading 2'];p.paragraph_format.keep_with_next=True
    else:
        p.paragraph_format.keep_with_next=keep
    p.paragraph_format.widow_control=True
    if role in ['caption','cell','code']:
        p.paragraph_format.space_after=Pt(5 if role=='caption' else 0)
        p.paragraph_format.line_spacing=1.1
    font,size,color='Tahoma',11,'000000'
    if role=='heading':size,color=18,'EE0000'
    if role=='subheading':size,color=14,'EE0000'
    if role in ['caption','cell']:size=9
    if role=='code':font,size='Consolas',8.5
    run_style(p.add_run(text),font,size,color=color)
    return p

def plain(item):
    if isinstance(item,Paragraph):return item.getPlainText()
    return str(item)

def image_paragraph(item,width_limit=527,height_limit=450,container=None):
    p=container.add_paragraph() if container else doc.add_paragraph()
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after=Pt(5)
    p.paragraph_format.keep_with_next=True
    scale=min(1,width_limit/item.drawWidth,height_limit/item.drawHeight)
    p.add_run().add_picture(item.filename,width=Pt(item.drawWidth*scale),height=Pt(item.drawHeight*scale))
    return p

def drawing_image(item):
    idx=len(list(TMP.glob('uml-*.pdf')))+1
    pdf=TMP/f'uml-{idx}.pdf';png=TMP/f'uml-{idx}.png'
    renderPDF.drawToFile(item,str(pdf))
    subprocess.run([str(POPLER),'-singlefile','-r','180','-png',str(pdf),str(png.with_suffix(''))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    image_paragraph(Image(str(png),width=item.width,height=item.height),height_limit=330)

def add_table(item):
    rows=item._cellvalues
    t=doc.add_table(rows=len(rows),cols=len(rows[0]));t.autofit=False
    widths=getattr(item,'_colWidths',None)
    if not widths or any(not isinstance(w,(int,float)) for w in widths):widths=[1]*len(rows[0])
    total=sum(widths)
    image_table=any(isinstance(v,Image) for row in rows for v in row)
    toc=bool(rows and len(rows[0])==2 and plain(rows[0][0]).startswith('1 Introducción'))
    for col,w in zip(t.columns,widths):col.width=Pt(527*w/total)
    if toc:
        set_prop(t._tbl.tblPr,'w:tblCaption',{'w:val':'IndicePanorama'})
    for ri,row in enumerate(rows):
        trPr=t.rows[ri]._tr.get_or_add_trPr()
        set_prop(trPr,'w:cantSplit',{})
        if ri==0 and not image_table and not toc:set_prop(trPr,'w:tblHeader',{})
        for ci,val in enumerate(row):
            cell=t.cell(ri,ci);cell.width=Pt(527*widths[ci]/total)
            pr=cell._tc.get_or_add_tcPr()
            margins=set_prop(pr,'w:tcMar',{})
            for edge in ['top','left','bottom','right']:
                set_prop(margins,'w:'+edge,{'w:w':60 if edge in ['top','bottom'] else 90,'w:type':'dxa'})
            set_prop(pr,'w:vAlign',{'w:val':'center'})
            if not image_table and not toc:
                borders=set_prop(pr,'w:tcBorders',{})
                for edge in ['top','left','bottom','right']:set_prop(borders,'w:'+edge,{'w:val':'single','w:sz':4,'w:color':'D9D9D9'})
                if ri==0:set_prop(pr,'w:shd',{'w:fill':'EFEFEF'})
            if isinstance(val,Image):
                image_paragraph(val,width_limit=240,height_limit=440,container=cell)
                cell._tc.remove(cell.paragraphs[0]._p)
            else:
                p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.08
                run_style(p.add_run(plain(val)),size=9,bold=ri==0 and not toc)
                if toc and ci==1:p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    after=doc.add_paragraph();after.paragraph_format.space_after=Pt(0);after.paragraph_format.line_spacing=Pt(3)
    run_style(after.add_run(''),size=3)

# Clone the actual cover from the reference and replace its three editable slots.
for idx in range(9):
    clone=copy.deepcopy(samples[idx])
    if idx in [2,3,8]:
        for child in list(clone):
            if child.tag!=qn('w:pPr'):clone.remove(child)
        from docx.text.paragraph import Paragraph as WordParagraph
        p=WordParagraph(clone,doc._body)
        if idx==2:
            p.style=doc.styles['Title'];run_style(p.add_run('PANORAMA'),size=20,bold=True,color='EE0000')
        elif idx==3:
            run_style(p.add_run('Informe técnico de implementación\nseguridad y pruebas'),size=20,color='EE0000')
        else:
            text='NOMBRE: Daniel Soto, Diego Villota, Mauro Sotomayor\nCARRERA: Analista Programador\nASIGNATURA: Ingeniería de Software TI3043\nPROFESOR: José Jara\nFECHA: 25 de noviembre de 2026'
            run_style(p.add_run(text),size=12)
    body.insert(len(body)-1,clone)

# Skip the old cover, retaining the complete index and development source.
cover=True
page_pending=False
metrics_text=None
for item in captured:
    if cover:
        if isinstance(item,PageBreak):cover=False;page_pending=True
        continue
    if isinstance(item,PageBreak):page_pending=True
    elif isinstance(item,Paragraph):
        role={'Heading1':'heading','Heading2':'subheading','Caption':'caption'}.get(item.style.name,'body')
        text=item.getPlainText()
        if text.startswith('Las aperturas se incrementan con una expresión F'):
            metrics_text=text
            continue
        # This count must be verified after layout, rather than carry the old PDF count.
        text=text.replace('El informe contiene 23 páginas de desarrollo, además de portada, índice, referencias y anexos. ','')
        p=paragraph(text,role)
        if page_pending:p.paragraph_format.page_break_before=True;page_pending=False
        if text=='5 Datos e interfaces desarrolladas' and metrics_text:
            paragraph(metrics_text)
    elif isinstance(item,Table):add_table(item)
    elif isinstance(item,Preformatted):paragraph('\n'.join(item.lines),'code')
    elif isinstance(item,Image):image_paragraph(item)
    elif isinstance(item,Drawing):drawing_image(item)
    elif isinstance(item,Spacer):pass
    else:raise TypeError(type(item))

# Preserve the template's original institutional back cover as its own page.
spacer=doc.add_paragraph();spacer.paragraph_format.space_after=Pt(58)
spacer.paragraph_format.page_break_before=True
body.insert(len(body)-1,copy.deepcopy(samples[66]))
doc.core_properties.title='Panorama Informe técnico de implementación seguridad y pruebas'
doc.core_properties.author='Daniel Soto, Diego Villota y Mauro Sotomayor'
doc.core_properties.subject='Evaluación 3 Ingeniería de Software TI3043'
buffer=io.BytesIO();doc.save(buffer)
generated=ZipFile(io.BytesIO(buffer.getvalue()))
original=ZipFile(REFERENCE)
# python-docx serializes unrelated parts; transplant only the intended mutations.
mutable={'word/document.xml','word/_rels/document.xml.rels','[Content_Types].xml','docProps/core.xml','word/footer1.xml','word/settings.xml'}
from lxml import etree as ET
footer=ET.fromstring(original.read('word/footer1.xml'))
anchor_run=OxmlElement('w:r');pict=OxmlElement('w:pict');anchor_run.append(pict)
vml='urn:schemas-microsoft-com:vml'
shape=ET.SubElement(pict,'{'+vml+'}shape')
shape.set('id','PanoramaPageNumber');shape.set('stroked','f');shape.set('filled','f')
shape.set('style','position:absolute;margin-left:544pt;margin-top:742pt;width:25pt;height:28pt;z-index:100;mso-position-horizontal-relative:page;mso-position-vertical-relative:page')
textbox=ET.SubElement(shape,'{'+vml+'}textbox');textbox.set('inset','0,0,0,0')
content=OxmlElement('w:txbxContent');textbox.append(content)
number=OxmlElement('w:p');pr=OxmlElement('w:pPr');number.append(pr);content.append(number)
set_prop(pr,'w:jc',{'w:val':'right'})
set_prop(pr,'w:spacing',{'w:before':0,'w:after':0,'w:line':200,'w:lineRule':'exact'})
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');r=OxmlElement('w:r');rp=OxmlElement('w:rPr');r.append(rp)
set_prop(rp,'w:rFonts',{'w:ascii':'Tahoma','w:hAnsi':'Tahoma','w:cs':'Tahoma'});set_prop(rp,'w:sz',{'w:val':16});set_prop(rp,'w:szCs',{'w:val':16})
t=OxmlElement('w:t');t.text='1';r.append(t);field.append(r);number.append(field)
footer.find(qn('w:p')).append(anchor_run)
settings=ET.fromstring(original.read('word/settings.xml'));set_prop(settings,'w:updateFields',{'w:val':'true'})
overrides={'word/footer1.xml':ET.tostring(footer,xml_declaration=True,encoding='UTF-8',standalone=True),'word/settings.xml':ET.tostring(settings,xml_declaration=True,encoding='UTF-8',standalone=True)}
with ZipFile(OUTPUT,'w',ZIP_DEFLATED) as z:
    for part in original.namelist():
        z.writestr(part,overrides.get(part,generated.read(part) if part in mutable else original.read(part)))
    for part in generated.namelist():
        if part not in original.namelist():z.writestr(part,generated.read(part))
with ZipFile(OUTPUT) as z:
    for part in original.namelist():
        if part not in mutable:assert z.read(part)==original.read(part),part
    from lxml import etree as ET
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    r=ET.fromstring(z.read('word/document.xml'))
    assert ET.tostring(r.find('w:body/w:sectPr',ns))==ET.tostring(ET.fromstring(original.read('word/document.xml')).find('w:body/w:sectPr',ns))
assert hashlib.sha256(REFERENCE.read_bytes()).hexdigest()==reference_hash
print('DOCX generado y partes institucionales preservadas:',OUTPUT)
