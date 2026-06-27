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
    page_title="Image & PDF Studio",
    page_icon="🖼️",
    layout="wide"
)

# ================= SESSION INIT =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""


# ================= LOGIN PAGE =================
def login_page():

    st.title("🔐 Login System")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):

        if username.strip() == "admin" and password.strip() == "1234":

            st.session_state.logged_in = True
            st.session_state.user = username

            st.success("Login successful")
            st.rerun()

        else:
            st.error("Invalid username or password")


# ================= LOGOUT =================
def logout():
    st.session_state.logged_in = False
    st.session_state.user = ""
    st.rerun()


# ================= AUTH GATE =================
if not st.session_state.logged_in:
    login_page()
    st.stop()


# ================= AFTER LOGIN =================
st.sidebar.success(f"Logged in as {st.session_state.user}")

if st.sidebar.button("Logout"):
    logout()


# ================= MENU =================
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

            st.download_button(
                "Download",
                buf.getvalue(),
                f"resized.{ext.lower()}"
            )

# ================= IMAGE COMPRESS =================
elif menu == "Image Compress":

    file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if file:
        img = Image.open(file)
        quality = st.slider("Quality", 10, 100, 70)

        if st.button("Compress"):
            buf = BytesIO()
            img = img.convert("RGB")

            img.save(buf, format="JPEG", quality=quality, optimize=True)

            st.download_button(
                "Download",
                buf.getvalue(),
                "compressed.jpg",
                mime="image/jpeg"
            )

# ================= IMAGE CONVERT =================
elif menu == "Image Convert":

    file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"])

    if file:
        img = Image.open(file)
        fmt = st.selectbox("Output Format", ["PNG", "JPEG", "WEBP"])

        if st.button("Convert"):
            buf = BytesIO()

            if fmt == "JPEG":
                img = img.convert("RGB")

            img.save(buf, format=fmt)

            st.download_button(
                "Download",
                buf.getvalue(),
                f"converted.{fmt.lower()}"
            )

# ================= IMAGES TO PDF =================
elif menu == "Images to PDF":

    files = st.file_uploader(
        "Upload Images",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if files and st.button("Create PDF"):

        images = [Image.open(f).convert("RGB") for f in files]

        pdf = BytesIO()
        images[0].save(pdf, save_all=True, append_images=images[1:], format="PDF")

        st.download_button(
            "Download PDF",
            pdf.getvalue(),
            "images.pdf",
            mime="application/pdf"
        )

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

    files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

    if files and st.button("Merge"):

        merger = PdfMerger()

        for f in files:
            merger.append(f)

        out = BytesIO()
        merger.write(out)
        merger.close()

        st.download_button("Download", out.getvalue(), "merged.pdf")

# ================= SPLIT PDF =================
elif menu == "Split PDF":

    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file:

        reader = PdfReader(file)

        if st.button("Split"):

            zip_buffer = BytesIO()

            with zipfile.ZipFile(zip_buffer, "w") as zf:

                for i, page in enumerate(reader.pages):

                    writer = PdfWriter()
                    writer.add_page(page)

                    pdf_bytes = BytesIO()
                    writer.write(pdf_bytes)

                    zf.writestr(f"page_{i+1}.pdf", pdf_bytes.getvalue())

            st.download_button(
                "Download ZIP",
                zip_buffer.getvalue(),
                "pages.zip"
            )

# ================= ROTATE PDF =================
elif menu == "Rotate PDF":

    file = st.file_uploader("Upload PDF", type=["pdf"])

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

    file = st.file_uploader("Upload PDF", type=["pdf"])

    quality_dict = {
        "High Compression": "/screen",
        "Medium Compression": "/ebook",
        "High Quality": "/printer",
        "Original": "/prepress"
    }

    quality = st.selectbox("Quality", list(quality_dict.keys()))
    gs_quality = quality_dict[quality]

    if file:

        original_size = len(file.getvalue()) / 1024 / 1024
        st.info(f"Original Size: {original_size:.2f} MB")

        if st.button("Compress PDF"):

            with tempfile.TemporaryDirectory() as tmp:

                inp = os.path.join(tmp, "in.pdf")
                outp = os.path.join(tmp, "out.pdf")

                with open(inp, "wb") as f:
                    f.write(file.getvalue())

                cmd = [
                    "gs",
                    "-sDEVICE=pdfwrite",
                    "-dCompatibilityLevel=1.4",
                    f"-dPDFSETTINGS={gs_quality}",
                    "-dNOPAUSE",
                    "-dQUIET",
                    "-dBATCH",
                    f"-sOutputFile={outp}",
                    inp
                ]

                if os.name == "nt":
                    cmd[0] = "gswin64c"

                try:
                    subprocess.run(cmd, check=True)

                    with open(outp, "rb") as f:
                        data = f.read()

                    st.success("Compressed successfully")

                    st.download_button(
                        "Download",
                        data,
                        "compressed.pdf",
                        mime="application/pdf"
                    )

                except Exception as e:
                    st.error(f"Error: {e}")
