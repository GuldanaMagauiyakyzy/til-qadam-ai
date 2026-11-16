import streamlit as st

st.set_page_config(
    page_title="TIL QADAM AI",
    page_icon="🗣️",
    layout="wide"
)

st.title("TIL QADAM AI")
st.write("Әр дыбыс – бір қадам, әр қадам – үлкен жетістік!")
st.caption("Логопедтерге арналған ЖИ платформасы")

st.header("Ақылды тапсырма құрастырғыш")

age = st.selectbox("Баланың жасы", [3, 4, 5, 6, 7], index=2)

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
        "Байланыстырып сөйлеу",
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

if st.button("✨ ЖИ арқылы тапсырма құрастыру", type="primary"):
    st.subheader("Тапсырмалар")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        prompt = f"""
        Сен қазақ тіліндегі логопедиялық тапсырмалар
        құрастыратын кәсіби әдістемелік көмекшісің.

        Баланың жасы: {age}
        Мақсатты дыбыс: {sound}
        Машықтандыру кезеңі: {stage}
        Күрделілік деңгейі: {level}
        Тапсырма саны: {count}

        Қазақ тілінде дәл {count} тапсырма құрастыр.

        Талаптар:
        - Тапсырмалар баланың жасына сәйкес болсын.
        - Мақсатты дыбысты дұрыс қолдан.
        - Қазақ тілінің фонетикалық ерекшеліктерін сақта.
        - Ойдан шығарылған сөздерді қолданба.
        - Тапсырмалар түсінікті және нақты болсын.
        - Әр тапсырманы нөмірлеп жаз.
        - Диагноз қойма.
        """

        with st.spinner("ЖИ тапсырмаларды құрастырып жатыр..."):
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

        st.write(response.output_text)
        st.info("Тапсырмаларды қолданар алдында логопед тексеруі қажет.")

    except KeyError:
        st.warning(
            "ЖИ қызметін қосу үшін OPENAI_API_KEY енгізу қажет."
        )
    except Exception as e:
        st.error(f"ЖИ қызметіне қосылу қатесі: {e}")
