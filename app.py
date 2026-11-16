import streamlit as st
from openai import OpenAI
import base64
import re

st.set_page_config(
    page_title="TIL QADAM AI",
    page_icon="🗣️",
    layout="wide"
)

st.title("🗣️ TIL QADAM AI")
st.write("Әр дыбыс – бір қадам, әр қадам – үлкен жетістік!")
st.caption("Логопедтерге арналған ЖИ платформасы")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

WORDS = {
    "Ш": ["Шар", "Шана", "Шие", "Шаш", "Шелек"],
    "С": ["Су", "Сағат", "Сәбіз", "Сиыр", "Сөмке"],
    "Л": ["Алма", "Бала", "Балық", "Лақ", "Гүл"],
    "Р": ["Ара", "Арба", "Қар", "Тарақ", "Орамал"],
    "Ж": ["Жалау", "Жапырақ", "Жүзім", "Жол", "Жастық"],
    "З": ["Зымыран", "Зәулім үй", "Қаз", "Көз", "Қыз"],
    "Қ": ["Қасық", "Қоян", "Қалам", "Қар", "Қайық"],
    "Ғ": ["Ағаш", "Таға", "Сағат", "Қағаз", "Жаға"],
    "Ң": ["Аң", "Таң", "Шаң", "Қоңырау", "Жаңғақ"]
}

if "tasks" not in st.session_state:
    st.session_state.tasks = ""

if "picture" not in st.session_state:
    st.session_state.picture = None

if "picture_word" not in st.session_state:
    st.session_state.picture_word = ""

tab1, tab2 = st.tabs([
    "✨ Тапсырма генераторы",
    "🖼️ Суретті тапсырмалар"
])

with tab1:
    st.header("Ақылды тапсырма генераторы")

    age = st.selectbox(
        "Баланың жасы", [3, 4, 5, 6, 7], index=2
    )

    sound = st.selectbox(
        "Мақсатты дыбыс", list(WORDS.keys())
    )

    stage = st.selectbox(
        "Машықтандыру кезеңі",
        [
            "Буындар",
            "Сөздер",
            "Сөз тіркестері",
            "Сөйлемдер",
            "Сурет бойынша әңгіме",
            "Дыбыстарды ажырату"
        ]
    )

    level = st.selectbox(
        "Күрделілік деңгейі",
        ["Жеңіл", "Орташа", "Күрделі"]
    )

    count = st.number_input(
        "Тапсырма саны",
        min_value=1,
        max_value=10,
        value=5
    )

    if st.button("✨ Тапсырма құрастыру", type="primary"):
        prompt = f"""
Сен қазақ тіліндегі логопедиялық тапсырмаларды
құрастыратын әдістемелік көмекшісің.

Баланың жасы: {age}
Мақсатты дыбыс: {sound}
Кезең: {stage}
Күрделілік: {level}
Тапсырма саны: {count}

Міндетті талаптар:
1. Тек қазақ тілінде жаз.
2. Дәл {count} тапсырма құрастыр.
3. Тек таңдалған кезеңге сәйкес тапсырма бер.
4. Буын кезеңінде сөздер мен сөйлемдерді араластырма.
5. Сөз кезеңінде нақты қазақша сөздерді қолдан.
6. Мақсатты дыбыс сөзде немесе буында болуы тиіс.
7. Жас ерекшелігі мен күрделілікті ескер.
8. Әр тапсырмаға қысқа нұсқаулық бер.
9. Ойдан шығарылған сөздерді қолданба.
10. Сурет жоқ болса, сурет бар деп көрсетпе.
11. Диагноз қойма.
12. Дыбыстарды ажыратуда екінші дыбысты көрсет.
13. Нәтижені нөмірленген тапсырмалар түрінде бер.
"""

        try:
            with st.spinner("Тапсырмалар жасалып жатыр..."):
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    instructions=(
                        "Сен қазақ тілінің фонетикасын "
                        "ескеретін логопедиялық көмекшісің."
                    ),
                    input=prompt,
                    max_output_tokens=2200
                )

            st.session_state.tasks = response.output_text

        except Exception as e:
            st.error("Тапсырма құрастыру мүмкін болмады.")
            st.code(str(e))

    if st.session_state.tasks:
        st.success("Тапсырмалар дайын!")
        st.markdown(st.session_state.tasks)

        plain_text = re.sub(
            r"\\(.?)\\*", r"\1",
            st.session_state.tasks
        )

        st.download_button(
            "📥 Мәтінді жүктеу",
            data=plain_text,
            file_name="til_qadam_tapsyrmalar.txt",
            mime="text/plain"
        )

with tab2:
    st.header("🖼️ Суретті тапсырмалар")

    picture_sound = st.selectbox(
        "Дыбысты таңдаңыз",
        list(WORDS.keys()),
        key="picture_sound"
    )

    word = st.selectbox(
        "Суретке арналған сөз",
        WORDS[picture_sound]
    )

    method = st.radio(
        "Суретті таңдау әдісі",
        [
            "🤖 ЖИ арқылы сурет жасау",
            "📁 Өз суретімді жүктеу"
        ]
    )

    if method == "🤖 ЖИ арқылы сурет жасау":
        st.info(
            "ЖИ сурет генерациясы API балансынан "
            "қосымша қаражат жұмсайды."
        )

        if st.button("🎨 Сурет жасау", type="primary"):
            try:
                with st.spinner("Сурет жасалып жатыр..."):
                    response = client.images.generate(
                        model="gpt-image-1-mini",
                        prompt=(
                            "Create one clear, simple educational "
                            "illustration for a preschool speech "
                            "therapy picture card. "
                            f"Object: {word}. "
                            "Use the Kazakh meaning of this word. "
                            "Single recognizable subject, "
                            "white background, clean outlines, "
                            "child-friendly style, no letters, "
                            "no text, no watermark."
                        ),
                        size="1024x1024",
                        n=1
                    )

                    image_bytes = base64.b64decode(
                        response.data[0].b64_json
                    )

                    st.session_state.picture = image_bytes
                    st.session_state.picture_word = word

            except Exception as e:
                st.error("Сурет жасау кезінде қате шықты.")
                st.code(str(e))

    else:
        uploaded = st.file_uploader(
            "Суретті жүктеңіз",
            type=["png", "jpg", "jpeg"]
        )

        if uploaded is not None:
            st.session_state.picture = uploaded.getvalue()
            st.session_state.picture_word = word

    if st.session_state.picture:
        st.subheader("Дайын сурет")

        st.image(
            st.session_state.picture,
            width=320
        )

        show_word = st.checkbox(
            "Суреттің астына сөзді жазу",
            value=True
        )

        if show_word:
            st.markdown(
                f"### {st.session_state.picture_word}"
            )

        st.download_button(
            "📥 Суретті жүктеу",
            data=st.session_state.picture,
            file_name="til_qadam_suret.png",
            mime="image/png"
        )

st.divider()
st.caption(
    "ЖИ жасаған тапсырмалар мен суреттерді "
    "қолданар алдында логопед тексеруі қажет. "
    "Баланың жеке деректерін енгізбеңіз."
)
