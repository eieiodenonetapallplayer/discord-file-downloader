import json
import aiohttp
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtCore import QUrl

class DiscordOAuth(QObject):
    """
    ระบบ Login ด้วย Discord OAuth
    """
    login_success = pyqtSignal(str)  # ส่ง token เมื่อล็อกอินสำเร็จ
    login_failed = pyqtSignal(str)   # ส่งข้อความ error เมื่อล็อกอินล้มเหลว

    def __init__(self, client_id, redirect_uri, scopes):
        super().__init__()
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.token = None

    def create_oauth_window(self):
        """
        สร้างหน้าต่าง OAuth
        """
        self.webview = QWebEngineView()
        self.profile = QWebEngineProfile("oauth_profile", self.webview)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        
        self.webview.setPage(QWebEnginePage(self.profile, self.webview))
        oauth_url = f"https://discord.com/api/oauth2/authorize?client_id={self.client_id}&redirect_uri={self.redirect_uri}&response_type=code&scope={' '.join(self.scopes)}"
        self.webview.load(QUrl(oauth_url))
        self.webview.urlChanged.connect(self._check_redirect)
        
        return self.webview

    def _check_redirect(self, url):
        """
        ตรวจสอบเมื่อมีการ redirect กลับมาจาก Discord
        """
        if "code=" in url.toString():
            code = self._extract_code_from_url(url)
            self._exchange_code_for_token(code)

    def _extract_code_from_url(self, url):
        """
        ดึง code จาก URL
        """
        return url.toString().split("code=")[1].split("&")[0]

    async def _exchange_code_for_token(self, code):
        """
        แลก code เป็น token (ควรใช้ backend server จริง)
        """
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'client_id': self.client_id,
                    'client_secret': 'YOUR_CLIENT_SECRET',
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': self.redirect_uri,
                    'scope': ' '.join(self.scopes)
                }
                
                async with session.post('https://discord.com/api/oauth2/token', data=data) as resp:
                    if resp.status == 200:
                        token_data = await resp.json()
                        self.token = token_data.get('access_token')
                        self.login_success.emit(self.token)
                    else:
                        error = await resp.text()
                        self.login_failed.emit(f"Failed to get token: {error}")
        except Exception as e:
            self.login_failed.emit(f"Error: {str(e)}")

class TokenValidator:
    """
    ตรวจสอบความถูกต้องของ Token
    """
    @staticmethod
    async def validate_token(token):
        """
        ตรวจสอบว่า Token ถูกต้องหรือไม่
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": token}
                async with session.get("https://discord.com/api/v9/users/@me", headers=headers) as resp:
                    return resp.status == 200
        except Exception:
            return False

    @staticmethod
    async def check_guild_membership(token, guild_id):
        """
        ตรวจสอบว่า Token อยู่ใน Guild ที่กำหนดหรือไม่
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": token}
                async with session.get("https://discord.com/api/v9/users/@me/guilds", headers=headers) as resp:
                    if resp.status == 200:
                        guilds = await resp.json()
                        return any(guild['id'] == guild_id for guild in guilds)
                    return False
        except Exception:
            return False