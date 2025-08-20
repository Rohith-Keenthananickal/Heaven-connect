from .users import router as users_router
from .otp_verifications import router as otp_router
from .properties import router as properties_router
from .rooms import router as rooms_router
from .facilities import router as facilities_router
from .property_photos import router as property_photos_router
from .location import router as location_router
from .availability import router as availability_router
from .property_agreements import router as property_agreements_router

__all__ = [
    "users_router",
    "otp_router", 
    "properties_router",
    "rooms_router",
    "facilities_router", 
    "property_photos_router",
    "location_router",
    "availability_router",
    "property_agreements_router"
]
