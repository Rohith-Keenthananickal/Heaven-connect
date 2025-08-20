from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.property import (
    Property, Room, Facility, PropertyPhoto, Location, 
    Availability, PropertyAgreement, PhotoCategory
)
from app.models.user import User
from app.schemas.property import (
    PropertyProfileCreate, PropertyDocumentsCreate, RoomCreate, 
    FacilityCreate, LocationCreate, AvailabilityCreate, 
    PropertyAgreementCreate, PropertyOnboardingStatus
)


class PropertyService:
    @staticmethod
    def create_property_profile(db: Session, user_id: int, profile_data: PropertyProfileCreate) -> Property:
        """Create property profile (Step 1)"""
        # Check if property profile already exists
        existing_property = db.query(Property).filter(Property.id == user_id).first()
        if existing_property:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Property profile already exists"
            )
        
        # Create property profile
        property_obj = Property(
            id=user_id,
            property_name=profile_data.property_name,
            alternate_phone=profile_data.alternate_phone,
            progress_step=2  # Move to step 2
        )
        
        db.add(property_obj)
        db.commit()
        db.refresh(property_obj)
        return property_obj
    
    @staticmethod
    def update_property_documents(
        db: Session, 
        property_id: int, 
        documents_data: PropertyDocumentsCreate,
        id_proof_url: Optional[str] = None
    ) -> Property:
        """Update property documents (Step 2)"""
        property_obj = PropertyService.get_property_by_id(db, property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property profile not found"
            )
        
        property_obj.id_proof_type = documents_data.id_proof_type
        property_obj.certificate_number = documents_data.certificate_number
        property_obj.trade_license_number = documents_data.trade_license_number
        
        if id_proof_url:
            property_obj.id_proof_url = id_proof_url
        
        property_obj.progress_step = max(property_obj.progress_step, 3)  # Move to step 3
        
        db.commit()
        db.refresh(property_obj)
        return property_obj
    
    @staticmethod
    def add_room(db: Session, property_id: int, room_data: RoomCreate) -> Room:
        """Add room to property (Step 3)"""
        property_obj = PropertyService.get_property_by_id(db, property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property profile not found"
            )
        
        room = Room(
            property_id=property_id,
            room_type=room_data.room_type,
            count=room_data.count,
            amenities=room_data.amenities
        )
        
        db.add(room)
        
        # Update progress step if this is the first room
        if not property_obj.rooms:
            property_obj.progress_step = max(property_obj.progress_step, 4)
        
        db.commit()
        db.refresh(room)
        return room
    
    @staticmethod
    def add_facility(db: Session, property_id: int, facility_data: FacilityCreate) -> Facility:
        """Add facility to property (Step 4)"""
        property_obj = PropertyService.get_property_by_id(db, property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property profile not found"
            )
        
        facility = Facility(
            property_id=property_id,
            category=facility_data.category,
            details=facility_data.details
        )
        
        db.add(facility)
        
        # Update progress step if this is the first facility
        if not property_obj.facilities:
            property_obj.progress_step = max(property_obj.progress_step, 5)
        
        db.commit()
        db.refresh(facility)
        return facility
    
    @staticmethod
    def add_property_photo(
        db: Session, 
        property_id: int, 
        category: PhotoCategory, 
        image_url: str
    ) -> PropertyPhoto:
        """Add property photo (Step 5)"""
        property_obj = PropertyService.get_property_by_id(db, property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property profile not found"
            )
        
        photo = PropertyPhoto(
            property_id=property_id,
            category=category,
            image_url=image_url
        )
        
        db.add(photo)
        
        # Update progress step if this is the first photo
        if not property_obj.property_photos:
            property_obj.progress_step = max(property_obj.progress_step, 6)
        
        db.commit()
        db.refresh(photo)
        return photo
    
    @staticmethod
    def update_location(
        db: Session, 
        property_id: int, 
        location_data: LocationCreate
    ) -> Location:
        """Update property location (Step 6)"""
        property_obj = PropertyService.get_property_by_id(db, property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property profile not found"
            )
        
        # Check if location already exists
        existing_location = db.query(Location).filter(Location.property_id == property_id).first()
        
        if existing_location:
            # Update existing location
            existing_location.address = location_data.address
            existing_location.google_map_link = location_data.google_map_link
            existing_location.floor = location_data.floor
            existing_location.elderly_friendly = location_data.elderly_friendly
            db.commit()
            db.refresh(existing_location)
            location = existing_location
        else:
            # Create new location
            location = Location(
                property_id=property_id,
                address=location_data.address,
                google_map_link=location_data.google_map_link,
                floor=location_data.floor,
                elderly_friendly=location_data.elderly_friendly
            )
            db.add(location)
            db.commit()
            db.refresh(location)
        
        # Update progress step
        property_obj.progress_step = max(property_obj.progress_step, 7)
        db.commit()
        
        return location
    
    @staticmethod
    def add_availability(
        db: Session, 
        property_id: int, 
        availability_data: AvailabilityCreate
    ) -> Availability:
        """Add property availability (Step 7)"""
        property_obj = PropertyService.get_property_by_id(db, property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property profile not found"
            )
        
        availability = Availability(
            property_id=property_id,
            available_from=availability_data.available_from,
            available_to=availability_data.available_to,
            is_blocked=availability_data.is_blocked
        )
        
        db.add(availability)
        
        # Update progress step if this is the first availability
        if not property_obj.availability:
            property_obj.progress_step = max(property_obj.progress_step, 8)
        
        db.commit()
        db.refresh(availability)
        return availability
    
    @staticmethod
    def create_property_agreement(
        db: Session, 
        property_id: int, 
        agreement_data: PropertyAgreementCreate
    ) -> PropertyAgreement:
        """Create property agreement (Step 8)"""
        property_obj = PropertyService.get_property_by_id(db, property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property profile not found"
            )
        
        # Check if agreement already exists
        existing_agreement = db.query(PropertyAgreement).filter(PropertyAgreement.property_id == property_id).first()
        if existing_agreement:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Property agreement already exists"
            )
        
        agreement = PropertyAgreement(
            property_id=property_id,
            owns_property=agreement_data.owns_property,
            agreed_to_rules=agreement_data.agreed_to_rules,
            allow_verification=agreement_data.allow_verification,
            payout_after_checkout=agreement_data.payout_after_checkout
        )
        
        db.add(agreement)
        
        # Update progress step to final step
        property_obj.progress_step = 9
        
        db.commit()
        db.refresh(agreement)
        return agreement
    
    @staticmethod
    def get_property_by_id(db: Session, property_id: int) -> Optional[Property]:
        """Get property by ID with all relationships"""
        return db.query(Property).options(
            joinedload(Property.rooms),
            joinedload(Property.facilities),
            joinedload(Property.property_photos),
            joinedload(Property.location),
            joinedload(Property.availability),
            joinedload(Property.agreements)
        ).filter(Property.id == property_id).first()
    
    @staticmethod
    def get_all_properties(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        verified_only: Optional[bool] = None
    ) -> List[Property]:
        """Get all properties with pagination and filters"""
        query = db.query(Property)
        
        if verified_only is not None:
            query = query.filter(Property.is_verified == verified_only)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_properties_by_coordinator(db: Session, coordinator_id: int) -> List[Property]:
        """Get all properties assigned to a specific coordinator"""
        return db.query(Property).filter(Property.area_coordinator_id == coordinator_id).all()
    
    @staticmethod
    def assign_coordinator(db: Session, property_id: int, coordinator_id: int) -> Property:
        """Assign area coordinator to property"""
        property_obj = PropertyService.get_property_by_id(db, property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property profile not found"
            )
        
        # Verify coordinator exists and is admin type
        coordinator = db.query(User).filter(User.id == coordinator_id, User.user_type == "admin").first()
        if not coordinator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coordinator not found or not authorized"
            )
        
        property_obj.area_coordinator_id = coordinator_id
        db.commit()
        db.refresh(property_obj)
        return property_obj
    
    @staticmethod
    def verify_property(db: Session, property_id: int) -> Property:
        """Verify property profile"""
        property_obj = PropertyService.get_property_by_id(db, property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property profile not found"
            )
        
        if property_obj.progress_step < 9:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Property onboarding not complete"
            )
        
        property_obj.is_verified = True
        db.commit()
        db.refresh(property_obj)
        return property_obj
    
    @staticmethod
    def get_onboarding_status(db: Session, property_id: int) -> PropertyOnboardingStatus:
        """Get property onboarding status"""
        property_obj = PropertyService.get_property_by_id(db, property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property profile not found"
            )
        
        # Define all steps
        all_steps = {
            "profile_created": property_obj.progress_step >= 1,
            "documents_uploaded": property_obj.progress_step >= 2,
            "rooms_added": property_obj.progress_step >= 3,
            "facilities_added": property_obj.progress_step >= 4,
            "photos_uploaded": property_obj.progress_step >= 5,
            "location_set": property_obj.progress_step >= 6,
            "availability_set": property_obj.progress_step >= 7,
            "agreement_signed": property_obj.progress_step >= 8,
            "onboarding_complete": property_obj.progress_step >= 9
        }
        
        return PropertyOnboardingStatus(
            user_id=property_obj.id,
            property_id=property_obj.id,
            progress_step=property_obj.progress_step,
            is_verified=property_obj.is_verified,
            completed_steps=all_steps
        ) 