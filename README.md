# OAuth Kit

A flexible, extensible OAuth 2.0 authentication kit with a modular architecture for handling OAuth flows across multiple providers and services. The kit is designed as a reusable OAuth library that can be integrated into any Python project, with a FastAPI testing interface included for easy development and testing.

## Table of Contents
- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Architecture & Design](#architecture--design)
- [Getting Started](#getting-started)
- [Modifying Scopes for Different Projects](#modifying-scopes-for-different-projects)
- [Expanding to Other Providers](#expanding-to-other-providers)
- [Expanding to Other Services](#expanding-to-other-services)
- [Integration Guide](#integration-guide)
- [API Endpoints](#api-endpoints)

## Project Overview

This OAuth Kit is a **reusable Python library** for OAuth 2.0 integration. The core OAuth logic is provider-agnostic and designed to be imported into any application. Currently, it supports **Google Cloud Platform (GCP)** for **IMAP/Gmail** services, but the architecture is built to easily accommodate additional providers (AWS, Azure, Microsoft, etc.) and services (Calendar, Drive, etc.).

The included FastAPI application (`main.py`) serves as a **testing and development interface** - it demonstrates how to use the kit and provides a ready-to-use OAuth server for quick integration testing. You can use the FastAPI app as-is, integrate the core OAuth modules into your existing application, or adapt the patterns to your framework of choice.

### Key Features
- ✅ Modular architecture with clear separation of concerns
- ✅ Type-safe enums for providers and services
- ✅ Base classes for easy extension
- ✅ Standardized credential formatting
- ✅ Framework-agnostic core OAuth logic
- ✅ FastAPI testing interface included
- ✅ OAuth 2.0 flow handling with redirect callbacks
- ✅ Token management and refresh capabilities

## Project Structure

```
oauth-kit/
├── main.py                          # FastAPI application entry point
├── requirements.txt                 # Python dependencies
├── gcp_secret.json                  # GCP OAuth credentials (not in repo)
│
├── app/                             # Application layer
│   ├── models.py                    # Pydantic models for API requests/responses
│   └── templates/
│       └── oauth_success.html       # OAuth success page template
│
└── src/
    └── oauth/                       # Core OAuth implementation
        ├── __init__.py              # Package initialization, exports gcp_oauth
        ├── enums.py                 # Provider and Service enums with scope definitions
        ├── base.py                  # BaseOAuth class with credential formatting
        │
        ├── gcp/                     # GCP-specific base implementation
        │   └── services.py          # GCPOAuth base class
        │
        ├── services/                # Service-specific implementations
        │   ├── __init__.py
        │   └── gcp_oauth.py         # Concrete GCP OAuth implementation
        │
        └── utils/
            └── email_utils.py       # Email/IMAP utility functions
```

### Architecture Layers

#### 1. **Enums Layer** (`src/oauth/enums.py`)
Defines supported providers and services with their required OAuth scopes.

```python
class Provider(StrEnum):
    GCP = "gcp"
    # Add more: AWS, AZURE, MICROSOFT, etc.

class Service(StrEnum):
    IMAP = "imap"
    # Add more: CALENDAR, DRIVE, STORAGE, etc.
```

#### 2. **Base Layer** (`src/oauth/base.py`)
`BaseOAuth` class provides:
- Standardized credential formatting across all providers
- Common interface for OAuth implementations
- Consistent data structure for storing credentials

#### 3. **Provider Base Layer** (`src/oauth/gcp/services.py`)
Provider-specific base classes (e.g., `GCPOAuth`) that:
- Handle provider-specific OAuth flows
- Implement authentication logic
- Manage token operations (get, refresh, decrypt)

#### 4. **Concrete Implementation Layer** (`src/oauth/services/gcp_oauth.py`)
Service-specific implementations that:
- Configure provider with credentials
- Define redirect URIs
- Handle authorization URLs
- Register and store credentials

#### 5. **Application Layer** (`main.py`, `app/`)
FastAPI application that:
- Exposes REST API endpoints
- Handles OAuth callbacks
- Manages user-facing responses

## Architecture & Design

### OAuth Flow

```
1. Client → POST /oauth
   ↓
2. Server generates authorization URL with scopes
   ↓
3. Client → Redirects user to provider's consent page
   ↓
4. User grants permissions
   ↓
5. Provider → GET /oauth/gcp/imap-redirect (with auth code)
   ↓
6. Server exchanges code for tokens
   ↓
7. Server stores credentials (currently to JSON file)
   ↓
8. Display success page to user
```

### Data Flow

```
OAuthRequest (API) → Service Enum → get_scopes() → Provider Flow
                                                      ↓
                                            Authorization URL
                                                      ↓
Provider Callback → Fetch Token → Decrypt ID Token → Format Credentials
                                                      ↓
                                              Store in Database
```

## Getting Started

### Prerequisites
- Python 3.8+
- GCP Project with OAuth 2.0 credentials
- Domain/localhost for redirect URI

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Create GCP OAuth Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create OAuth 2.0 Client ID
   - Download JSON and save as `gcp_secret.json`

2. **Update Redirect URI**
   - In `src/oauth/services/gcp_oauth.py`, modify `REDIRECT_URL` if needed:
     ```python
     REDIRECT_URL = "http://localhost:8080/oauth/gcp/imap-redirect"
     ```

3. **Run the Server**
   ```bash
   python main.py
   ```

### Usage

1. **Initiate OAuth**
   ```bash
   curl -X POST http://localhost:8080/oauth \
     -H "Content-Type: application/json" \
     -d '{"provider": "gcp", "service": "imap"}'
   ```

2. **Navigate to Authorization URL** (from response)

3. **Grant Permissions** - User will be redirected back after consent

4. **Credentials Stored** - Check `debug_gcp_imap_creds.json`

## Modifying Scopes for Different Projects

The `get_scopes()` method in `src/oauth/enums.py` is the **central configuration point** for OAuth scopes. This is where you define what permissions your application requests.

### Current Implementation

```python
class Service(StrEnum):
    IMAP = "imap"

    def get_scopes(self, provider: Provider):
        if self == Service.IMAP and provider == Provider.GCP:
            return [
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/gmail.labels",
                "https://www.googleapis.com/auth/gmail.metadata",
                "https://www.googleapis.com/auth/gmail.modify",
            ]
        else: 
            raise ValueError(f"Unsupported service {self} for provider {provider}")
```

### Why Modify Scopes?

Different projects have different requirements:
- **Read-only email**: Only need `gmail.readonly`
- **Send emails**: Need `gmail.send`
- **Full Gmail access**: Need `gmail.compose`, `gmail.insert`, etc.
- **Calendar integration**: Need `calendar.readonly` or `calendar.events`

### How to Modify Scopes

#### Example 1: Read-Only Gmail Access

```python
def get_scopes(self, provider: Provider):
    if self == Service.IMAP and provider == Provider.GCP:
        return [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/gmail.readonly",  # Read-only
        ]
```

#### Example 2: Gmail Send Capability

```python
def get_scopes(self, provider: Provider):
    if self == Service.IMAP and provider == Provider.GCP:
        return [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/gmail.send",      # Send emails
            "https://www.googleapis.com/auth/gmail.compose",   # Draft emails
        ]
```

#### Example 3: Multiple Services

```python
def get_scopes(self, provider: Provider):
    if self == Service.IMAP and provider == Provider.GCP:
        return [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/gmail.modify",
        ]
    elif self == Service.CALENDAR and provider == Provider.GCP:
        return [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/calendar.events",
        ]
```

### ⚠️ Important Notes About Scope Changes

1. **Breaking Changes**: Changing scopes can break existing integrations
2. **User Re-authorization**: Users must re-authorize when scopes change
3. **Revoke Old Tokens**: Always revoke old authorization tokens before changing scopes
4. **Scope Documentation**: Document why each scope is needed for compliance

### Common GCP Scopes Reference

| Scope | Purpose |
|-------|---------|
| `gmail.readonly` | Read all Gmail data |
| `gmail.modify` | Read, compose, send messages, permanently delete |
| `gmail.send` | Send email on user's behalf |
| `gmail.compose` | Create drafts |
| `calendar.readonly` | Read calendar events |
| `calendar.events` | View and edit events |
| `drive.readonly` | View files |
| `drive.file` | View and manage files created by app |

[Full GCP Scope List](https://developers.google.com/identity/protocols/oauth2/scopes)

## Expanding to Other Providers

The layered architecture makes it straightforward to add new OAuth providers (Microsoft, AWS Cognito, Azure AD, GitHub, etc.). The pattern follows the existing GCP implementation structure.

### Adding a New Provider: Step-by-Step

The process involves five layers, mirroring the existing GCP implementation:

#### 1. **Define the Provider in Enums** (`src/oauth/enums.py`)

Add your new provider to the `Provider` enum. This is a simple one-line addition that makes the provider available throughout the system.

#### 2. **Configure Scopes** (`src/oauth/enums.py`)

Extend the `get_scopes()` method in the `Service` enum to handle your new provider. Add an `elif` branch that returns the appropriate OAuth scopes for your provider-service combination. For example, Microsoft IMAP would need scopes like `"https://outlook.office.com/IMAP.AccessAsUser.All"` and `"offline_access"` for refresh tokens.

Each provider has its own scope format and requirements - consult the provider's OAuth documentation to determine which scopes you need.

#### 3. **Create Provider Base Class** (`src/oauth/<provider>/services.py`)

Create a new directory for your provider (e.g., `src/oauth/microsoft/`) and implement a base class that inherits from `BaseOAuth`. This class handles the provider-specific OAuth mechanics:

- **Setup method**: Initialize with provider credentials (client ID, client secret, tenant ID, etc.)
- **Flow creation**: Create the OAuth flow object using the provider's SDK (e.g., `msal` for Microsoft, `boto3` for AWS)
- **Authorization URL generation**: Build the authorization URL with proper scopes and redirect URIs
- **Token exchange**: Exchange authorization codes for access/refresh tokens
- **Token operations**: Refresh tokens, validate tokens, decrypt ID tokens as needed

This layer abstracts away the provider-specific OAuth library calls and presents a consistent interface.

#### 4. **Implement Concrete Service Class** (`src/oauth/services/<provider>_oauth.py`)

Create a concrete implementation that extends your provider base class. This layer:

- **Loads credentials**: Reads client secrets from environment variables or config files
- **Defines redirect URIs**: Sets the callback URLs for your application
- **Exposes auth URL methods**: Provides simple methods to get authorization URLs for each service
- **Registers credentials**: Formats and stores the OAuth credentials using the inherited `format_credentials()` method from `BaseOAuth`

Look at `src/oauth/services/gcp_oauth.py` as a reference - your implementation will follow the same pattern with provider-specific details.

#### 5. **Export the OAuth Instance** (`src/oauth/__init__.py`)

Instantiate your new OAuth class and export it. This creates a singleton instance that can be imported and used throughout your application. Update the `__all__` list to include your new instance.

#### 6. **Integrate with FastAPI (Optional - for testing)**

If you're using the included FastAPI testing interface, add:

- **Lifespan setup**: Call your provider's `setup()` method during app startup
- **Callback endpoint**: Create a route handler for the OAuth redirect (e.g., `/oauth/microsoft/imap-redirect`)
- **Initiation logic**: Add a branch in the `/oauth` POST endpoint to handle your provider-service combination

This step is optional if you're integrating the kit into another application - you'll implement similar logic in your own framework instead.

## Expanding to Other Services

Adding new services (Calendar, Drive, Storage, etc.) follows a similar pattern to adding providers, but focuses on service-specific scopes and methods.

### Adding a New Service: Step-by-Step

#### 1. **Define the Service in Enums** (`src/oauth/enums.py`)

Add your new service to the `Service` enum. This could be `CALENDAR`, `DRIVE`, `STORAGE`, or any other service you want to support.

#### 2. **Configure Service Scopes** (`src/oauth/enums.py`)

Extend the `get_scopes()` method to include your new service for each supported provider. Each provider-service combination may require different scope URLs and permissions. For example:

- GCP Calendar might need `calendar.events` and `calendar.readonly` scopes
- GCP Drive might need `drive.file` and `drive.metadata.readonly` scopes
- Microsoft Calendar would use different scope URLs specific to Microsoft Graph API

Research the provider's documentation to determine the exact scope strings required for your service.

#### 3. **Add Service Methods to Provider Base** (`src/oauth/<provider>/services.py`)

In each provider's base class, add methods specific to your new service:

- **Flow creation method**: A method like `get_calendar_flow()` that creates an OAuth flow with the service's scopes
- **Token management**: If the service has unique token requirements, add service-specific token handling

Follow the pattern of existing methods like `get_imap_flow()` - the implementation will be similar but with service-specific scopes pulled from your enum.

#### 4. **Implement in Concrete Service Class** (`src/oauth/services/<provider>_oauth.py`)

In the concrete implementation for each provider, add:

- **Redirect URI property**: Define where the OAuth callback should go for this service
- **Authorization URL method**: Create a method like `get_calendar_auth_url()` that generates the auth URL for your service
- **Credential registration**: Implement a method like `register_calendar_credentials()` that stores the OAuth tokens using the inherited `format_credentials()` method

Each service gets its own set of methods that follow the same pattern as the existing IMAP implementation.

#### 5. **Integrate with FastAPI (Optional - for testing)**

If using the FastAPI testing interface:

- **Add callback route**: Create an endpoint like `/oauth/gcp/calendar-redirect` to handle the OAuth callback
- **Handle token exchange**: In the callback, fetch the token and register the credentials
- **Update initiation endpoint**: Add a branch in the `/oauth` POST handler for your new service

This testing setup lets you verify the OAuth flow works before integrating into your production application.

### Key Considerations

- **Service-Provider Combinations**: Not all services make sense for all providers. Calendar works for GCP and Microsoft, but Storage might be different across providers
- **Scope Differences**: The same logical service (e.g., email) requires completely different scopes across providers
- **Multiple Services**: Users can authorize multiple services independently - each gets its own set of stored credentials
- **Reuse Base Logic**: All services share the same credential formatting and storage pattern from `BaseOAuth`

## Integration Guide

The OAuth kit is designed to be integrated into any Python application, regardless of framework. The FastAPI interface in `main.py` is purely for testing and demonstration.

### Using the Kit in Your Application

#### Direct Import and Usage

Import the OAuth instances and use them directly in your application:

```python
from src.oauth import gcp_oauth
from src.oauth.enums import Provider, Service

# Initialize during app startup
gcp_oauth.setup()

# In your OAuth initiation logic
auth_url = gcp_oauth.get_imap_auth_url()
# Redirect user to auth_url

# In your OAuth callback handler (after user authorizes)
flow = gcp_oauth.get_imap_flow(redirect_uri=your_redirect_uri)
flow.fetch_token(authorization_response=callback_url)
credentials = flow.credentials
gcp_oauth.register_imap_credentials(flow, credentials)
```

### Using `get_credentials()` - The Main Function

**`get_credentials()` is the primary function you'll use** after initial OAuth setup. This async method retrieves stored credentials for a user and automatically handles token refresh when needed.

#### Function Signature

```python
async def get_credentials(
    self,
    email: str,
    service: Service,
    raise_refresh_error: bool = True
) -> GCPOAuthCredentials | None
```

#### Parameters

- **`email`** (str): The user's email address associated with the OAuth credentials
- **`service`** (Service): The service enum (e.g., `Service.IMAP`) to retrieve credentials for
- **`raise_refresh_error`** (bool, default=True): Whether to raise an exception if token refresh fails

#### Returns

- **`GCPOAuthCredentials`**: Valid, refreshed credentials ready to use
- **`None`**: If credentials don't exist or refresh fails (when `raise_refresh_error=False`)

#### Usage Example

```python
from src.oauth import gcp_oauth
from src.oauth.enums import Service
from src.oauth.services.exceptions import RefreshError

# In your application code (e.g., when sending an email)
async def send_email(user_email: str, message: str):
    try:
        # Get credentials - will automatically refresh if expired
        creds = await gcp_oauth.get_credentials(
            email=user_email,
            service=Service.IMAP
        )
        
        if creds is None:
            # User hasn't authorized yet
            return {"error": "Please authorize your Gmail account first"}
        
        # Use credentials with Gmail API
        # ... your email sending logic here ...
        
    except RefreshError as e:
        # Token refresh failed - user needs to re-authorize
        return {"error": "Please re-authorize your Gmail account"}
```

#### Automatic Token Refresh

The function handles token validation and refresh automatically:

1. **Loads** stored credentials from storage (database/file)
2. **Checks** if credentials are valid (`creds.valid`)
3. **Refreshes** automatically if expired using the refresh token
4. **Updates** stored credentials in the background after refresh
5. **Returns** valid, ready-to-use credentials

#### Error Handling

```python
# Option 1: Raise exception on refresh failure (default)
creds = await gcp_oauth.get_credentials(user_email, Service.IMAP)
# Raises RefreshError if refresh fails

# Option 2: Return None on refresh failure
creds = await gcp_oauth.get_credentials(
    user_email, 
    Service.IMAP,
    raise_refresh_error=False
)
if creds is None:
    # Handle gracefully - redirect to re-authorization
    pass
```

#### Integration Pattern

**Typical workflow in your application:**

```python
# 1. First-time setup: User authorizes (one-time)
#    - Generate auth URL with get_imap_auth_url()
#    - Handle callback with register_imap_credentials()

# 2. Ongoing usage: Retrieve credentials (every API call)
#    - Call get_credentials() to get valid tokens
#    - Use returned credentials with provider's API
#    - Token refresh happens automatically

# Example: Email service class
class EmailService:
    async def fetch_emails(self, user_email: str):
        # This is the only call you need!
        creds = await gcp_oauth.get_credentials(user_email, Service.IMAP)
        
        if not creds:
            raise ValueError("User not authorized")
        
        # Use creds with Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me').execute()
        return results
```

#### Best Practices

- ✅ **Always await**: `get_credentials()` is async - don't forget `await`
- ✅ **Check for None**: Credentials may not exist for a user
- ✅ **Handle RefreshError**: Plan for token refresh failures
- ✅ **Use raised exceptions**: Keep `raise_refresh_error=True` for explicit error handling
- ✅ **Trust the refresh**: Don't manually check `creds.valid` - the function handles it
- ✅ **Call frequently**: It's designed to be called for each API operation

#### Framework Integration Examples

**Django**: Call `setup()` in your `AppConfig.ready()` method, handle OAuth in views

**Flask**: Call `setup()` in `create_app()`, implement OAuth routes as regular Flask routes

**Streamlit**: Call `setup()` at module level, use OAuth methods in your page functions

**AWS Lambda**: Call `setup()` once per cold start, use OAuth methods in handler functions

The core OAuth logic is framework-independent - you just need to:
1. Call `setup()` once at startup
2. Generate authorization URLs when users want to connect
3. Handle the OAuth callback and register credentials
4. Store the formatted credentials in your database

### Customizing Credential Storage

By default, `register_imap_credentials()` writes to a JSON file for testing. In production:

1. Modify the `register_*_credentials()` methods in `src/oauth/services/<provider>_oauth.py`
2. Replace the JSON write with your database call
3. Store the `formatted_creds` dict using your ORM or database client

The standardized credential format from `BaseOAuth.format_credentials()` works with any storage backend.

## API Endpoints

### `POST /oauth`
Initiates OAuth flow for a provider/service combination.

**Request:**
```json
{
  "provider": "gcp",
  "service": "imap"
}
```

**Response:**
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?..."
}
```

### `GET /oauth/gcp/imap-redirect`
OAuth callback endpoint for GCP IMAP service.

**Query Parameters:**
- `code`: Authorization code from provider
- `state`: CSRF protection state
- `error` (optional): Error message if auth failed

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Best Practices

### Security
- ✅ Store credentials securely (use database, not JSON files in production)
- ✅ Validate redirect URIs
- ✅ Use HTTPS in production
- ✅ Implement CSRF protection with state parameter
- ✅ Rotate client secrets regularly
- ✅ Never commit `gcp_secret.json` or similar files

### Scope Management
- ✅ Request only necessary scopes (principle of least privilege)
- ✅ Document why each scope is needed
- ✅ Revoke and re-authorize when changing scopes
- ✅ Test scope changes in development first

### Code Organization
- ✅ Keep provider-specific logic in provider modules
- ✅ Use base classes for shared functionality
- ✅ Type hint everything for better IDE support
- ✅ Document public methods and complex logic

## Troubleshooting

### Common Issues

**"Invalid redirect URI"**
- Ensure redirect URI matches exactly in GCP Console
- Check for trailing slashes
- Verify HTTP vs HTTPS

**"Insufficient permissions"**
- Check requested scopes in `get_scopes()`
- Verify scopes are enabled in provider console
- User may need to re-authorize

**"Token expired"**
- Implement token refresh logic
- Store and use refresh tokens
- Handle token refresh in your application

## Future Enhancements

- [ ] Token refresh mechanism
- [ ] Database integration for credential storage
- [ ] Support for AWS Cognito
- [ ] Support for Azure AD / Microsoft Identity
- [ ] Support for GitHub OAuth
- [ ] Webhook support for token revocation
- [ ] Admin dashboard for managing OAuth apps
- [ ] Multi-tenant support

## License

MIT License - see [LICENSE](LICENSE) file for details

## Developer

**Rudra Sikri**  
Email: rudrasikri12@gmail.com

## Contributing

Contributions welcome! Please follow the established patterns and add tests for new providers/services.

For questions or contributions, reach out to the developer above.
