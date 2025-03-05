import streamlit as st
import requests
import json
import random
import base64
from gtts import gTTS
import os

# ---- Function to Load Image and Convert to Base64 ----
def get_base64_of_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Load images and convert to Base64
bg_image_base64 = get_base64_of_image("image.png")  # Background image
char_image_base64 = get_base64_of_image("character.png")  # Character image

# ---- Custom CSS for Background Image and Styling ----
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{bg_image_base64}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    # filter: blur(2px);  /* Slight blur for background */
}}
[data-testid="stSidebar"] {{
    background-color: rgba(0, 0, 0, 0.6);
}}
h1, h2, h3, h4, h5, h6 {{
    color: #ffffff !important;
}}
.stButton > button {{
    background-color: #ff4b4b;
    color: white;
    border-radius: 10px;
    font-size: 20px;
    padding: 10px;
}}
.stHeader {{
    background-color: rgba(0, 0, 0, 0.8);
    padding: 10px;
    color: white;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
}}
.subtitle {{
    font-size: 18px;
    color: #ffffff;
    text-align: left;
    margin-top: 10px;
    background-color: rgba(0, 0, 0, 0.7);
    padding: 10px;
    border-radius: 5px;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# ---- Header ----
st.markdown('<div class="stHeader">Apache Solr Data Indexing & Metadata Extraction Tool</div>', unsafe_allow_html=True)

# ---- Sidebar Content Based on Page ----
if "page" not in st.session_state:
    st.session_state.page = "home"

# Conditionally render sidebar content
if st.session_state.page == "home":
    st.sidebar.image(f"data:image/png;base64,{char_image_base64}", caption="Your Guide", width=100, output_format="PNG")
    st.sidebar.header("🔗 Important Links")
    st.sidebar.markdown("""
    - [Apache Solr Official Site](https://solr.apache.org/)
    - [Solr Documentation](https://solr.apache.org/guide/)
    - [Solr Tutorial](https://solr.apache.org/guide/solr/latest/getting-started/solr-tutorial.html)
    - [Streamlit Docs](https://docs.streamlit.io/)
    - [JSON Formatting Guide](https://www.json.org/json-en.html)
    """)

# ---- Text-to-Speech Function ----
def generate_audio(text, filename="welcome.mp3"):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    return filename

# ---- Home Page with Updated Info, Voice, and Subtitles ----
if st.session_state.page == "home":
    st.title("🚀 Apache Solr Data Indexing & Metadata Extraction")
    st.subheader("🔍 A Tool for Efficient Data Management")

    # Updated welcome message with purpose and goal
    welcome_text = """
    Hello! I’m your guide. This is the Apache Solr Data Indexing and Metadata Extraction Tool, 
    designed to simplify how you interact with Apache Solr. 
    It connects to your Solr core, extracts metadata, fetches sample documents, 
    and indexes new JSON data effortlessly. 
    Why was it created? To save time and reduce complexity for developers and data analysts 
    managing large datasets. 
    The goal? To provide a user-friendly interface for structuring, searching, 
    and organizing data with Solr, making data management faster and more efficient.
    Click 'Start' to dive in!
    """

    # Generate audio file if not already present and play automatically
    audio_file = "welcome.mp3"
    if not os.path.exists(audio_file):
        generate_audio(welcome_text, audio_file)

    # Display audio (autoplay enabled) and subtitles
    st.audio(audio_file, format="audio/mp3", start_time=0)  # Autoplay enabled by default
    st.markdown(f'<div class="subtitle">{welcome_text}</div>', unsafe_allow_html=True)

    st.write("""
    **What Does This Application Do?**  
    This tool streamlines interaction with Apache Solr by providing features like metadata extraction, 
    document sampling, and JSON data indexing, all in one place.

    **Why Was It Created?**  
    Managing Solr data manually can be time-consuming and error-prone. This app automates key tasks 
    to enhance productivity for developers and analysts.

    **Goal:**  
    To empower users with a simple, efficient way to manage and search data in Solr, 
    improving workflows and data accessibility.
    """)

    if st.button("▶ Start"):
        st.session_state.page = "main"
        st.rerun()

# ---- Main Page ----
elif st.session_state.page == "main":
    st.title("📌 Apache Solr Metadata & Document Extraction")
    st.sidebar.header("🔹 Solr Configuration")

    # User Inputs
    hostname = st.sidebar.text_input("🔹 Solr Hostname", "http://localhost")
    port = st.sidebar.text_input("🔹 Solr Port", "8983")
    core_name = st.sidebar.text_input("🔹 Core Name", "mycore")
    username = st.sidebar.text_input("👤 Username (if applicable)", "")
    password = st.sidebar.text_input("🔑 Password (if applicable)", "", type="password")

    base_url = f"{hostname}:{port}/solr/{core_name}"

    # Fetch Metadata
    if st.sidebar.button("Fetch Metadata"):
        try:
            solr_status_url = f"{hostname}:{port}/solr/admin/info/system?wt=json"
            auth = (username, password) if username and password else None
            response = requests.get(solr_status_url, auth=auth, timeout=5)
            response.raise_for_status()

            core_status_url = f"{hostname}:{port}/solr/admin/cores?action=STATUS&core={core_name}&wt=json"
            core_status = requests.get(core_status_url, auth=auth, timeout=5).json()

            if core_name not in core_status["status"]:
                st.error(f"❌ Error: Core '{core_name}' does not exist in Solr.")
            else:
                index_size = core_status["status"][core_name]["index"]["sizeInBytes"]
                num_docs = core_status["status"][core_name]["index"]["numDocs"]

                query_url = f"{base_url}/select?q=*:*&wt=json&rows=10"
                response = requests.get(query_url, auth=auth, timeout=5).json()
                docs = response["response"]["docs"]

                sample_docs = random.sample(docs, min(2, len(docs)))

                filtered_docs = [
                    {key: doc[key] for key in doc if not key.startswith("_")}
                    for doc in sample_docs
                ]

                st.subheader("📊 Core Metadata")
                st.json({
                    "Core Name": core_name,
                    "Index Size (Bytes)": index_size,
                    "Number of Documents": num_docs,
                    "Sample Documents": filtered_docs
                })

                metadata_output = {
                    "core_name": core_name,
                    "index_size_bytes": index_size,
                    "num_documents": num_docs,
                    "sample_documents": filtered_docs
                }
                with open("solr_metadata.json", "w") as json_file:
                    json.dump(metadata_output, json_file, indent=4)

                st.success("✅ Metadata saved to solr_metadata.json!")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error connecting to Solr. Please check the details and try again.\nDetails: {e}")

    # ---- Upload & Index Normal JSON Data ----
    st.sidebar.subheader("📤 Upload Standard JSON Data")
    normal_file = st.sidebar.file_uploader("📂 Choose a JSON file", type=["json"], key="normal_json")

    if normal_file is not None:
        file_content = normal_file.read()
        
        try:
            json_data = json.loads(file_content)

            if st.sidebar.button("📥 Index Standard Data"):
                index_url = f"{base_url}/update?commit=true"
                headers = {"Content-Type": "application/json"}
                auth = (username, password) if username and password else None
                response = requests.post(index_url, headers=headers, json=json_data, auth=auth, timeout=5)
                
                if response.status_code == 200:
                    st.success("✅ Standard JSON data successfully indexed!")
                else:
                    st.error(f"❌ Failed to index data: {response.text}")

        except json.JSONDecodeError:
            st.error("❌ Invalid JSON file!")

    # ---- Upload & Index Complex JSON Data ----
    st.sidebar.subheader("📤 Upload Complex JSON Data")
    complex_file = st.sidebar.file_uploader("📂 Choose a Complex JSON file", type=["json"], key="complex_json")

    if complex_file is not None:
        file_content = complex_file.read()

        try:
            raw_json = json.loads(file_content)

            # ---- Function to Fix Complex JSON ----
            def transform_json_for_solr(raw_data):
                documents = []
                for index_entry in raw_data.get("data", {}).get("Index", []):
                    for doc in index_entry.get("Documents", []):
                        processed_doc = {"id": doc["document_id"]}  # Set unique Solr ID
                        
                        for field in doc.get("fieldTypes", []):
                            field_name = field["fieldName"]
                            field_value = field["value"]
                            
                            if isinstance(field_value, list) and isinstance(field_value[0], dict):
                                field_value = [json.dumps(item) for item in field_value]  
                            elif isinstance(field_value, dict):
                                field_value = json.dumps(field_value)  

                            if field_name not in ["sensitive_data"]:
                                processed_doc[field_name] = field_value
                        
                        documents.append(processed_doc)
                return documents

            fixed_json = transform_json_for_solr(raw_json)

            if st.sidebar.button("⚙ Fix & Index Complex Data"):
                index_url = f"{base_url}/update?commit=true"
                headers = {"Content-Type": "application/json"}
                auth = (username, password) if username and password else None
                response = requests.post(index_url, headers=headers, json=fixed_json, auth=auth, timeout=5)
                
                if response.status_code == 200:
                    st.success("✅ Complex JSON data successfully fixed & indexed!")
                else:
                    st.error(f"❌ Failed to index complex data: {response.text}")

        except json.JSONDecodeError:
            st.error("❌ Invalid JSON file!")