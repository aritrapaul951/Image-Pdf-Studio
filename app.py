import streamlit as st
from PIL import Image
from io import BytesIO
import zipfile
import fitz
from PyPDF2 import PdfReader, PdfWriter, PdfMerger


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Image & PDF Studio",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= THEME CSS =================
st.markdown("""
<style>

/* Hide default UI */
#MainMenu, footer, header {visibility: hidden;}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}

/* Sidebar glass effect */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* Main container */
.block-container {
    padding: 2rem 2rem;
}

/* Title */
.main-title {
    font-size: 44px;
    font-weight: 800;
    text-align: center;
    color: #60a5fa;
    margin-bottom: 5px;
}

.sub-title {
    text-align: center;
    color: #cbd5e1;
    font-size: 16px;
    margin-bottom: 30px;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.06);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}

/* Buttons */
.stButton>button, .stDownloadButton>button {
    width: 100%;
    border-radius: 10px;
    height: 3em;
    font-weight: 600;
    background: #3b82f6;
    color: white;
    border: none;
    transition: 0.3s;
}

.stButton>button:hover {
    background: #2563eb;
    transform: scale(1.02);
}

/* File uploader */
section[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.05);
    padding: 10px;
    border-radius: 12px;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ================= HEADER =================
st.markdown("""
<div class="main-title">🖼️ Image & PDF Studio</div>
<div class="sub-title">Professional File Processing Toolkit by Aritra Paul</div>
""", unsafe_allow_html=True)


# ================= SIDEBAR =================
menu = st.selectbox(
    "📂 Tools",
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

#st.markdown("---")
st.info("Fast • Clean • Professional File Tools")


# ================= UI WRAPPER =================
#def card():
#    st.markdown('<div class="card">', unsafe_allow_html=True)


# ================= IMAGE RESIZE =================
if menu == "Image Resize":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"])

    if file:
        img = Image.open(file)
        st.image(img, use_container_width=True)

        w = st.number_input("Width", 1, value=img.width)
        h = st.number_input("Height", 1, value=img.height)

        if st.button("Resize"):
            img2 = img.resize((int(w), int(h)))

            buf = BytesIO()
            img2.save(buf, format="PNG")

            st.image(img2, use_container_width=True)

            st.download_button("Download", buf.getvalue(), "resized.png")

    st.markdown('</div>', unsafe_allow_html=True)


# ================= IMAGE COMPRESS =================
elif menu == "Image Compress":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if file:
        img = Image.open(file)
        q = st.slider("Quality", 10, 100, 70)

        if st.button("Compress"):
            buf = BytesIO()
            img.convert("RGB").save(buf, "JPEG", quality=q)

            st.download_button("Download", buf.getvalue(), "compressed.jpg")

    st.markdown('</div>', unsafe_allow_html=True)


# ================= IMAGE CONVERT =================
elif menu == "Image Convert":

    st.markdown('<div class="card">', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)


# ================= IMAGES TO PDF =================
elif menu == "Images to PDF":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    files = st.file_uploader("Upload Images", accept_multiple_files=True)

    if files and st.button("Create PDF"):

        images = [Image.open(f).convert("RGB") for f in files]

        pdf = BytesIO()
        images[0].save(pdf, save_all=True, append_images=images[1:], format="PDF")

        st.download_button("Download PDF", pdf.getvalue(), "images.pdf")

    st.markdown('</div>', unsafe_allow_html=True)


# ================= PDF TO IMAGES =================
elif menu == "PDF to Images":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file:
        pdf = fitz.open(stream=file.read(), filetype="pdf")

        pages = st.multiselect("Select Pages", list(range(1, pdf.page_count + 1)))
        fmt = st.selectbox("Format", ["png", "jpeg", "webp"])
        zoom = st.slider("Zoom", 1, 3, 2)

        if st.button("Convert"):

            for p in pages:
                page = pdf[p - 1]
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))

                st.download_button(
                    f"Download Page {p}",
                    pix.tobytes(fmt),
                    file_name=f"page_{p}.{fmt}"
                )

    st.markdown('</div>', unsafe_allow_html=True)


# ================= MERGE PDF =================
elif menu == "Merge PDF":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    files = st.file_uploader("Upload PDFs", accept_multiple_files=True)

    if files and st.button("Merge"):

        merger = PdfMerger()
        for f in files:
            merger.append(f)

        out = BytesIO()
        merger.write(out)

        st.download_button("Download", out.getvalue(), "merged.pdf")

    st.markdown('</div>', unsafe_allow_html=True)


# ================= SPLIT PDF =================
elif menu == "Split PDF":

    st.markdown('<div class="card">', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)


# ================= ROTATE PDF =================
elif menu == "Rotate PDF":

    st.markdown('<div class="card">', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)


# ================= PDF COMPRESS =================
elif menu == "PDF Compress":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    file = st.file_uploader("Upload PDF")

    if file:
        st.info(f"Size: {len(file.getvalue())/1024/1024:.2f} MB")
        st.warning("Ghostscript required for compression")

    st.markdown('</div>', unsafe_allow_html=True)




