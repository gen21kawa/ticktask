import asyncio
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs
from typing import Optional, Dict, Any
import httpx
from cryptography.fernet import Fernet
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from aiohttp import web
import logging

logger = logging.getLogger(__name__)


class TokenStorage:
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".ticktask" / "tokens.enc"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._fernet = self._get_or_create_key()

    def _get_or_create_key(self) -> Fernet:
        key_path = self.storage_path.parent / "key.key"
        if key_path.exists():
            with open(key_path, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, "wb") as f:
                f.write(key)
            os.chmod(key_path, 0o600)
        return Fernet(key)

    def save_tokens(self, tokens: Dict[str, Any]) -> None:
        tokens["saved_at"] = datetime.now().isoformat()
        encrypted = self._fernet.encrypt(json.dumps(tokens).encode())
        with open(self.storage_path, "wb") as f:
            f.write(encrypted)
        os.chmod(self.storage_path, 0o600)

    def load_tokens(self) -> Optional[Dict[str, Any]]:
        if not self.storage_path.exists():
            return None
        try:
            with open(self.storage_path, "rb") as f:
                encrypted = f.read()
            decrypted = self._fernet.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"Failed to load tokens: {e}")
            return None

    def clear_tokens(self) -> None:
        if self.storage_path.exists():
            self.storage_path.unlink()


class OAuth2Handler:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = "http://localhost:8080/callback"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = "https://ticktick.com"
        self.api_base_url = "https://api.ticktick.com"
        self.token_storage = TokenStorage()
        self._server = None
        self._auth_code = None
        self._auth_error = None

    def get_authorization_url(self, state: str = "random_state") -> str:
        params = {
            "client_id": self.client_id,
            "scope": "tasks:write tasks:read",
            "state": state,
            "redirect_uri": self.redirect_uri,
            "response_type": "code"
        }
        return f"{self.base_url}/oauth/authorize?{urlencode(params)}"

    async def _handle_callback(self, request: web.Request) -> web.Response:
        code = request.query.get("code")
        error = request.query.get("error")
        
        if error:
            self._auth_error = error
            return web.Response(text=f"Authorization failed: {error}", status=400)
        
        if code:
            self._auth_code = code
            return web.Response(text="Authorization successful! You can close this window.", status=200)
        
        return web.Response(text="No authorization code received", status=400)

    async def _run_server(self, app: web.Application, port: int = 8080) -> None:
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", port)
        await site.start()
        self._server = runner

    async def wait_for_authorization(self, timeout: int = 300) -> str:
        app = web.Application()
        app.router.add_get("/callback", self._handle_callback)
        
        parsed_uri = urlparse(self.redirect_uri)
        port = parsed_uri.port or 8080
        
        await self._run_server(app, port)
        
        auth_url = self.get_authorization_url()
        logger.info(f"Opening browser for authorization: {auth_url}")
        webbrowser.open(auth_url)
        
        start_time = asyncio.get_event_loop().time()
        while self._auth_code is None and self._auth_error is None:
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError("Authorization timeout")
            await asyncio.sleep(0.1)
        
        if self._server:
            await self._server.cleanup()
        
        if self._auth_error:
            raise Exception(f"Authorization error: {self._auth_error}")
        
        return self._auth_code

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth/token",
                auth=(self.client_id, self.client_secret),
                data={
                    "code": code,
                    "grant_type": "authorization_code",
                    "scope": "tasks:write tasks:read",
                    "redirect_uri": self.redirect_uri
                }
            )
            response.raise_for_status()
            tokens = response.json()
            self.token_storage.save_tokens(tokens)
            return tokens

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth/token",
                auth=(self.client_id, self.client_secret),
                data={
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
            )
            response.raise_for_status()
            tokens = response.json()
            self.token_storage.save_tokens(tokens)
            return tokens

    async def get_access_token(self) -> Optional[str]:
        tokens = self.token_storage.load_tokens()
        if not tokens:
            return None
        
        # Check if token needs refresh (assuming 1 hour expiry)
        saved_at = datetime.fromisoformat(tokens.get("saved_at", datetime.now().isoformat()))
        if datetime.now() - saved_at > timedelta(hours=1):
            if "refresh_token" in tokens:
                try:
                    tokens = await self.refresh_token(tokens["refresh_token"])
                except Exception as e:
                    logger.error(f"Failed to refresh token: {e}")
                    return None
            else:
                return None
        
        return tokens.get("access_token")

    async def login(self) -> str:
        code = await self.wait_for_authorization()
        tokens = await self.exchange_code_for_token(code)
        return tokens["access_token"]

    def logout(self) -> None:
        self.token_storage.clear_tokens()