import streamlit as st
from PIL import Image
from io import BytesIO
import zipfile
import fitz
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

# ================= CONFIG =================
st.set_page_config(
    page_title="Image & PDF Studio",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= CSS =================
st.markdown("""
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR (FORCE ALWAYS LOAD) =================
with st.sidebar:
    st.title("🖼️ Image & PDF Studio")

    menu = st.radio(
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

# ================= ROUTER =================
def image_resize():
    file = st.file_uploader("Upload Image")
    if file:
        img = Image.open(file)
        w = st.number_input("Width", value=img.width)
        h = st.number_input("Height", value=img.height)

        if st.button("Resize"):
            buf = BytesIO()
            img.resize((int(w), int(h))).save(buf, "PNG")
            st.download_button("Download", buf.getvalue(), "resized.png")

def image_compress():
    file = st.file_uploader("Upload Image")
    if file:
        q = st.slider("Quality", 10, 100, 70)

        if st.button("Compress"):
            buf = BytesIO()
            Image.open(file).convert("RGB").save(buf, "JPEG", quality=q)
            st.download_button("Download", buf.getvalue(), "compressed.jpg")

def image_convert():
    file = st.file_uploader("Upload Image")
    if file:
        fmt = st.selectbox("Format", ["PNG","JPEG","WEBP"])

        if st.button("Convert"):
            buf = BytesIO()
            img = Image.open(file)
            img.convert("RGB").save(buf, fmt)
            st.download_button("Download", buf.getvalue(), f"out.{fmt.lower()}")

def images_to_pdf():
    files = st.file_uploader("Upload Images", accept_multiple_files=True)
    if files and st.button("Create PDF"):
        imgs = [Image.open(f).convert("RGB") for f in files]
        buf = BytesIO()
        imgs[0].save(buf, save_all=True, append_images=imgs[1:], format="PDF")
        st.download_button("Download", buf.getvalue(), "images.pdf")

def pdf_to_images():
    file = st.file_uploader("Upload PDF")
    if file:
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        pages = st.multiselect("Pages", list(range(1, pdf.page_count+1)))

        if pages and st.button("Convert"):
            zip_buf = BytesIO()
            with zipfile.ZipFile(zip_buf, "w") as zf:
                for p in pages:
                    pix = pdf[p-1].get_pixmap()
                    zf.writestr(f"page_{p}.png", pix.tobytes("png"))

            st.download_button("Download ZIP", zip_buf.getvalue(), "pages.zip")

def merge_pdf():
    files = st.file_uploader("Upload PDFs", accept_multiple_files=True)
    if files and st.button("Merge"):
        merger = PdfMerger()
        for f in files:
            merger.append(f)
        out = BytesIO()
        merger.write(out)
        st.download_button("Download", out.getvalue(), "merged.pdf")

def split_pdf():
    file = st.file_uploader("Upload PDF")
    if file and st.button("Split"):
        reader = PdfReader(file)
        zip_buf = BytesIO()

        with zipfile.ZipFile(zip_buf, "w") as zf:
            for i, p in enumerate(reader.pages):
                w = PdfWriter()
                w.add_page(p)
                b = BytesIO()
                w.write(b)
                zf.writestr(f"page_{i+1}.pdf", b.getvalue())

        st.download_button("Download", zip_buf.getvalue(), "split.zip")

def rotate_pdf():
    file = st.file_uploader("Upload PDF")
    if file:
        angle = st.selectbox("Angle", [90,180,270])

        if st.button("Rotate"):
            r = PdfReader(file)
            w = PdfWriter()

            for p in r.pages:
                p.rotate(angle)
                w.add_page(p)

            out = BytesIO()
            w.write(out)
            st.download_button("Download", out.getvalue(), "rotated.pdf")

def pdf_compress():
    file = st.file_uploader("Upload PDF")
    if file:
        st.info(f"Size: {len(file.getvalue())/1024/1024:.2f} MB")
        st.warning("Ghostscript required")

# ================= MAIN ROUTER =================
if menu == "Image Resize":
    image_resize()
elif menu == "Image Compress":
    image_compress()
elif menu == "Image Convert":
    image_convert()
elif menu == "Images to PDF":
    images_to_pdf()
elif menu == "PDF to Images":
    pdf_to_images()
elif menu == "Merge PDF":
    merge_pdf()
elif menu == "Split PDF":
    split_pdf()
elif menu == "Rotate PDF":
    rotate_pdf()
elif menu == "PDF Compress":
    pdf_compress()
