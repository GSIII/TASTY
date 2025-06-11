import streamlit as st
import openai
from PIL import Image
import base64
import os
import io

# --- OpenAI API 키 설정 ---
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("OpenAI API 키를 찾을 수 없습니다. 환경 변수에 OPENAI_API_KEY를 설정해주세요.")


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
                    "content": "너는 이미지를 보고 음식 이름만 정확히 답변하는 전문가야. 절대 다른 설명이나 인사는 하지 마."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "이 음식 뭐야?"},
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
    st.image(image, caption="업로드된 이미지", use_container_width=True)

    if st.button("음식 이름 분석하기"):
        with st.spinner("AI가 이미지를 분석하고 있습니다... 잠시만 기다려주세요."):

            resized_bytes = preprocess_image(image)

            food_name = analyze_image(resized_bytes)

            st.write(f"### AI 분석 결과: **{food_name}**")
