import re
import io
import html
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def make_pdf(content):
    font_dir = Path(__file__).resolve().parent / "fonts"
    regular = font_dir / "DejaVuSans.ttf"
    bold = font_dir / "DejaVuSans-Bold.ttf"
    if not regular.exists() or not bold.exists():
        raise FileNotFoundError("fonts қалтасындағы DejaVuSans қаріптері табылмады")
    if "Kaz" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("Kaz", str(regular)))
    if "KazBold" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("KazBold", str(bold)))
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=43, leftMargin=43, topMargin=48, bottomMargin=48, title="Жеке түзету-дамыту бағдарламасы")
    base = ParagraphStyle("KazBody", fontName="Kaz", fontSize=9.5, leading=15, spaceAfter=7, textColor=colors.HexColor("#26363B"))
    heading = ParagraphStyle("KazHeading", parent=base, fontName="KazBold", fontSize=11, leading=17, spaceBefore=12, spaceAfter=7, textColor=colors.HexColor("#176D76"))
    title = ParagraphStyle("KazTitle", parent=heading, fontSize=15, leading=22, alignment=TA_CENTER, spaceAfter=20)
    story = [Paragraph("ЖЕКЕ ТҮЗЕТУ-ДАМЫТУ БАҒДАРЛАМАСЫ", title), Paragraph("ЖИ әзірлеген жоба. Маман тексеріп, бекітуі қажет.", base), Spacer(1, 10)]
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 6)); continue
        is_heading = line.startswith("#") or bool(re.match(r"^\d+\.\s+\S", line))
        line = re.sub(r"^#{1,6}\s*", "", line)
        line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
        line = re.sub(r"^[-*]\s+", "• ", line)
        story.append(Paragraph(html.escape(line), heading if is_heading else base))
    def page_number(canvas, document):
        canvas.setFont("Kaz", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(A4[0] - 43, 28, f"{document.page}")
    doc.build(story, onFirstPage=page_number, onLaterPages=page_number)
    return buffer.getvalue()

import streamlit as st
from openai import OpenAI

st.set_page_config(page_title='LOGO PLAN AI', page_icon='🧩', layout='wide')
st.markdown('''<style>
.stApp {background:#f7fafc}
.block-container {max-width:1000px;padding-top:2rem}
h1,h2,h3 {color:#176d76}
div[data-testid="stForm"] {background:white;padding:18px;border-radius:16px;border:1px solid #d9e8ea}
</style>''', unsafe_allow_html=True)
st.title('🧩 LOGO PLAN AI')
st.write('Логопед пен дефектологқа арналған 3 немесе 6 айлық жеке түзету-дамыту бағдарламасын әзірлеуге арналған ЖИ көмекші')
st.caption('ЖИ маманның жұмысын қолдайды, бірақ кәсіби бағалауды алмастырмайды.')

if 'generated_plan' not in st.session_state:
    st.session_state.generated_plan = ''

with st.form('plan_form'):
    col1, col2 = st.columns(2)
    with col1:
        specialist = st.selectbox('Маман бағыты', ['Логопед', 'Дефектолог'])
        age = st.selectbox('Баланың жасы', [2, 3, 4, 5, 6, 7, 8, 9, 10], index=3)
        duration = st.selectbox('Бағдарлама мерзімі', ['3 ай', '6 ай'])
    with col2:
        level = st.selectbox('Қолдау деңгейі', ['Көп қолдау қажет', 'Ішінара қолдау қажет', 'Өздігінен орындайды'])
        focus = st.text_input('Түзету-дамыту жұмысының негізгі бағыттары', placeholder='Мысалы: фонематикалық қабылдау, дыбыс айту, байланыстырып сөйлеу')
        strengths = st.text_area('Бала орындай алатын дағдылар (аты-жөнін жазбаңыз)', placeholder='Мысалы: нұсқауды түсінеді, суреттегі заттарды атайды', height=90)
    difficulties = st.text_area('Жұмысты қажет ететін дағдылар', placeholder='Мысалы: Ш дыбысын сөйлемде С дыбысымен алмастырады', height=90)
    submitted = st.form_submit_button('✨ Жеке түзету-дамыту бағдарламасын құрастыру', type='primary')

if submitted:
    if not focus.strip() or not difficulties.strip():
        st.warning('Негізгі жұмыс бағыты мен жұмысты қажет ететін дағдыларды толтырыңыз.')
    else:
        try:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            prompt = f'''Маман бағыты: {specialist}
Жасы: {age}
Бағдарлама мерзімі: {duration}
Қолдау деңгейі: {level}
Негізгі бағыт: {focus}
Қалыптасқан дағдылар: {strengths or 'Көрсетілмеген'}
Жұмысты қажет ететін дағдылар: {difficulties}

Тек қазақ тілінде 3 немесе 6 айға арналған БАЛАНЫҢ ЖЕКЕ ТҮЗЕТУ-ДАМЫТУ БАҒДАРЛАМАСЫНЫҢ жобасын жаса.
Бұл бір сабақтың конспектісі ЕМЕС. Әр айға бөлінген ұзақ мерзімді түзету-дамыту бағдарламасы болуы керек.
Маман бағытына сай салаларды таңда: логопед үшін сөйлеуді түсіну, сөздік қор, грамматикалық құрылым, байланыстырып сөйлеу, дыбыс айту, фонематикалық процестер және қажет болса сөйлеудің моторлық компоненттері; дефектолог үшін қабылдау, зейін, есте сақтау, ойлау, ұсақ моторика, оқу әрекетіне алғышарттар. Барлық саланы мәжбүрлі түрде қоспа, тек берілген деректерге қатыстысын таңда.
Мына бөлімдер міндетті:
1. Бағдарлама паспорты: маман бағыты, жас, мерзім, басым бағыттар (жеке деректерсіз).
2. Түсінік хат: бағдарламаның өзектілігі, баланың бастапқы даму деңгейі, қалыптасқан және дамытуға қажет дағдылар. Диагноз бен нормативтік құжаттарды ойдан қоспа. Белгісіз тұстарды «нақтылау қажет» деп көрсет.
3. Бағдарламаның жалпы мақсаты және 3–6 өлшенетін жеке міндет.
4. Түзету-дамыту жұмысының мазмұны: қалыптасқан дағдылар және дамытуға қажет дағдылар. Белгісіз тұстарды «нақтылау қажет» деп көрсет.
5. Кесте: «Түзету бағыты | Бастапқы деңгей | Мақсат | Жұмыс мазмұны/әдістер | Күтілетін нәтиже | Бағалау көрсеткіші».
6. Айлық кезеңдер: дәл {duration} мерзіміне сәйкес әр айды жеке көрсет, әр айда басым мақсат, жұмыс мазмұны және аралық нәтиже болсын. Алдыңғы дағдылар қалыптаспай тұрып келесі күрделі кезеңге автоматты көшпе.
7. Бастапқы, аралық және қорытынды мониторинг: өлшемдер, бақылау тәсілі, қажет болғанда бағдарламаны қайта қарау шарттары.
8. Ата-анамен жұмыс: үйде қолдануға болатын қысқа, нақты ұсыныстар.
Жаттығуларды бір сабаққа арналған минуттық конспект ретінде жазба.
Күтілетін нәтижелерді кепілдендірме, баланың жеке даму қарқынын ескер.
Диагноз қойма, берілмеген фактілерді ойдан қоспа, тек маманның бекітуіне арналған жоба ұсын.
'''
            with st.spinner('ЖИ түзету-дамыту бағдарламасын дайындап жатыр...'):
                response = client.responses.create(
                    model='gpt-4.1-mini',
                    instructions='Сен қазақ тілінде жұмыс істейтін логопедиялық және дефектологиялық әдістемелік көмекшісің. Диагноз қоймайсың. Маманның кәсіби тексеруін талап етесің.',
                    input=prompt,
                    max_output_tokens=3000,
                )
            result = (response.output_text or '').strip()
            if not result:
                st.error('ЖИ бос жауап қайтарды. Кейінірек қайталап көріңіз.')
            else:
                st.session_state.generated_plan = result
                st.success('Бағдарлама дайын!')
        except Exception as exc:
            st.error('Бағдарламаны жасау кезінде қате шықты. API баптауларын және балансты тексеріңіз.')
            with st.expander('Қате туралы техникалық ақпарат'):
                st.code(str(exc))

if st.session_state.generated_plan:
    st.subheader('📋 Жеке түзету-дамыту бағдарламасының жобасы')
    st.markdown(st.session_state.generated_plan)
    edited = st.text_area('✏️ Қажет болса, бағдарламаны өңдеңіз', value=st.session_state.generated_plan, height=350)
    clean = re.sub(r'\*\*(.*?)\*\*', r'\1', edited)
    st.download_button('📥 Бағдарламаны TXT форматында жүктеу', data=clean, file_name='logo_plan_ai_bagdarlama.txt', mime='text/plain; charset=utf-8')
    try:
        pdf_bytes = make_pdf(edited)
        st.download_button('📄 Бағдарламаны PDF форматында жүктеу', data=pdf_bytes, file_name='logo_plan_ai_bagdarlama.pdf', mime='application/pdf', type='primary')
    except Exception as exc:
        st.error('PDF дайындау кезінде қате шықты.')
        with st.expander('Техникалық ақпарат'):
            st.code(str(exc))
    st.info('Бұл — ЖИ жасаған әдістемелік жоба. Қолданар алдында маман тексеріп, баланың нақты қажеттілігіне бейімдеуі тиіс.')

st.divider()
st.caption('🔒 Нақты балалардың аты-жөнін, мекенжайын, медициналық құжаттарын немесе басқа жеке деректерін енгізбеңіз.')

