# dreamweaver.py

import streamlit as st
from openai import OpenAI

# Initialize OpenAI client with your secret key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Streamlit UI
st.title("🌙 Dream Weaver AI")
st.write("Turn your dreams into stories and memes! AI magic, low cost!")

# User input
dream = st.text_input("💭 Describe your dream in one line:")

if st.button("✨ Weave My Dream"):
    if dream:
        try:
            # 1️⃣ Generate Story using GPT-3.5-turbo (cheaper)
            response_story = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative storyteller."},
                    {"role": "user", "content": f"Write a short story about this dream: {dream}"}
                ]
            )
            story = response_story.choices[0].message.content
            st.subheader("✨ Your Dream Story:")
            st.write(story)

            # 2️⃣ Generate Meme (Image) — keep same DALL·E
            response_image = client.images.generate(
                model="dall-e-3",
                prompt=f"Create a fun, colorful meme image for this dream: {dream}",
                n=1,
                size="512x512"
            )
            image_url = response_image.data[0].url
            st.subheader("🖼️ Your Dream Meme:")
            st.image(image_url, caption="AI-generated Meme")

        except Exception as e:
            st.error(f"Oops! Something went wrong: {e}")

    else:
        st.warning("Please enter a dream first!")
