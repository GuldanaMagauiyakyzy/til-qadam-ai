import re
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
st.write('Логопед пен дефектологқа арналған интеллектуалды әдістемелік көмекші')
st.caption('ЖИ маманның жұмысын қолдайды, бірақ кәсіби бағалауды алмастырмайды.')

if 'generated_plan' not in st.session_state:
    st.session_state.generated_plan = ''

with st.form('plan_form'):
    col1, col2 = st.columns(2)
    with col1:
        specialist = st.selectbox('Маман бағыты', ['Логопед', 'Дефектолог'])
        age = st.selectbox('Баланың жасы', [2, 3, 4, 5, 6, 7, 8, 9, 10], index=3)
        duration = st.selectbox('Жоспар мерзімі', ['1 сабақ (25–30 минут)', '1 апта', '1 ай'])
    with col2:
        level = st.selectbox('Тапсырмалардың күрделілігі', ['Жеңіл', 'Орташа', 'Күрделі'])
        focus = st.text_input('Негізгі жұмыс бағыты', placeholder='Мысалы: Ш дыбысын сөйлемде машықтандыру')
        strengths = st.text_area('Бала орындай алатын дағдылар (аты-жөнін жазбаңыз)', placeholder='Мысалы: нұсқауды түсінеді, суреттегі заттарды атайды', height=90)
    difficulties = st.text_area('Жұмысты қажет ететін дағдылар', placeholder='Мысалы: Ш дыбысын сөйлемде С дыбысымен алмастырады', height=90)
    submitted = st.form_submit_button('✨ Жеке түзету жоспарын құрастыру', type='primary')

if submitted:
    if not focus.strip() or not difficulties.strip():
        st.warning('Негізгі жұмыс бағыты мен жұмысты қажет ететін дағдыларды толтырыңыз.')
    else:
        try:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            prompt = f'''Маман бағыты: {specialist}
Жасы: {age}
Жоспар мерзімі: {duration}
Күрделілігі: {level}
Негізгі бағыт: {focus}
Қалыптасқан дағдылар: {strengths or 'Көрсетілмеген'}
Жұмысты қажет ететін дағдылар: {difficulties}

Тек қазақ тілінде, кәсіби, қолдануға ыңғайлы әдістемелік жоба жаса.
Мына бөлімдерді міндетті түрде бер:
1. Бастапқы мәліметтердің қысқаша сипаттамасы (диагноз емес)
2. Нақты әрі бақыланатын түзету мақсаттары
3. Кезең-кезеңімен жұмыс жоспары (мерзімге сай)
4. 4–6 нақты жаттығу: мақсат, материал, орындалу барысы
5. Нәтижені бақылау критерийлері
6. Ата-анаға арналған 3–5 ұсыныс
Тапсырмалар жасына және көрсетілген дағдыларға сәйкес болсын.
Ойдан шығарылған сөздер, жалған ғылыми тұжырымдар, автоматты диагноз болмасын.
Берілмеген деректерді нақты факт ретінде көрсетпе. Қажет жерінде маман тексеруі тиіс екенін ескерт.
Егер сөйлеу дыбысы таңдалса, дыбыстың фонетикалық орны мен машықтандыру кезеңін ескер.'''
            with st.spinner('ЖИ әдістемелік жоспарды дайындап жатыр...'):
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
                st.success('Жоспар дайын!')
        except Exception as exc:
            st.error('Жоспарды жасау кезінде қате шықты. API баптауларын және балансты тексеріңіз.')
            with st.expander('Қате туралы техникалық ақпарат'):
                st.code(str(exc))

if st.session_state.generated_plan:
    st.subheader('📋 Дайын жоспар')
    st.markdown(st.session_state.generated_plan)
    edited = st.text_area('✏️ Қажет болса, жоспарды өңдеңіз', value=st.session_state.generated_plan, height=350)
    clean = re.sub(r'\*\*(.*?)\*\*', r'\1', edited)
    st.download_button('📥 Жоспарды TXT форматында жүктеу', data=clean, file_name='logo_plan_ai_zhospar.txt', mime='text/plain; charset=utf-8')
    st.info('Бұл — ЖИ жасаған әдістемелік жоба. Қолданар алдында маман тексеріп, баланың нақты қажеттілігіне бейімдеуі тиіс.')

st.divider()
st.caption('🔒 Нақты балалардың аты-жөнін, мекенжайын, медициналық құжаттарын немесе басқа жеке деректерін енгізбеңіз.')
