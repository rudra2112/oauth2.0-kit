from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from pathlib import Path
from src.oauth import gcp_oauth
from app.models import OAuthRequest, OAuthResponse
from src.oauth.enums import Provider as OAuthProvider, Service as OAuthService
from contextlib import asynccontextmanager


# Setup templates directory
templates = Jinja2Templates(directory="app/templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    gcp_oauth.setup()
    yield

app = FastAPI(title="OAuth Service", lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint"""
    return "<h1>OAuth Service Running</h1>"


@app.get("/oauth/gcp/imap-redirect", response_class=HTMLResponse)
async def oauth_callback(request: Request):
    """
    OAuth callback endpoint that displays the confirmation page.
    
    Args:
        request: FastAPI request object
        code: Authorization code from OAuth provider
        state: State parameter for CSRF protection
        error: Error message if OAuth failed
    """
    # Check if there's an error in the query parameters
    error_param = request.query_params.get("error")
    error_description = request.query_params.get("error_description", "")
    
    if error_param:
        return f"""
            <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: red;">Authorization Failed</h1>
                    <p><strong>Error:</strong> {error_param}</p>
                    {f'<p><strong>Description:</strong> {error_description}</p>' if error_description else ''}
                    <button onclick="window.close()" style="margin-top: 20px; padding: 10px 20px; cursor: pointer;">Close Window</button>
                </body>
            </html>
        """
    
    request_uri = str(request.url)
    request_uri = request_uri.replace("http://", "https://") if not request_uri.startswith("https://") else request_uri
    # Here you can process the authorization code
    try:
        orc_imap_flow = gcp_oauth.get_imap_flow(redirect_uri=gcp_oauth.imap_auth_redirect_uri)
        orc_imap_flow.fetch_token(
            authorization_response=request_uri,
        )

        creds = orc_imap_flow.credentials
        gcp_oauth.register_imap_credentials(orc_imap_flow, creds)

    except Exception as e:
        error_message = str(e)
        return f"""
            <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: red;">Authorization Failed</h1>
                    <p><strong>Error:</strong> {error_message}</p>
                    <button onclick="window.close()" style="margin-top: 20px; padding: 10px 20px; cursor: pointer;">Close Window</button>
                </body>
            </html>
        """
    else:
        return templates.TemplateResponse("oauth_success.html", {"request": request})
    
@app.post("/oauth")
async def oauth(request: OAuthRequest) -> OAuthResponse:
    """OAuth initiation endpoint"""
    if request.provider == OAuthProvider.GCP and request.service == OAuthService.IMAP:
        imap_flow = gcp_oauth.get_imap_flow()
        auth_url = gcp_oauth.get_imap_auth_url(
            imap_flow
        )
        return OAuthResponse(authorization_url=auth_url)
    else:
        raise ValueError(f"Unsupported provider {request.provider} or service {request.service}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8080)
