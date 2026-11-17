import base64
import io
import json
import os
import re
import streamlit as st
from openai import OpenAI
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from PIL import Image

st.set_page_config(page_title="TIL QADAM AI", page_icon="🗣️", layout="wide")

st.markdown("""
<style>
.stApp {background:#f7f9ff}
.block-container{max-width:1050px;padding-top:2rem}
.sheet-title{color:#5337a7;font-size:28px;font-weight:800}
.task-card{background:white;border:1px solid #ded9ff;
border-radius:18px;padding:18px;margin:14px 0}
</style>
""", unsafe_allow_html=True)

st.title("🗣️ TIL QADAM AI")
st.caption("Әр дыбыс – бір қадам, әр қадам – үлкен жетістік!")
st.subheader("🎨 Суреттермен безендірілген жұмыс парағы")

st.info(
    "ЖИ тапсырмалар мен суреттерді жасайды. "
    "Әр сурет API балансынан қаражат жұмсайды. "
    "Алғашқы сынаққа 1 тапсырма таңдаңыз."
)

SOUNDS = ["Ш", "С", "Л", "Р", "Ж", "З", "Қ", "Ғ", "Ң"]
STAGES = [
    "Буындар", "Сөздер", "Сөз тіркестері",
    "Сөйлемдер", "Сурет бойынша әңгіме",
    "Дыбыстарды ажырату"
]

with st.form("settings"):
    c1, c2, c3 = st.columns(3)
    age = c1.selectbox("Баланың жасы", [3,4,5,6,7], index=2)
    sound = c2.selectbox("Мақсатты дыбыс", SOUNDS)
    stage = c3.selectbox("Машықтандыру кезеңі", STAGES, index=3)
    level = c1.selectbox("Күрделілік", ["Жеңіл", "Орташа", "Күрделі"])
    count = c2.number_input(
        "Тапсырма саны", min_value=1, max_value=4, value=1
    )
    color_mode = c3.selectbox(
        "Безендіру", ["Түрлі түсті", "Ақ-қара"]
    )
    submitted = st.form_submit_button(
        "✨ Суретті жұмыс парағын құрастыру",
        type="primary"
    )

def fonts():
    import os
    import urllib.request

    font_dir = "/tmp/til_qadam_fonts"
    os.makedirs(font_dir, exist_ok=True)

    font_files = {
        "Kaz": (
            "DejaVuSans.ttf",
            "https://raw.githubusercontent.com/dejavu-fonts/"
            "dejavu-fonts/version_2_37/ttf/DejaVuSans.ttf"
        ),
        "KazBold": (
            "DejaVuSans-Bold.ttf",
            "https://raw.githubusercontent.com/dejavu-fonts/"
            "dejavu-fonts/version_2_37/ttf/DejaVuSans-Bold.ttf"
        )
    }

    for font_name, (filename, url) in font_files.items():
        path = os.path.join(font_dir, filename)

        if not os.path.exists(path):
            urllib.request.urlretrieve(url, path)

        if font_name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(
                TTFont(font_name, path)
            )

def create_tasks(client):
    prompt = f"""
Қазақ тілінде логопедиялық жұмыс парағын құрастыр.

Жасы: {age}
Дыбыс: {sound}
Кезең: {stage}
Деңгей: {level}
Тапсырма саны: {count}

Тек JSON қайтар:
{{"tasks":[{{"title":"Тақырып",
"instruction":"Нұсқаулық",
"text":"Тапсырманың негізгі мәтіні",
"image_prompt":"English description of the illustration"}}]}}

Талаптар:
1. Дәл {count} тапсырма құрастыр.
2. Барлық мәтін қазақ тілінде болсын.
3. Тек таңдалған кезеңге сәйкес материал бер.
4. Сөздер табиғи әрі фонетикалық дұрыс болсын.
5. Мақсатты {sound} дыбысы материалда болсын.
6. Әр сурет тапсырманың мағынасын дәл көрсетсін.
7. Суреттің ішіне жазу енгізбе.
8. Сөйлемдер қысқа әрі түсінікті болсын.
9. «Шынар шырын ішті» сөйлемінде
қыз шырынды стаканнан ішіп отыруы керек.
10. Диагноз қойма.
"""
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "Сен қазақ тіліндегі логопедиялық тапсырмаларды "
            "құрастыратын кәсіби әдістемелік көмекшісің. "
            "Тек жарамды JSON объектісін қайтар. "
            "Жауапта tasks массиві міндетті түрде болсын."
        ),
        input=prompt,
        text={
            "format": {
                "type": "json_object"
            }
        },
        max_output_tokens=3000
    )
        instructions=(
            "Сен қазақша логопедиялық материал "
            "құрастыратын әдістемелік көмекшісің. "
            "Тек жарамды JSON қайтар."
        ),
        input=prompt,
        max_output_tokens=1600
    )
    raw = response.output_text.strip()
   if not raw:
        raise ValueError(
            "ЖИ бос жауап қайтарды. "
            "Тапсырманы қайта құрастыру қажет."
        )

    raw = re.sub(
        r"^(?:json)?\s*|\s*$",
        "",
        raw
    ).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(
            "ЖИ тапсырманы дұрыс форматта қайтармады. "
            "JSON құрылымын тексеру қажет."
        )

    tasks = data["tasks"]
    if len(tasks) != count:
        raise ValueError("Тапсырмалар саны сәйкес емес")
    for task in tasks:
        for key in ["title", "instruction", "text", "image_prompt"]:
            if key not in task:
                raise ValueError("Тапсырма құрылымы толық емес")
    return tasks

def create_picture(client, task):
    style = (
        "Black and white clean line art for coloring."
        if color_mode == "Ақ-қара"
        else "Friendly colorful children's illustration."
    )
    prompt = (
        "Preschool speech therapy worksheet illustration. "
        + task["image_prompt"]
        + ". Show the action and objects accurately. "
        + "No text, no letters, no watermark. "
        + style
    )
    response = client.images.generate(
        model="gpt-image-1-mini",
        prompt=prompt,
        size="1024x1024",
        n=1
    )
    return base64.b64decode(response.data[0].b64_json)

def wrap_words(text, font, size, width):
    lines = []
    line = ""
    for word in text.split():
        candidate = (line + " " + word).strip()
        if line and pdfmetrics.stringWidth(
            candidate, font, size
        ) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines

def make_pdf(tasks, images):
    fonts()
    from reportlab.lib.pagesizes import A4
    W, H = A4
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    purple = HexColor(
        "#6042A8" if color_mode == "Түрлі түсті" else "#222222"
    )
    pale = HexColor(
        "#F0EBFF" if color_mode == "Түрлі түсті" else "#F4F4F4"
    )

    for index, (task, img) in enumerate(zip(tasks, images)):
        pdf.setFillColor(pale)
        pdf.roundRect(
            28, H-112, W-56, 82, 16,
            fill=1, stroke=0
        )

        pdf.setFillColor(purple)
        pdf.setFont("KazBold", 18)
        pdf.drawString(46, H-63, "TIL QADAM AI")

        pdf.setFont("Kaz", 11)
        pdf.drawString(
            46, H-87,
            f"{sound} дыбысы • {age} жас • {stage}"
        )

        pdf.setFont("KazBold", 15)
        y = H-150

        title = f"{index+1}-тапсырма. {task['title']}"
        for line in wrap_words(title, "KazBold", 15, W-96)[:2]:
            pdf.drawString(46, y, line)
            y -= 22

        pdf.setFillColor(HexColor("#222222"))
        pdf.setFont("Kaz", 11)

        for line in wrap_words(
            task["instruction"], "Kaz", 11, W-96
        )[:3]:
            pdf.drawString(46, y-7, line)
            y -= 17

        picture = Image.open(io.BytesIO(img)).convert("RGB")
        iw, ih = picture.size
        scale = min((W-100)/iw, 385/ih)
        dw, dh = iw*scale, ih*scale

        top = min(y-25, H-230)
        pdf.drawImage(
            ImageReader(picture),
            (W-dw)/2, top-dh, dw, dh
        )

        text_y = top-dh-30
        pdf.setFillColor(purple)
        pdf.setFont("KazBold", 16)

        for line in wrap_words(
            task["text"], "KazBold", 16, W-110
        )[:4]:
            if text_y < 75:
                break
            pdf.drawCentredString(W/2, text_y, line)
            text_y -= 23

        pdf.setFillColor(HexColor("#777777"))
        pdf.setFont("Kaz", 8)
        pdf.drawCentredString(
            W/2, 36,
            "ЖИ материалын логопед қолданар алдында тексереді"
        )
        pdf.showPage()

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()

if submitted:
    st.session_state.pop("worksheet", None)
    try:
        client = OpenAI(
            api_key=st.secrets["OPENAI_API_KEY"]
        )

        with st.spinner("Тапсырмалар құрастырылуда..."):
            tasks = create_tasks(client)

        images = []
        progress = st.progress(0)

        for i, task in enumerate(tasks):
            with st.spinner(
                f"{i+1}/{len(tasks)}: сурет жасалып жатыр..."
            ):
                images.append(create_picture(client, task))
            progress.progress((i+1)/len(tasks))

        st.session_state.saved_tasks = tasks
        st.session_state.saved_images = images
        
        result_pdf = make_pdf(tasks, images)

        st.session_state.worksheet = {
            "tasks": tasks,
            "images": images,
            "pdf": result_pdf
        }

    except Exception as e:
        st.error("Жұмыс парағын жасау кезінде қате шықты.")
        st.code(str(e))

if st.session_state.get("worksheet"):
    ws = st.session_state.worksheet
    st.success("Суретті жұмыс парағы дайын!")

    for i, (task, img) in enumerate(
        zip(ws["tasks"], ws["images"])
    ):
        st.markdown(f"### {i+1}-тапсырма. {task['title']}")
        st.write(task["instruction"])
        st.image(img, width=440)
        st.markdown(f"### {task['text']}")

    st.download_button(
        "📄 А4 жұмыс парағын PDF жүктеу",
        data=ws["pdf"],
        file_name="til_qadam_zhumys_paragy.pdf",
        mime="application/pdf",
        type="primary"
    )

    st.warning(
        "ЖИ жасаған материалды логопед тексеруі қажет. "
        "Баланың жеке деректерін енгізбеңіз.")
if (
    st.session_state.get("saved_tasks")
    and st.session_state.get("saved_images")
):
    if st.button("🔄 PDF-ті қайта құрастыру"):
        try:
            pdf_data = make_pdf(
                st.session_state.saved_tasks,
                st.session_state.saved_images
            )
            st.session_state.worksheet = {
                "tasks": st.session_state.saved_tasks,
                "images": st.session_state.saved_images,
                "pdf": pdf_data
            }
            st.success("PDF дайын!")
            st.rerun()
        except Exception as e:
            st.error("PDF жасау кезінде қате шықты.")
            st.code(str(e))


if st.button("🧪 PDF жүйесін тегін тексеру"):
    try:
        from PIL import ImageDraw

        test_image = Image.new("RGB", (600, 600), "white")
        draw = ImageDraw.Draw(test_image)
        draw.rectangle(
            (100, 100, 500, 500),
            outline="purple",
            width=8
        )

        buffer = io.BytesIO()
        test_image.save(buffer, format="PNG")

        test_tasks = [{
            "title": "Сөйлемді қайтала",
            "instruction": "Сөйлемді анық айт.",
            "text": "Шынар шырын ішті.",
            "image_prompt": ""
        }]

        pdf_data = make_pdf(
            test_tasks,
            [buffer.getvalue()]
        )

        st.success("PDF жүйесі дұрыс жұмыс істейді!")

        st.download_button(
            "📄 Сынақ PDF файлын жүктеу",
            data=pdf_data,
            file_name="til_qadam_test.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error("PDF жүйесінде қате бар.")
        st.code(str(e))
