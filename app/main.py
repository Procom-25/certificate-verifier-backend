from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv("/app/.env")

app = FastAPI()

MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["certificates"]
collection = db["participants"]

class CertificateResponse(BaseModel):
    is_verified: bool

def generate_certificate_html(verified: bool, certificate=None):
    verification_status = "Certificate is Verified ✅" if verified else "Certificate is Not Verified ❌"
    details = (
        f"""
        <p><span class="highlight">{certificate['student_name']}</span> participated in the competition 
        <span class="highlight">{certificate['competition_name']}</span> with the team 
        <span class="highlight">{certificate['team_name']}</span>.</p>
        <p>Team Leader: <span class="highlight">{certificate['leader_name']}</span></p>
        """
        if verified else "<p>This certificate ID is not found.</p>"
    )

    return f"""
    <html>
        <head>
            <title>Certificate Verification</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f5;
                    text-align: center;
                    padding: 20px;
                }}
                .container {{
                    position: relative;
                    max-width: 800px;
                    margin: 0 auto;
                }}
                .verified-image {{
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    width: 65px;
                    height: auto;
                }}
                h1 {{
                    color: #000000;
                }}
                .content {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid rgba(228, 228, 231, 1);
                    position: relative;
                }}
                .details {{
                    font-size: 18px;
                    color: #333;
                }}
                .highlight {{
                    font-weight: bold;
                    color: #000000;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h1>{verification_status}</h1>
                    <div class="details">
                        {details}
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/certificates/verify/{certificate_id}", response_class=HTMLResponse)
async def verify_certificate(certificate_id: str):
    certificate = collection.find_one({"uuid": certificate_id})

    if certificate:
        return HTMLResponse(content=generate_certificate_html(True, certificate))
    else:
        return HTMLResponse(content=generate_certificate_html(False), status_code=404)



@app.get("/test", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Certificate Verification</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f5;
                    text-align: center;
                    padding: 20px;
                }
            </style>
        </head>
        <body>
            This is testing page.
        </body>
    </html>
    """

@app.exception_handler(404)
async def custom_404_handler(request, exc):
    return HTMLResponse(content="""
    <html>
        <head>
            <title>404 Not Found</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f5;
                    text-align: center;
                    padding: 20px;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid rgba(228, 228, 231, 1);
                }
                a {
                    display: inline-block;
                    margin-top: 10px;
                    color: blue;
                    text-decoration: none;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>404 - Page Not Found</h1>
                <p>Oops! The page you are looking for does not exist.</p>
            </div>
        </body>
    </html>
    """, status_code=404)