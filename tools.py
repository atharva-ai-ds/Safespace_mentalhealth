"""Safety tools. Twilio is disabled unless all required environment variables are configured."""
from __future__ import annotations

import logging

from twilio.base.exceptions import TwilioException
from twilio.rest import Client

from backend.config import EMERGENCY_CONTACT, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER

logger = logging.getLogger(__name__)


def call_emergency(message: str) -> str:
    if not all((TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, EMERGENCY_CONTACT)):
        return "Emergency contact is not configured. Please call local emergency services now if there is immediate danger."
    try:
        call = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN).calls.create(
            to=EMERGENCY_CONTACT, from_=TWILIO_FROM_NUMBER, url="http://demo.twilio.com/docs/voice.xml"
        )
        logger.warning("Emergency call placed: %s", call.sid)
        return "An emergency contact call has been initiated."
    except TwilioException:
        logger.exception("Twilio emergency call failed")
        return "I could not place the emergency call. Please call local emergency services now if there is immediate danger."


def find_nearby_therapists(location: str) -> list[dict[str, str]]:
    place = location.strip() or "your area"
    return [
        {"name": "SafeMind Counseling", "location": place, "phone": "+1 (555) 010-1001"},
        {"name": "Harbor Wellness Clinic", "location": place, "phone": "+1 (555) 010-1002"},
        {"name": "Community Mental Health Center", "location": place, "phone": "+1 (555) 010-1003"},
    ]
