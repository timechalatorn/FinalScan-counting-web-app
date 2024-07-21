import streamlit as st
import requests
import json
import base64
from PIL import Image
from io import BytesIO
import os

st.set_page_config(page_title="FinalScan Counting Object", page_icon=":smiley:")

API_URL = "http://127.0.0.1:8000"  # Adjust if your FastAPI server runs on a different address/port

def main():
    st.title("FinalScan Counting Object")
    sample_image_path = "C:/Users/66915/Desktop/Baksters/Finalscan-api/counting-dimension-api/sample_image.jpg"  # Adjust this path accordingly

    if os.path.exists(sample_image_path):
        sample_image = Image.open(sample_image_path)

        buf = BytesIO()
        sample_image.save(buf, format="JPEG")
        byte_im = buf.getvalue()

        sample_image_name = "sample_image.jpg"
        st.download_button(label="Download Sample Image", data=byte_im, file_name=sample_image_name, key="download_button")
    else:
        st.error(f"Sample image not found at {sample_image_path}")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image_placeholder = st.empty()
        recognizing_message = st.empty()

        image_placeholder.image(uploaded_file, caption="Uploaded Image.", use_column_width=True)
        recognizing_message.write("Recognizing...")

        # Call the FastAPI detection endpoint
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(f"{API_URL}/detection/detect/", files=files)

        if response.status_code == 200:
            detection_data = response.json()
            detection_id = detection_data["detection_id"]
            detected_classes = detection_data["detected_classes"]

            # Face Detection Results Section
            recognizing_message.empty()
            st.header("Object Detection Results:")
            # st.write(f"Total Faces Detected: {len(detected_classes)}")
            st.write(f"Detected Classes: {', '.join(detected_classes)}")

            # Annotate the image with the detected faces
            class_names = ",".join(detected_classes)
            annotate_response = requests.post(f"{API_URL}/detection/annotate/", data={"detection_id": detection_id, "classes": class_names})

            if annotate_response.status_code == 200:
                annotate_data = annotate_response.json()
                annotated_image_base64 = annotate_data["image"]
                class_counts = annotate_data["class_counts"]

                # Display the annotated image
                annotated_image = Image.open(BytesIO(base64.b64decode(annotated_image_base64)))
                st.image(annotated_image, caption="Annotated Image", use_column_width=True)

                # Display the class counts
                st.header("Object Counting Results:")
                for cls, count in class_counts.items():
                    st.write(f"{cls}: {count}")
            else:
                st.error("Failed to annotate the image.")
        else:
            st.error("Failed to detect faces in the image.")

if __name__ == "__main__":
    main()
