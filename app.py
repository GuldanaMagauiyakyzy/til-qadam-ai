import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="TIL QADAM AI",
    page_icon="🗣️",
    layout="wide"
)

st.title("🗣️ TIL QADAM AI")
st.write("Әр дыбыс – бір қадам, әр қадам – үлкен жетістік!")
st.caption("Логопедтерге арналған ЖИ платформасы")

st.header("✨ Ақылды тапсырма генераторы")

age = st.selectbox(
    "Баланың жасы",
    [3, 4, 5, 6, 7],
    index=2
)

sound = st.selectbox(
    "Мақсатты дыбыс",
    ["Ш", "С", "Л", "Р", "Ж", "З", "Қ", "Ғ", "Ң"]
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
    try:
        client = OpenAI(
            api_key=st.secrets["OPENAI_API_KEY"]
        )

        prompt = f"""
Сен қазақ тіліндегі логопедиялық тапсырмаларды
құрастыратын кәсіби әдістемелік көмекшісің.

Баланың жасы: {age}
Мақсатты дыбыс: {sound}
Машықтандыру кезеңі: {stage}
Күрделілік деңгейі: {level}
Тапсырма саны: {count}

Талаптар:
1. Тапсырмаларды тек қазақ тілінде жаз.
2. Баланың жас ерекшелігін ескер.
3. Мақсатты дыбысқа сәйкес материал таңда.
4. Буындар мен сөздер фонетикалық тұрғыдан дұрыс болсын.
5. Сөздер қазақ тілінде қолданылатын нақты сөздер болсын.
6. Әр тапсырмаға қысқа нұсқаулық бер.
7. Тапсырмаларды нөмірлеп жаз.
8. Сурет қажет болса, суретке арналған сипаттама бер.
9. Диагноз қойма.
10. Дыбыстарды ажырату кезеңінде салыстырылатын
екінші дыбысты анық көрсет.
"""

        with st.spinner("ЖИ тапсырмаларды құрастырып жатыр..."):
            response = client.responses.create(
                model="gpt-4.1-mini",
                instructions=(
                    "Сен қазақ тілі фонетикасын ескеретін "
                    "логопедиялық әдістемелік көмекшісің."
                ),
                input=prompt,
                max_output_tokens=1800
            )

        result = response.output_text

        st.success("Тапсырмалар дайын!")
        st.markdown(result)

        st.download_button(
            "📥 Тапсырмаларды жүктеу",
            data=result,
            file_name="til_qadam_tapsyrmalar.txt",
            mime="text/plain"
        )

        st.info(
            "ЖИ жасаған материалды қолданар алдында "
            "логопед тексеруі қажет."
        )

    except Exception as e:
        st.error("Тапсырма құрастыру кезінде қате шықты.")
        st.code(str(e))
