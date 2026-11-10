import os, shutil, subprocess, tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="MusicPDF Studio")
AUDIVERIS = os.getenv("AUDIVERIS_BIN", "audiveris")
MAX_BYTES = int(os.getenv("MAX_UPLOAD_MB", "40")) * 1024 * 1024
BASE = Path(tempfile.gettempdir()) / "musicpdf-studio"
BASE.mkdir(exist_ok=True)

@app.get("/api/health")
def health():
    return {"ok": True, "recognition_engine": shutil.which(AUDIVERIS) is not None}

@app.post("/api/convert")
async def convert(file: UploadFile = File(...), mode: str = Form("balanced")):
    name = Path(file.filename or "score").name
    ext = Path(name).suffix.lower()
    if ext not in {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
        raise HTTPException(400, "Formato no admitido.")
    if not shutil.which(AUDIVERIS):
        raise HTTPException(503, "El motor Audiveris no está instalado en el servidor.")
    job = Path(tempfile.mkdtemp(prefix="job-", dir=BASE))
    source, output = job / ("input" + ext), job / "output"
    output.mkdir()
    size = 0
    with source.open("wb") as dest:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_BYTES:
                shutil.rmtree(job, ignore_errors=True)
                raise HTTPException(413, "El archivo supera el límite permitido.")
            dest.write(chunk)
    try:
        result = subprocess.run([AUDIVERIS, "-batch", "-export", "-output", str(output), "--", str(source)], capture_output=True, text=True, timeout=900, check=False)
    except subprocess.TimeoutExpired:
        shutil.rmtree(job, ignore_errors=True)
        raise HTTPException(504, "El reconocimiento ha superado el tiempo máximo.")
    candidates = list(output.rglob("*.mxl")) + list(output.rglob("*.musicxml")) + list(output.rglob("*.xml"))
    if result.returncode != 0 or not candidates:
        detail = (result.stderr or result.stdout or "Audiveris no ha generado MusicXML.")[-1800:]
        shutil.rmtree(job, ignore_errors=True)
        raise HTTPException(422, detail)
    result_file = candidates[0]
    return FileResponse(result_file, filename=Path(name).stem + ".mxl", media_type="application/vnd.recordare.musicxml", background=None)

app.mount("/", StaticFiles(directory="static", html=True), name="static")
