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
    """이미지를 리사이즈하고 압축한 후 바이트로 반환"""
    image.thumbnail(max_size)  # 비율 유지한 리사이즈
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    return buffer.read()


def analyze_image(image_bytes):
    """이미지 바이트를 받아 AI로 분석하고 음식 이름을 반환하는 함수"""
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
            max_tokens=10,
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


# AI 분석 결과 음식들 표시 + 수정 버튼
if "analyzed_foods" in st.session_state and st.session_state.analyzed_foods:
    st.subheader("AI 분석 결과")
    for food in st.session_state.analyzed_foods:
        cols = st.columns([4, 1])
        with cols[0]:
            st.markdown(f"**{food}**")
        with cols[1]:
            if st.button("수정", key=f"edit_btn_{food}"):
                st.session_state.edit_food = food

        # 수정 모드일 경우 텍스트 입력창 띄우기
        if st.session_state.get("edit_food") == food:
            new_name = st.text_input("음식 이름 수정", value=food, key=f"edit_input_{food}")
            if st.button("저장", key=f"save_btn_{food}"):
                # 수정한 이름으로 교체
                idx = st.session_state.analyzed_foods.index(food)
                st.session_state.analyzed_foods[idx] = new_name
                st.session_state.edit_food = None
                st.experimental_rerun()

        # 등록 버튼 (수정 중 아닐 때만)
        if st.session_state.get("edit_food") != food:
            cols2 = st.columns(4)
            for i, meal in enumerate(["아침", "점심", "저녁", "간식"]):
                if cols2[i].button(f"{meal} 등록", key=f"{food}_{meal}"):
                    try:
                        response = requests.post(SERVER_URL, json={"food_name": food, "meal_type": meal})
                        if response.status_code == 200:
                            st.success(f"'{food}'을(를) {meal}에 등록했습니다.")
                        else:
                            st.error(f"서버 오류: {response.status_code} - {response.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"서버 요청 실패: {e}")


if "analyzed_foods" in st.session_state and st.session_state.analyzed_foods:

    st.write("---")
    st.write("📌 사진 속 음식이 없나요? 직접 추가하세요!")

    if "manual_foods" not in st.session_state:
        st.session_state.manual_foods = []

    def add_manual_food():
        new_food = st.session_state.manual_food_input.strip()
        if new_food and new_food not in st.session_state.manual_foods:
            st.session_state.manual_foods.append(new_food)
        st.session_state.manual_food_input = "" 

    st.text_input("음식 이름을 입력하세요.", key="manual_food_input", on_change=add_manual_food)

    if st.session_state.manual_foods:
        st.markdown("### 직접 추가한 음식 목록")
        for food in st.session_state.manual_foods:
            st.markdown(f" **{food}**")
            cols3 = st.columns(4)
            for i, meal in enumerate(["아침", "점심", "저녁", "간식"]):
                if cols3[i].button(f"{meal} 등록", key=f"manual_{food}_{meal}"):
                    try:
                        response = requests.post(SERVER_URL, json={"food_name": food, "meal_type": meal}, timeout=5)
                        if response.status_code == 200:
                            st.success(f"'{food}'을(를) {meal}에 등록했습니다.")
                        else:
                            st.error(f"서버 오류: {response.status_code} - {response.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"서버 요청 실패: {e}")