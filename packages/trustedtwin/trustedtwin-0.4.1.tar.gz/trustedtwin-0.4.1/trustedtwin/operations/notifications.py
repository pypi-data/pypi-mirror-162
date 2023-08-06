"""Definition of Notifications access methods."""
import urllib.parse
from typing import TYPE_CHECKING, Dict, Any

from trustedtwin.misc import RESTMethod
from trustedtwin.models.responses import process_response

if TYPE_CHECKING:
    from trustedtwin.service import RestService


class NotificationsOperations:
    """Interfaces for accessing Notifications API operations"""

    def __init__(self, service: "RestService"):
        """Initialize object"""
        self._service = service
        self._http_client = self._service.http_client

    def webhook_subscribe(self, **kwargs: Any) -> Dict:
        """Execute webhook_subscribe API operation"""
        endpoint = "notifications/webhooks"
        endpoint = urllib.parse.quote(endpoint)

        body = {
            "callback_url": kwargs.get("callback_url"),
            "topic": kwargs.get("topic"),
            "user_secret": kwargs.get("user_secret"),
            "expires": kwargs.get("expires"),
        }
        body = {x: y for x, y in body.items() if y}

        resp = self._http_client.execute_request(
            method=RESTMethod.POST,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            body=body,
        )

        return process_response(resp, "webhook_subscribe", **self._service.kwargs)

    def webhook_unsubscribe(self, account: str, token: str) -> Dict:
        """Execute webhook_unsubscribe API operation"""
        endpoint = "notifications/webhooks/{account}".format(account=account)
        endpoint = urllib.parse.quote(endpoint)

        params = {"token": token}

        resp = self._http_client.execute_request(
            method=RESTMethod.DELETE,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            params=params,
        )

        return process_response(resp, "webhook_unsubscribe", **self._service.kwargs)

    def webhook_refresh_subscription(self, account: str, token: str) -> Dict:
        """Execute webhook_refresh_subscription API operation"""
        endpoint = "notifications/webhooks/{account}".format(account=account)
        endpoint = urllib.parse.quote(endpoint)

        params = {"token": token}

        resp = self._http_client.execute_request(
            method=RESTMethod.PATCH,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            params=params,
        )

        return process_response(
            resp, "webhook_refresh_subscription", **self._service.kwargs
        )

    def webhook_confirm_subscription(self, account: str, token: str) -> Dict:
        """Execute webhook_confirm_subscription API operation"""
        endpoint = "notifications/webhooks/{account}".format(account=account)
        endpoint = urllib.parse.quote(endpoint)

        params = {"token": token}

        resp = self._http_client.execute_request(
            method=RESTMethod.GET,
            url_root=self._http_client.host_name,
            endpoint=endpoint,
            params=params,
        )

        return process_response(
            resp, "webhook_confirm_subscription", **self._service.kwargs
        )
