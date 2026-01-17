"""
Enhanced Shopee Live Streaming Integration Service
Mengintegrasikan 22 API endpoints Shopee Live untuk streaming affiliate
"""

import httpx
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from app.config import settings

logger = logging.getLogger(__name__)


class ShopeeStreamingService:
    """Service untuk Shopee Live Streaming API"""

    # API Base URLs
    SELLER_API = "https://seller.shopee.co.id/api/v4"
    CREATOR_API = "https://creator.shopee.co.id/supply/api/lm/sellercenter"
    LIVE_API = "https://live.shopee.co.id/api/v1"
    SELLER_APP_API = "https://seller-app.shopee.co.id/api/app/pas/v1"
    SHOPEE_AUTH = "https://shopee.co.id/api/v2"
    SHOPEE_MAIN = "https://shopee.co.id"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.access_token = None
        self.shop_id = None
        self.user_id = None

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    # ==================== AUTHENTICATION APIs ====================

    async def generate_qr_code(self) -> dict:
        """
        1. AUTHENTICATION QR CODE API
        Generate QR code untuk login Shopee
        """
        try:
            response = await self.client.post(
                f"{self.SHOPEE_AUTH}/authentication/gen_qrcode"
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Generated QR code: {data}")
            return data
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            raise

    async def check_qr_status(self, qrcode_id: str) -> dict:
        """
        14. QR CODE STATUS API
        Mengecek status QR code login
        """
        try:
            params = {"qrcode_id": qrcode_id}
            response = await self.client.get(
                f"{self.SHOPEE_AUTH}/authentication/qrcode_status",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error checking QR status: {e}")
            raise

    async def qr_code_login(self, qrcode_id: str) -> dict:
        """
        15. QR CODE LOGIN API
        Melakukan login menggunakan QR code
        """
        try:
            payload = {"qrcode_id": qrcode_id}
            response = await self.client.post(
                f"{self.SHOPEE_AUTH}/authentication/qrcode_login",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            # Save tokens
            if "access_token" in data:
                self.access_token = data["access_token"]
            if "shop_id" in data:
                self.shop_id = data["shop_id"]
            if "user_id" in data:
                self.user_id = data["user_id"]
            
            logger.info(f"QR login successful for shop {self.shop_id}")
            return data
        except Exception as e:
            logger.error(f"Error QR login: {e}")
            raise

    # ==================== CREATOR/STREAMER APIs ====================

    async def get_creator_user_info(self, access_token: str = None) -> dict:
        """
        5. CREATOR USER INFO API
        Mendapatkan informasi user creator/streamer
        """
        try:
            token = access_token or self.access_token
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await self.client.get(
                f"{self.CREATOR_API}/userInfo",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting creator user info: {e}")
            raise

    async def get_session_list(
        self,
        access_token: str = None,
        page: int = 1,
        page_size: int = 10,
        name: str = "",
        order_by: str = "",
        sort: str = ""
    ) -> dict:
        """
        4. CREATOR SESSION LIST API
        Mendapatkan daftar sesi live streaming dengan pagination
        """
        try:
            token = access_token or self.access_token
            headers = {"Authorization": f"Bearer {token}"}
            
            params = {
                "page": page,
                "pageSize": page_size,
                "name": name,
                "orderBy": order_by,
                "sort": sort
            }
            
            response = await self.client.get(
                f"{self.CREATOR_API}/realtime/sessionList",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting session list: {e}")
            return {"sessions": [], "total": 0}

    async def get_session_info(
        self,
        session_id: str,
        access_token: str = None
    ) -> dict:
        """
        2. CREATOR SESSION INFO API
        Mendapatkan informasi sesi live streaming realtime
        """
        try:
            token = access_token or self.access_token
            headers = {"Authorization": f"Bearer {token}"}
            
            params = {"sessionId": session_id}
            response = await self.client.get(
                f"{self.CREATOR_API}/realtime/dashboard/sessionInfo",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            raise

    async def get_dashboard_overview(
        self,
        session_id: str,
        access_token: str = None
    ) -> dict:
        """
        3. CREATOR DASHBOARD OVERVIEW API
        Mendapatkan overview dashboard live streaming
        """
        try:
            token = access_token or self.access_token
            headers = {"Authorization": f"Bearer {token}"}
            
            params = {"sessionId": session_id}
            response = await self.client.get(
                f"{self.CREATOR_API}/realtime/dashboard/overview",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting dashboard overview: {e}")
            raise

    # ==================== STREAMING PROMOTION APIs ====================

    async def get_streaming_promotions(
        self,
        access_token: str = None
    ) -> dict:
        """
        1. STREAMING PROMOTION API
        Mendapatkan daftar streamer selector untuk promosi streaming
        """
        try:
            token = access_token or self.access_token
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await self.client.get(
                f"{self.SELLER_API}/streaming_promotion/streamer_selector/",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting streaming promotions: {e}")
            return {"streamers": []}

    async def get_promotions_today(
        self,
        access_token: str = None
    ) -> dict:
        """
        16. GET PROMOTIONS TODAY API
        Mendapatkan daftar promosi live stream hari ini
        """
        try:
            token = access_token or self.access_token
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await self.client.get(
                f"{self.SELLER_APP_API}/live_stream/get_promotions_today/",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting promotions today: {e}")
            return {"promotions": []}

    async def edit_live_stream_promotion(
        self,
        promotion_data: dict,
        access_token: str = None
    ) -> dict:
        """
        22. EDIT LIVE STREAM PROMOTION API
        Mengedit setting promosi live stream
        """
        try:
            token = access_token or self.access_token
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                f"{self.SELLER_APP_API}/live_stream/edit/",
                headers=headers,
                json=promotion_data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error editing promotion: {e}")
            raise

    # ==================== ITEMS/PRODUCTS APIs ====================

    async def get_item_promotion_list(
        self,
        offset: int = 0,
        limit: int = 50,
        keyword: str = "",
        access_token: str = None
    ) -> dict:
        """
        10. ITEM PROMOTION LIST API
        Mendapatkan daftar produk yang dipromosikan dalam live
        """
        try:
            token = access_token or self.access_token
            headers = {"Authorization": f"Bearer {token}"}
            
            params = {
                "offset": offset,
                "limit": limit,
                "kw": keyword
            }
            
            response = await self.client.get(
                f"{self.LIVE_API}/item/promotion",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting item promotion list: {e}")
            return {"items": []}

    async def get_item_promotion_by_id(
        self,
        promo_id: str,
        offset: int = 0,
        limit: int = 50,
        keyword: str = "",
        access_token: str = None
    ) -> dict:
        """
        11. ITEM PROMOTION BY ID API
        Mendapatkan detail produk promosi berdasarkan promo ID
        """
        try:
            token = access_token or self.access_token
            headers = {"Authorization": f"Bearer {token}"}
            
            params = {
                "offset": offset,
                "limit": limit,
                "kw": keyword
            }
            
            response = await self.client.get(
                f"{self.LIVE_API}/item/promotion/{promo_id}",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting item promotion by ID: {e}")
            raise

    # ==================== LIVE STATUS APIs ====================

    async def check_shop_live_ongoing(
        self,
        uid: str,
        access_token: str = None
    ) -> dict:
        """
        6. SHOP LIVE ONGOING API
        Mengecek status live ongoing dari shop berdasarkan UID
        """
        try:
            token = access_token or self.access_token
            headers = {"Authorization": f"Bearer {token}"}
            
            params = {"uid": uid}
            response = await self.client.get(
                f"{self.LIVE_API}/shop_page/live/ongoing",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error checking shop live ongoing: {e}")
            raise

    # ==================== CAMPAIGN/ADS APIs ====================

    async def get_campaign_expense_today(
        self,
        access_token: str = None
    ) -> dict:
        """
        17. GET CAMPAIGN EXPENSE TODAY API
        Mendapatkan data pengeluaran kampanye iklan hari ini
        """
        try:
            token = access_token or self.access_token
            headers = {"Authorization": f"Bearer {token}"}
            
            timestamp = int(datetime.utcnow().timestamp() * 1000)
            params = {"_": timestamp}
            
            response = await self.client.get(
                f"{self.SELLER_APP_API}/live_stream/get_campaign_expense_today/",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting campaign expense: {e}")
            raise

    async def get_ads_data(
        self,
        access_token: str = None
    ) -> dict:
        """
        21. GET ADS DATA API
        Mendapatkan data iklan meta
        """
        try:
            token = access_token or self.access_token
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await self.client.get(
                f"{self.SELLER_APP_API}/meta/get_ads_data/",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting ads data: {e}")
            raise

    # ==================== COIN/REWARDS APIs ====================

    async def coin_giveout(
        self,
        session_id: str,
        coin_data: dict,
        access_token: str = None
    ) -> dict:
        """
        18. COIN GIVEOUT API
        API untuk memberikan coin dalam live session
        """
        try:
            token = access_token or self.access_token
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                f"{self.LIVE_API}/session/{session_id}/coin/giveout",
                headers=headers,
                json=coin_data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error coin giveout: {e}")
            raise

    async def coin_start(
        self,
        session_id: str,
        coin_config: dict,
        access_token: str = None
    ) -> dict:
        """
        19. COIN START API
        Memulai pembagian coin dalam live session
        """
        try:
            token = access_token or self.access_token
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                f"{self.LIVE_API}/session/{session_id}/coin/start",
                headers=headers,
                json=coin_config
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error coin start: {e}")
            raise

    async def get_coin_reward_info(
        self,
        session_id: str,
        access_token: str = None
    ) -> dict:
        """
        20. COIN REWARD INFO API
        Mendapatkan informasi reward coin
        """
        try:
            token = access_token or self.access_token
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await self.client.get(
                f"{self.LIVE_API}/session/{session_id}/coin/rewardinfo",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting coin reward info: {e}")
            raise

    # ==================== URL BUILDERS ====================

    @staticmethod
    def get_shop_page_url(shop_name: str) -> str:
        """
        7. SHOP PAGE URL
        Build URL halaman toko shopee
        """
        return f"{ShopeeStreamingService.SHOPEE_MAIN}/{shop_name}"

    @staticmethod
    def get_product_url(shop_id: str, item_id: str) -> str:
        """
        12. PRODUCT URL
        Build URL produk shopee
        """
        return f"{ShopeeStreamingService.SHOPEE_MAIN}/product/{shop_id}/{item_id}"

    @staticmethod
    def get_live_share_link(session_id: str, share_user_id: str = "1") -> str:
        """
        9. LIVE SHARE LINK
        Build link untuk share live streaming
        """
        return f"http://live.shopee.co.id/share?from=live&session={session_id}&share_user_id={share_user_id}"

    @staticmethod
    def get_undrctrl_api(endpoint: str) -> str:
        """
        8. UNDRCTRL API V2
        Build UNDRCTRL API URL
        """
        return f"https://undrctrl.id/api/v2/{endpoint}"


# Initialize service
shopee_streaming_service = ShopeeStreamingService()
