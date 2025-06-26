import streamlit as st
import openai
from PIL import Image
import base64
import os
import io
import requests

# --- OpenAI API 키 설정 ---
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
except KeyError:
    st.error("OpenAI API 키를 찾을 수 없습니다. 환경 변수에 OPENAI_API_KEY를 설정해주세요.")

SERVER_URL = "http://13.124.198.232:3000/register-meal"

def preprocess_image(image: Image.Image, max_size=(512, 512), quality=85):
    image.thumbnail(max_size)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    return buffer.read()

def analyze_image(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert who accurately identifies only the names of foods in the image. "
                        "Do not provide any other explanations, greetings, or comments."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What foods are in this image? List all food names in korean and separated by commas."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "low"
                            },
                        },
                    ],
                }
            ],
            max_tokens=50,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"분석 중 오류가 발생했습니다: {e}"

# --- Streamlit UI ---
st.title("🤖 AI 음식 이름 판독기")
st.write("음식 사진을 올려주시면 AI가 어떤 음식인지 알려드립니다!")

uploaded_file = st.file_uploader("이미지 파일을 선택하세요.", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 이미지")

if st.button("음식 이름 분석하기"):
    if uploaded_file is None:
        st.error("먼저 이미지를 업로드해주세요.")
    else:
        with st.spinner("AI가 이미지를 분석하고 있습니다..."):
            resized_bytes = preprocess_image(image)
            food_names_text = analyze_image(resized_bytes)

            food_list = [item.strip() for item in food_names_text.split(",") if item.strip()]
            st.session_state.analyzed_foods = food_list

# --- AI 분석 결과 표시 및 수정/삭제/등록 ---
if "analyzed_foods" in st.session_state and st.session_state.analyzed_foods:
    st.write("---")
    st.markdown(f"##### AI 분석 결과")    
    for food in st.session_state.analyzed_foods:
        cols = st.columns([4, 2, 2, 3, 2, 2, 2])  # 이름, 수정, 삭제, 입력창, 아침, 점심, 저녁

        if st.session_state.get("edit_food") == food:
            with cols[0]:
                st.markdown(f"**{food}**")
            new_name = cols[1].text_input("새 이름", value=food, key=f"ai_edit_input_{food}")
            if cols[1].button("저장", key=f"ai_save_btn_{food}"):
                idx = st.session_state.analyzed_foods.index(food)
                st.session_state.analyzed_foods[idx] = new_name
                st.session_state.edit_food = None
                st.experimental_rerun()
            cols[1].write("")
            cols[2].write("")
        else:
            with cols[0]:
                st.markdown(f"**🍽️ {food}**")
            if cols[1].button("수정", key=f"ai_edit_btn_{food}"):
                st.session_state.edit_food = food
            if cols[2].button("삭제", key=f"ai_del_btn_{food}"):
                st.session_state.analyzed_foods.remove(food)
                if st.session_state.get("edit_food") == food:
                    st.session_state.edit_food = None
                st.experimental_rerun()
            cols[3].write("")

            for i, meal in enumerate(["아침", "점심", "저녁"]):
                if cols[4 + i].button(f"{meal}", key=f"ai_{food}_{meal}"):
                    try:
                        response = requests.post(SERVER_URL, json={"food_name": food, "meal_type": meal})
                        if response.status_code == 200:
                            st.success(f"'{food}'을(를) {meal}에 등록했습니다.")
                        elif response.status_code == 400:
                            detail = response.json().get("detail", "등록 실패")
                            st.warning(f"{detail}")  # <-- 이미 등록된 음식입니다 같은 메시지 출력
                        else:
                            st.error(f"서버 오류: {response.status_code} - {response.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"서버 요청 실패: {e}")

# --- 수동 음식 추가 ---
if "analyzed_foods" in st.session_state and st.session_state.analyzed_foods:
    # st.write("---")
    st.write("")
    st.write("")
    st.markdown(f"##### 📌 사진 속 음식이 없나요? 직접 추가하세요!")

    if "manual_foods" not in st.session_state:
        st.session_state.manual_foods = []

    def add_manual_food():
        new_food = st.session_state.manual_food_input.strip()
        if new_food and new_food not in st.session_state.manual_foods:
            st.session_state.manual_foods.append(new_food)
        st.session_state.manual_food_input = ""

    st.text_input("음식 이름을 입력하세요.", key="manual_food_input", on_change=add_manual_food)

    if st.session_state.manual_foods:
      
        for food in st.session_state.manual_foods:
            cols = st.columns([4, 2, 2, 3, 2, 2, 2])

            if st.session_state.get("manual_edit_food") == food:
                with cols[0]:
                    st.markdown(f"**{food}**")
                new_name = cols[1].text_input("새 이름", value=food, key=f"manual_edit_input_{food}")
                if cols[1].button("저장", key=f"manual_save_btn_{food}"):
                    idx = st.session_state.manual_foods.index(food)
                    st.session_state.manual_foods[idx] = new_name
                    st.session_state.manual_edit_food = None
                    st.experimental_rerun()
                cols[1].write("")
                cols[2].write("")
            else:
                with cols[0]:
                    st.markdown(f"**🍽️ {food}**")
                if cols[1].button("수정", key=f"manual_edit_btn_{food}"):
                    st.session_state.manual_edit_food = food
                if cols[2].button("삭제", key=f"manual_del_btn_{food}"):
                    st.session_state.manual_foods.remove(food)
                    if st.session_state.get("manual_edit_food") == food:
                        st.session_state.manual_edit_food = None
                    st.experimental_rerun()
                cols[3].write("")

                for i, meal in enumerate(["아침", "점심", "저녁"]):
                    if cols[4 + i].button(f"{meal}", key=f"manual_{food}_{meal}"):
                        try:
                            response = requests.post(SERVER_URL, json={"food_name": food, "meal_type": meal}, timeout=5)
                            if response.status_code == 200:
                                st.success(f"'{food}'을(를) {meal}에 등록했습니다.")
                            elif response.status_code == 400:
                                detail = response.json().get("detail", "등록 실패")
                                st.warning(f"{detail}")  # <-- 이미 등록된 음식입니다 같은 메시지 출력
                            else:
                                st.error(f"서버 오류: {response.status_code} - {response.text}")
                        except requests.exceptions.RequestException as e:
                            st.error(f"서버 요청 실패: {e}")

if "analyzed_foods" in st.session_state and st.session_state.analyzed_foods:
    st.write("---")

    if st.button("음식 영양 분석하기", key="analyze"):
        st.session_state.clear()
        st.markdown(
            """
            <meta http-equiv="refresh" content="0; url='http://13.124.198.232:8501/'" />
            """,
            unsafe_allow_html=True
        )