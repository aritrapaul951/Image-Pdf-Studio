import streamlit as st
from PIL import Image
from io import BytesIO
import zipfile
import tempfile
import subprocess
import os
import fitz
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Image & PDF Studio by Aritra Paul",
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
st.markdown("<h1 style='text-align:center;'>🖼️ Image & PDF Studio</h1>", unsafe_allow_html=True)

# ================= SIDEBAR =================
menu = st.sidebar.selectbox(
    "📂 Select Tool",
    [
        "🖼️ Image Resize",
        "🗜️ Image Compress",
        "🔄 Image Convert",
        "📄 Images to PDF",
        "🖼️ PDF to Images",
        "📑 Merge PDF",
        "✂️ Split PDF",
        "🔃 Rotate PDF",
        "📉 PDF Compress"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("""
Available Tools:
Image Resize
Image Compress
Image Convert
Images to PDF
PDF to Images
Merge PDF
Split PDF
Rotate PDF
PDF Compress
""")

# ================= IMAGE RESIZE =================
if menu == "🖼️ Image Resize":
    file = st.file_uploader("Upload Image", type=["png","jpg","jpeg","webp"])

    if file:
        img = Image.open(file)
        st.image(img)

        w = st.number_input("Width", 1, value=img.width)
        h = st.number_input("Height", 1, value=img.height)

        if st.button("Resize"):
            img2 = img.resize((int(w), int(h)))
            buf = BytesIO()
            img2.save(buf, format="PNG")

            st.download_button("Download", buf.getvalue(), "resized.png")

# ================= IMAGE COMPRESS =================
elif menu == "🗜️ Image Compress":
    file = st.file_uploader("Upload Image", type=["jpg","jpeg","png"])

    if file:
        img = Image.open(file)
        q = st.slider("Quality", 10, 100, 70)

        if st.button("Compress"):
            buf = BytesIO()
            img.convert("RGB").save(buf, "JPEG", quality=q)
            st.download_button("Download", buf.getvalue(), "compressed.jpg")

# ================= IMAGE CONVERT =================
elif menu == "🔄 Image Convert":
    file = st.file_uploader("Upload Image", type=["png","jpg","jpeg","webp"])

    if file:
        img = Image.open(file)
        fmt = st.selectbox("Format", ["PNG","JPEG","WEBP"])

        if st.button("Convert"):
            buf = BytesIO()
            img.convert("RGB").save(buf, fmt)
            st.download_button("Download", buf.getvalue(), f"output.{fmt.lower()}")

# ================= IMAGES TO PDF =================
elif menu == "📄 Images to PDF":
    files = st.file_uploader("Upload Images", type=["png","jpg","jpeg"], accept_multiple_files=True)

    if files and st.button("Create PDF"):
        images = [Image.open(f).convert("RGB") for f in files]

        pdf = BytesIO()
        images[0].save(pdf, save_all=True, append_images=images[1:], format="PDF")

        st.download_button("Download PDF", pdf.getvalue(), "images.pdf")

# ================= PDF TO IMAGES =================
elif menu == "🖼️ PDF to Images":
    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file:
        pdf = fitz.open(stream=file.read(), filetype="pdf")

        pages = st.multiselect("Pages", list(range(1, pdf.page_count + 1)))
        fmt = st.selectbox("Format", ["png","jpeg","webp"])
        zoom = st.slider("Zoom", 1, 3, 2)

        if pages and st.button("Convert"):
            zip_buffer = BytesIO()

            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for p in pages:
                    page = pdf[p-1]
                    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))

                    zf.writestr(
                        f"page_{p}.{fmt}",
                        pix.tobytes(fmt)
                    )

            st.download_button("Download ZIP", zip_buffer.getvalue(), "images.zip")

# ================= MERGE PDF =================
elif menu == "📑 Merge PDF":
    files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

    if files and st.button("Merge"):
        merger = PdfMerger()

        for f in files:
            merger.append(f)

        out = BytesIO()
        merger.write(out)
        st.download_button("Download", out.getvalue(), "merged.pdf")

# ================= SPLIT PDF =================
elif menu == "✂️ Split PDF":
    file = st.file_uploader("Upload PDF", type=["pdf"])

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
elif menu == "🔃 Rotate PDF":
    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file:
        angle = st.selectbox("Angle", [90,180,270])

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
elif menu == "📉 PDF Compress":
    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file:
        st.info(f"Size: {len(file.getvalue())/1024/1024:.2f} MB")
        st.warning("Ghostscript required for compression")
