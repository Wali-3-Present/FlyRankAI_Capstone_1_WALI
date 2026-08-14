import httpx
import logging

logger = logging.getLogger("uvicorn.error")

async def enrich_ip_location(ip: str) -> dict:
    """
    Fallback Chain for IP Geo Enrichment:
    Provider A (ip-api.com) -> Provider B (ipapi.co) -> Graceful Fallback
    """
    # Ignore local/private IPs in dev
    if not ip or ip in ("127.0.0.1", "localhost", "::1"):
        return {"country": "Local", "city": "Development"}

    # Provider A: ip-api.com
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"http://ip-api.com/json/{ip}")
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "success":
                    return {"country": data.get("country", "Unknown"), "city": data.get("city", "Unknown")}
    except Exception as e:
        logger.warning(f"Geo Provider A failed: {str(e)}")

    # Provider B (Fallback): ipapi.co
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"https://ipapi.co/{ip}/json/")
            if res.status_code == 200:
                data = res.json()
                return {"country": data.get("country_name", "Unknown"), "city": data.get("city", "Unknown")}
    except Exception as e:
        logger.warning(f"Geo Provider B failed: {str(e)}")

    # Graceful degradation if both providers are down
    return {"country": "Unknown", "city": "Unknown"}

async def trigger_safe_side_effects(submission_id: str, email: str):
    """
    Safe side effect operation (Email/Webhook).
    Exceptions must NOT block main submission flow[cite: 1].
    """
    try:
        logger.info(f"[SIDE-EFFECT] Sending confirmation email for submission {submission_id} to {email}...")
        # Simulate potential notification failure scenario
        if "fail" in email:
            raise RuntimeError("SMTP connection timeout simulation")
        logger.info(f"[SIDE-EFFECT SUCCESS] Email dispatched to {email}")
    except Exception as e:
        logger.error(f"[SIDE-EFFECT NON-BLOCKING FAILURE] {str(e)}")