import shutil
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from report_builder import process_files_and_generate_report

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate-report", response_class=HTMLResponse)
async def generate_report(
    request: Request,
    month: str = Form(...),
    email: str = Form(...),
    report_type: str = Form(...),
    notes: str = Form(""),
    files: list[UploadFile] = File(...),
):
    try:
        month_folder = UPLOAD_DIR / month.replace(" ", "_")
        if month_folder.exists():
            shutil.rmtree(month_folder)
        month_folder.mkdir(parents=True, exist_ok=True)

        saved_files = []

        for uploaded_file in files:
            file_path = month_folder / uploaded_file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(uploaded_file.file, buffer)
            saved_files.append(str(file_path))

        result = process_files_and_generate_report(
            month=month,
            email=email,
            notes=notes,
            report_type=report_type,
            file_paths=saved_files,
        )

        return HTMLResponse(
            f"""
            <html>
                <body style="font-family: Arial; padding: 40px;">
                    <h2>Report generation completed</h2>
                    <p><strong>Month:</strong> {month}</p>
                    <p><strong>Report Type:</strong> {report_type}</p>
                    <p><strong>Status:</strong> {result}</p>
                    <p>You can now check your email and the outputs folder.</p>
                    <a href="/">Go back</a>
                </body>
            </html>
            """
        )

    except Exception as e:
        return HTMLResponse(
            f"""
            <html>
                <body style="font-family: Arial; padding: 40px;">
                    <h2>Report generation failed</h2>
                    <p><strong>Error:</strong> {str(e)}</p>
                    <a href="/">Go back</a>
                </body>
            </html>
            """,
            status_code=500,
        )


@app.post("/api/generate-report")
async def api_generate_report(
    month: str = Form(...),
    email: str = Form(...),
    report_type: str = Form(...),
    notes: str = Form(""),
    files: list[UploadFile] = File(...),
):
    try:
        month_folder = UPLOAD_DIR / month.replace(" ", "_")
        if month_folder.exists():
            shutil.rmtree(month_folder)
        month_folder.mkdir(parents=True, exist_ok=True)

        saved_files = []

        for uploaded_file in files:
            file_path = month_folder / uploaded_file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(uploaded_file.file, buffer)
            saved_files.append(str(file_path))

        result = process_files_and_generate_report(
            month=month,
            email=email,
            notes=notes,
            report_type=report_type,
            file_paths=saved_files,
        )

        generated_docs = sorted(
            OUTPUT_DIR.glob("*.docx"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        latest_file = generated_docs[0].name if generated_docs else None

        return JSONResponse(
            {
                "success": True,
                "message": result,
                "download_url": f"/api/download/{latest_file}" if latest_file else None,
            }
        )

    except Exception as e:
        return JSONResponse(
            {"success": False, "message": str(e)},
            status_code=500,
        )


@app.get("/api/download/{filename}")
async def download_report(filename: str):
    file_path = OUTPUT_DIR / filename

    if not file_path.exists():
        return JSONResponse(
            {"success": False, "message": "File not found"},
            status_code=404,
        )

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )