"""
Shopee API Integration Service
Handles OAuth, token refresh, order sync, and campaign data sync
"""

import httpx
import logging
from datetime import datetime, timedelta
from app.config import settings

logger = logging.getLogger(__name__)


class ShopeeAPIService:
    """Service to interact with Shopee Partner API"""

    BASE_URL = settings.shopee_api_base_url
    PARTNER_ID = settings.shopee_partner_id
    PARTNER_KEY = settings.shopee_partner_key

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def get_authorization_url(self, redirect_uri: str) -> str:
        """
        Generate Shopee OAuth authorization URL
        User should visit this URL to authorize the app
        """
        params = {
            "client_id": self.PARTNER_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": "random_state",
        }
        auth_url = f"{self.BASE_URL}/shop/auth_partner"
        return f"{auth_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

    async def exchange_code_for_token(self, code: str) -> dict:
        """
        Exchange authorization code for access token
        This should be called after user authorizes the app
        """
        try:
            payload = {
                "partner_id": self.PARTNER_ID,
                "partner_key": self.PARTNER_KEY,
                "code": code,
            }

            response = await self.client.post(
                f"{self.BASE_URL}/auth/token/get",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "access_token": data.get("access_token"),
                "refresh_token": data.get("refresh_token"),
                "expire_in": data.get("expire_in"),
                "shop_id": data.get("shop_id"),
            }
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token
        """
        try:
            payload = {
                "partner_id": self.PARTNER_ID,
                "partner_key": self.PARTNER_KEY,
                "refresh_token": refresh_token,
            }

            response = await self.client.post(
                f"{self.BASE_URL}/auth/token/refresh",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "access_token": data.get("access_token"),
                "refresh_token": data.get("refresh_token"),
                "expire_in": data.get("expire_in"),
            }
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise

    async def get_shop_info(self, access_token: str, shop_id: int) -> dict:
        """
        Get shop information
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await self.client.get(
                f"{self.BASE_URL}/shop/get_profile",
                headers=headers,
                params={"shop_id": shop_id},
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting shop info: {e}")
            raise

    async def get_orders(
        self,
        access_token: str,
        shop_id: int,
        date_from: datetime = None,
        date_to: datetime = None,
    ) -> list:
        """
        Get orders for a shop within a date range
        """
        try:
            if not date_from:
                date_from = datetime.utcnow() - timedelta(days=30)
            if not date_to:
                date_to = datetime.utcnow()

            headers = {"Authorization": f"Bearer {access_token}"}
            params = {
                "shop_id": shop_id,
                "time_range_field": "create_time",
                "time_from": int(date_from.timestamp()),
                "time_to": int(date_to.timestamp()),
                "pagination_entries_per_page": 100,
            }

            response = await self.client.get(
                f"{self.BASE_URL}/order/orders/get",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", {}).get("orders", [])
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []

    async def get_campaigns(
        self,
        access_token: str,
        shop_id: int,
    ) -> list:
        """
        Get advertising campaigns for a shop
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            params = {"shop_id": shop_id}

            response = await self.client.get(
                f"{self.BASE_URL}/campaign/get_campaigns",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", [])
        except Exception as e:
            logger.error(f"Error getting campaigns: {e}")
            return []

    async def sync_orders(
        self,
        db,
        account_id: int,
        access_token: str,
        shop_id: int,
    ) -> dict:
        """
        Sync orders from Shopee to database
        """
        from app.models.order import Order
        from app.models.shopee_account import ShopeeAccount

        try:
            orders = await self.get_orders(access_token, shop_id)

            created = 0
            updated = 0

            for order in orders:
                order_id = order.get("order_id")
                existing = db.query(Order).filter(Order.order_id == str(order_id)).first()

                if not existing:
                    db_order = Order(
                        shopee_account_id=account_id,
                        order_id=str(order_id),
                        total_amount=order.get("total_amount", 0),
                        status="completed",
                        date=datetime.fromtimestamp(order.get("create_time", 0)),
                    )
                    db.add(db_order)
                    created += 1
                else:
                    existing.total_amount = order.get("total_amount", 0)
                    updated += 1

            db.commit()
            logger.info(f"Synced {created} new orders, updated {updated} existing")

            return {"created": created, "updated": updated}
        except Exception as e:
            logger.error(f"Error syncing orders: {e}")
            db.rollback()
            raise


# Initialize service
shopee_service = ShopeeAPIService()
