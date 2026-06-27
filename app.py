import streamlit as st
from PIL import Image
from io import BytesIO
import zipfile
import tempfile
import subprocess
import os
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter, PdfMerger


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Image & PDF Studio",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
#st.markdown("<h1 style='text-align:center;'>🖼️ Image & PDF Studio</h1>", unsafe_allow_html=True)
st.markdown("""
<div class="main-title">
    🖼️ Image & PDF Studio 
</div>
<div class="sub-title">
    Professional Image & PDF Processing Toolkit by Aritra Paul
</div>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
menu = st.sidebar.selectbox(
    "Select Tool",
    [
        "Image Resize",
        "Image Compress",
        "Image Convert",
        "Images to PDF",
        "PDF to Images",
        "Merge PDF",
        "Split PDF",
        "Rotate PDF",
        "PDF Compress"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("Image & PDF Processing Toolkit")


# ================= IMAGE RESIZE =================
if menu == "Image Resize":

    file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"])

    if file:
        img = Image.open(file)
        st.image(img)

        w = st.number_input("Width", 1, value=img.width)
        h = st.number_input("Height", 1, value=img.height)

        if st.button("Resize"):
            img2 = img.resize((int(w), int(h)))

            buf = BytesIO()
            ext = file.name.split(".")[-1].upper()
            if ext == "JPG":
                ext = "JPEG"

            img2.save(buf, format=ext)

            st.download_button("Download", buf.getvalue(), f"resized.{ext.lower()}")


# ================= IMAGE COMPRESS =================
elif menu == "Image Compress":

    file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if file:
        img = Image.open(file)
        q = st.slider("Quality", 10, 100, 70)

        if st.button("Compress"):
            buf = BytesIO()
            img.convert("RGB").save(buf, "JPEG", quality=q)

            st.download_button("Download", buf.getvalue(), "compressed.jpg")


# ================= IMAGE CONVERT =================
elif menu == "Image Convert":

    file = st.file_uploader("Upload Image")

    if file:
        img = Image.open(file)
        fmt = st.selectbox("Format", ["PNG", "JPEG", "WEBP"])

        if st.button("Convert"):
            buf = BytesIO()

            if fmt == "JPEG":
                img = img.convert("RGB")

            img.save(buf, fmt)

            st.download_button("Download", buf.getvalue(), f"output.{fmt.lower()}")


# ================= IMAGES TO PDF =================
elif menu == "Images to PDF":

    files = st.file_uploader("Upload Images", accept_multiple_files=True)

    if files and st.button("Create PDF"):

        images = [Image.open(f).convert("RGB") for f in files]

        pdf = BytesIO()
        images[0].save(pdf, save_all=True, append_images=images[1:], format="PDF")

        st.download_button("Download PDF", pdf.getvalue(), "images.pdf")


# ================= PDF TO IMAGES =================
elif menu == "PDF to Images":

    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file:

        pdf = fitz.open(stream=file.read(), filetype="pdf")

        total_pages = pdf.page_count
        st.write(f"Total Pages: {total_pages}")

        pages = st.multiselect("Select Pages", list(range(1, total_pages + 1)))

        fmt = st.selectbox("Image Format", ["PNG", "JPEG", "WEBP"])
        zoom = st.slider("Zoom", 1, 3, 2)

        if pages:

            if st.button("Convert"):

                for p in pages:

                    page = pdf[p - 1]
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)

                    img_bytes = pix.tobytes(fmt.lower())

                    st.download_button(
                        f"Download Page {p}",
                        img_bytes,
                        file_name=f"page_{p}.{fmt.lower()}",
                        mime=f"image/{fmt.lower()}"
                    )

# ================= MERGE PDF =================
elif menu == "Merge PDF":

    files = st.file_uploader("Upload PDFs", accept_multiple_files=True)

    if files and st.button("Merge"):

        merger = PdfMerger()

        for f in files:
            merger.append(f)

        out = BytesIO()
        merger.write(out)

        st.download_button("Download", out.getvalue(), "merged.pdf")


# ================= SPLIT PDF =================
elif menu == "Split PDF":

    file = st.file_uploader("Upload PDF")

    if file:
        reader = PdfReader(file)

        if st.button("Split"):

            zip_buffer = BytesIO()

            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for i, page in enumerate(reader.pages):

                    writer = PdfWriter()
                    writer.add_page(page)

                    buf = BytesIO()
                    writer.write(buf)

                    zf.writestr(f"page_{i+1}.pdf", buf.getvalue())

            st.download_button("Download ZIP", zip_buffer.getvalue(), "pages.zip")


# ================= ROTATE PDF =================
elif menu == "Rotate PDF":

    file = st.file_uploader("Upload PDF")

    if file:

        angle = st.selectbox("Angle", [90, 180, 270])

        if st.button("Rotate"):

            reader = PdfReader(file)
            writer = PdfWriter()

            for page in reader.pages:
                page.rotate(angle)
                writer.add_page(page)

            out = BytesIO()
            writer.write(out)

            st.download_button("Download", out.getvalue(), "rotated.pdf")


# ================= PDF COMPRESS =================
elif menu == "PDF Compress":

    file = st.file_uploader("Upload PDF")

    if file:

        st.info(f"Size: {len(file.getvalue())/1024/1024:.2f} MB")

        if st.button("Compress"):
            st.warning("Ghostscript required on server")
