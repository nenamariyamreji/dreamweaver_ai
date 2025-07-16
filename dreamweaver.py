# dream_weaver.py

import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# ---- Streamlit Page Settings ----
st.set_page_config(page_title="Dream Weaver AI", page_icon="🌙")
st.title("🌙 Dream Weaver AI")
st.write("Turn your dreams into short stories and memes with AI magic!")

# ---- User Input ----
dream = st.text_input("💭 *Describe your dream in one line:*", placeholder="Example: I was surfing on a giant pizza.")

if st.button("✨ Weave My Dream"):
    if dream:
        with st.spinner("Weaving your dream... please wait..."):

            # ---- Generate Story ----
            response_story = client.chat.completions.create(
                model="gpt-4o",  # or "gpt-4-turbo"
                messages=[
                    {"role": "system", "content": "You are a creative storyteller."},
                    {"role": "user", "content": f"Write a short, fun, imaginative story about this dream: {dream}"}
                ]
            )
            story = response_story.choices[0].message.content

            st.subheader("📖 *Your Dream Story:*")
            st.write(story)

            # ---- Generate Meme Image ----
            response_image = client.images.generate(
                model="dall-e-3",
                prompt=f"A colorful, fun meme image about this dream: {dream}",
                n=1,
                size="512x512"
            )
            image_url = response_image.data[0].url

            st.subheader("🖼️ *Your Dream Meme:*")
            st.image(image_url, caption="AI-generated Meme")

            st.success("Dream woven successfully! 💫")
    else:
        st.warning("Please type your dream first!")
