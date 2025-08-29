import streamlit as st

st.title("🧪 Test Streamlit App")
st.write("If you can see this, Streamlit is working!")
st.success("Connection successful! ✅")

if st.button("Click me!"):
    st.balloons()
    st.write("Button clicked! The app is responsive.")