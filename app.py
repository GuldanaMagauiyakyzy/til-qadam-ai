import io
import json
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

import streamlit as st
from openai import OpenAI
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

st.set_page_config(page_title="LOGO PLAN AI", page_icon="🧩", layout="wide")
st.markdown("""<style>.block-container{max-width:1100px;padding-top:2rem}h1,h2,h3{color:#176d76}</style>""", unsafe_allow_html=True)
st.title("🧩 LOGO PLAN AI")
st.write("ПМПК қорытындысы мен бастапқы диагностика негізінде 3 немесе 6 айлық жеке түзету-дамыту бағдарламасының жобасын құрастыру")
st.caption("ЖИ маманның кәсіби бағалауын алмастырмайды. Нақты баланың жеке деректерін енгізбеңіз.")

if "program" not in st.session_state:
    st.session_state.program = None

with st.form("program_form"):
    left, right = st.columns(2)
    with left:
        specialist = st.selectbox("Маман бағыты", ["Логопед", "Дефектолог"])
        age = st.selectbox("Баланың жасы", list(range(2, 18)), index=3)
        motivation = st.selectbox("Баланың ынтасы", ["Жоғары", "Орташа", "Төмен", "Тұрақсыз", "Нақтылау қажет"])
    with right:
        duration = st.selectbox("Бағдарлама мерзімі", ["3 ай", "6 ай"])
        pmpk = st.text_area("ПМПК қорытындысы", placeholder="Қорытындыдағы маңызды тұжырымдарды жеке деректерсіз енгізіңіз", height=115)
    baseline = st.text_area("Баланың жалпы ерекшеліктері және бастапқы диагностика", placeholder="Қалыптасқан дағдылары, сөйлеу/танымдық ерекшеліктері, нұсқауды түсінуі, мінез-құлқы...", height=130)
    needs = st.text_area("Түзету жұмысын қажет ететін дағдылар", placeholder="Мысалы: фонематикалық қабылдау, дыбыс айту, сөздік қор...", height=110)
    submit = st.form_submit_button("✨ Жеке түзету-дамыту бағдарламасын құрастыру", type="primary")

if submit:
    if not pmpk.strip() or not baseline.strip() or not needs.strip():
        st.warning("ПМПК қорытындысын, бастапқы диагностиканы және түзетуді қажет ететін дағдыларды толтырыңыз.")
    else:
        prompt = f"""Маман: {specialist}
Жас: {age}
Ынта: {motivation}
Бағдарлама мерзімі: {duration}
ПМПК қорытындысы: {pmpk}
Бастапқы диагностика және жалпы ерекшеліктері: {baseline}
Түзетуді қажет ететін дағдылар: {needs}

Маман тексеретін ЖЕКЕ ТҮЗЕТУ-ДАМЫТУ БАҒДАРЛАМАСЫНЫҢ жобасын құрастыр.
Бұл сабақ жоспары ЕМЕС. Мерзімді айларға БӨЛМЕ. Барлық жол үшін бір ғана ортақ мерзім — {duration}.
ПМПК мен диагностикаға сүйен. Берілмеген диагноз, қабілет, дерек, нәтиже ойдан шығарылмасын.
Тек осы балаға сәйкес келетін бағыттарды таңда. 5–10 мазмұнды, бір-бірінен бөлек мақсат құрастыр.
Мақсаттар мен күтілетін нәтижелер нақты, бақылауға келетін және қолжетімді болсын; нәтижеге кепілдік берме.
Әр жолда 'direction' (дамыту бағыты), 'goal' (мақсат), 'expected' (күтілетін нәтиже) болсын.
'achievement' және 'notes' жолдары БОС болсын: маман кейін өзі толтырады.
Жауап ТЕК мына JSON объектісі болсын:
{{"rows":[{{"direction":"...","goal":"...","expected":"...","achievement":"","notes":""}}]}}
"""
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            with st.spinner("Бағдарлама әзірленіп жатыр..."):
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    instructions="Қазақ тілінде жұмыс істейтін логопед және дефектологтың әдістемелік көмекшісісің. Тек дұрыс JSON қайтар. Диагноз қойма, айларға бөлме.",
                    input=prompt,
                    text={"format": {"type": "json_object"}},
                    max_output_tokens=3500,
                )
            result = json.loads(response.output_text)
            rows = result.get("rows", [])
            if not isinstance(rows, list) or not rows:
                raise ValueError("ЖИ кесте жолдарын қайтармады")
            cleaned = []
            for item in rows:
                if isinstance(item, dict):
                    cleaned.append({
                        "Бағыты": str(item.get("direction", "")),
                        "Мақсаты": str(item.get("goal", "")),
                        "Күтілетін нәтиже": str(item.get("expected", "")),
                        "Жетістік белгісі": "",
                        "Ескертулер": "",
                    })
            if not cleaned:
                raise ValueError("Кесте бос")
            st.session_state.program = {"specialist": specialist, "age": age, "motivation": motivation,
                                        "duration": duration, "pmpk": pmpk, "baseline": baseline,
                                        "needs": needs, "rows": cleaned}
            st.success("Бағдарлама жобасы дайын!")
        except Exception as exc:
            st.error("ЖИ жауап беру кезінде қате шықты. API кілтін, балансты және интернетті тексеріңіз.")
            with st.expander("Техникалық ақпарат"):
                st.code(str(exc))


def register_fonts():
    font_dir = Path(__file__).resolve().parent / "fonts"
    for name, filename in [("Kaz", "DejaVuSans.ttf"), ("KazBold", "DejaVuSans-Bold.ttf")]:
        path = font_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"Қаріп табылмады: fonts/{filename}")
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(path)))


def make_pdf(program, rows):
    register_fonts()
    out = io.BytesIO()
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    body = ParagraphStyle("BodyKaz", fontName="Kaz", fontSize=8.2, leading=12, spaceAfter=5)
    title = ParagraphStyle("TitleKaz", parent=body, fontName="KazBold", fontSize=13, leading=19, alignment=TA_CENTER, spaceAfter=15)
    head = ParagraphStyle("HeadKaz", parent=body, fontName="KazBold", fontSize=8.1, leading=11)
    small = ParagraphStyle("SmallKaz", parent=body, fontSize=7.4, leading=11)
    def p(value, style=body):
        return Paragraph(escape(str(value or "" )).replace("\n", "<br/>"), style)
    story = [p("ЖЕКЕ ТҮЗЕТУ-ДАМЫТУ БАҒДАРЛАМАСЫ", title)]
    info = [
        ("Бағдарламаның құрылған күні", date.today().strftime("%d.%m.%Y")),
        ("Баланың аты-жөні", "________________________________"),
        ("Туған жылы", "________________"),
        ("ПМПК қорытындысы", program["pmpk"]),
        ("Маман", program["specialist"]),
        ("Бағдарлама мерзімі", program["duration"]),
        ("Баланың жасы", f'{program["age"]} жас'),
        ("Баланың ынтасы", program["motivation"]),
    ]
    for label, value in info:
        story.append(p(f"{label}: {value}"))
    story.append(Spacer(1, 12))
    headers = ["Мерзімі", "Даму жұмыстарының бағыттары, мақсат және күтілетін нәтиже", "Жетістік белгісі", "Ескертулер"]
    data = [[p(x, head) for x in headers]]
    for i, item in enumerate(rows):
        content = [p(item.get("Бағыты", ""), head), p("Мақсаты: " + item.get("Мақсаты", ""), small), p("Күтілетін нәтиже: " + item.get("Күтілетін нәтиже", ""), small)]
        data.append([p(program["duration"], small) if i == 0 else p("", small), content,
                     p(item.get("Жетістік белгісі", ""), small), p(item.get("Ескертулер", ""), small)])
    table = Table(data, colWidths=[61, 322, 81, 59], repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#829da3")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e4f1f2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(table)
    story.append(Spacer(1, 14))
    story.append(p("Балдық бағалау:", head))
    story.append(p("0 — мақсатқа қол жеткізілмеді; 1 — шамамен 25%; 2 — шамамен 50%; 3 — мақсатқа толық қол жеткізілді (100%).", small))
    story.append(p("Қорытынды / ескертулер: __________________________________________________________", small))
    story.append(p("Бұл — ЖИ құрастырған жоба. Маман тексеріп, баланың нақты қажеттіліктеріне бейімдеуі тиіс.", small))
    def footer(canvas, document):
        canvas.setFont("Kaz", 7)
        canvas.drawRightString(A4[0] - 36, 21, str(document.page))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out.getvalue()


if st.session_state.program:
    program = st.session_state.program
    st.subheader("📋 Жеке түзету-дамыту бағдарламасы")
    st.info("Жетістік белгісі мен ескертулерді маман толтырады. Кестедегі мақсаттар мен нәтижелерді PDF жүктемей тұрып түзетуге болады.")
    rows = st.data_editor(program["rows"], num_rows="dynamic", use_container_width=True, key="program_editor")
    st.caption("Бағалау: 0 — қол жеткізілмеді; 1 — 25%; 2 — 50%; 3 — 100%. Бұл шкаланы ұйымның бекітілген бағалау тәртібімен сәйкестендіріңіз.")
    try:
        pdf = make_pdf(program, rows)
        st.download_button("📄 Бағдарламаны PDF форматында жүктеу", pdf, file_name="zheke_tuzetu_damytu_bagdarlamasy.pdf", mime="application/pdf", type="primary")
    except Exception as exc:
        st.error("PDF дайындау кезінде қате шықты.")
        st.code(str(exc))

st.divider()
st.caption("🔒 Баланың аты-жөнін, ЖСН-ын, мекенжайын және медициналық құжаттарының фотосын ЖИ жүйесіне енгізбеңіз.")
