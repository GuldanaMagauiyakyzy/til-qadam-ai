import streamlit as st

st.set_page_config(
    page_title="TIL QADAM AI",
    page_icon="🗣️",
    layout="wide"
)

st.title("TIL QADAM AI")
st.write("Әр дыбыс – бір қадам, әр қадам – үлкен жетістік!")
st.caption("Логопедтерге арналған ЖИ платформасы")

st.header("Тапсырма құрастырғыш")

age = st.selectbox("Баланың жасы", [3, 4, 5, 6, 7], index=2)
sound = st.selectbox("Мақсатты дыбыс", ["Ш", "С", "Л", "Р", "Ж", "Қ"])
stage = st.selectbox(
    "Машықтандыру кезеңі",
    ["Буындар", "Сөздер", "Сөз тіркестері",
     "Сөйлемдер", "Сурет бойынша әңгіме",
     "Дыбыстарды ажырату"],
    index=1
)
level = st.selectbox(
    "Күрделілік деңгейі",
    ["Жеңіл", "Орташа", "Күрделі"]
)
count = st.number_input(
    "Тапсырма саны", min_value=1, max_value=10, value=5
)

if st.button("Тапсырма құрастыру", type="primary"):
    st.success("Генератордың алғашқы нұсқасы іске қосылды!")
    st.write("Жасы:", age)
    st.write("Дыбысы:", sound)
    st.write("Кезеңі:", stage)
    st.write("Деңгейі:", level)
    st.write("Тапсырма саны:", count)
    st.info("Келесі кезеңде нақты ЖИ генерациясы қосылады.")
