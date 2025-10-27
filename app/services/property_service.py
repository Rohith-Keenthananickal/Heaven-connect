from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_, or_
from fastapi import HTTPException, status
from datetime import datetime
from app.models.property import (
    Property, Room, Facility, PropertyPhoto, Location, 
    Availability, PropertyAgreement, PropertyApproval, PhotoCategory, PropertyType, PropertyStatus, 
    VerificationStatus, PropertyVerificationStatus
)
from app.models.user import User
from app.schemas.property import (
    PropertyProfileCreate, PropertyDocumentsCreate, RoomCreate, 
    FacilityCreate, LocationCreate, AvailabilityCreate, 
    PropertyAgreementCreate, PropertyOnboardingStatus, PropertyTypeCreate, PropertyTypeUpdate
)
from app.utils.error_handler import create_server_error_http_exception


class PropertyTypeService:
    @staticmethod
    def create_property_type(db: Session, type_data: PropertyTypeCreate) -> PropertyType:
        """Create a new property type"""
        # Check if property type already exists
        existing_type = db.query(PropertyType).filter(PropertyType.name == type_data.name).first()
        if existing_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Property type already exists"
            )
        
        property_type = PropertyType(
            name=type_data.name,
            description=type_data.description,
            is_active=type_data.is_active
        )
        
        db.add(property_type)
        db.commit()
        db.refresh(property_type)
        return property_type
    
    @staticmethod
    def get_property_type_by_id(db: Session, type_id: int) -> Optional[PropertyType]:
        """Get property type by ID"""
        return db.query(PropertyType).filter(PropertyType.id == type_id).first()
    
    @staticmethod
    def get_all_property_types(db: Session, active_only: bool = True) -> List[PropertyType]:
        """Get all property types"""
        query = db.query(PropertyType)
        if active_only:
            query = query.filter(PropertyType.is_active == True)
        return query.all()
    
    @staticmethod
    def update_property_type(db: Session, type_id: int, type_data: PropertyTypeUpdate) -> PropertyType:
        """Update property type"""
        property_type = PropertyTypeService.get_property_type_by_id(db, type_id)
        if not property_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property type not found"
            )
        
        if type_data.name is not None:
            # Check if new name conflicts with existing
            existing_type = db.query(PropertyType).filter(
                PropertyType.name == type_data.name,
                PropertyType.id != type_id
            ).first()
            if existing_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Property type name already exists"
                )
            property_type.name = type_data.name
        
        if type_data.description is not None:
            property_type.description = type_data.description
        
        if type_data.is_active is not None:
            property_type.is_active = type_data.is_active
        
        db.commit()
        db.refresh(property_type)
        return property_type
    
    @staticmethod
    def delete_property_type(db: Session, type_id: int) -> bool:
        """Delete property type (soft delete by setting is_active to False)"""
        property_type = PropertyTypeService.get_property_type_by_id(db, type_id)
        if not property_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property type not found"
            )
        
        # Check if any properties are using this type
        properties_using_type = db.query(Property).filter(Property.property_type_id == type_id).first()
        if properties_using_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete property type as it is being used by properties"
            )
        
        property_type.is_active = False
        db.commit()
        return True


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
            property_type_id=profile_data.property_type_id,
            id_proof_type=profile_data.id_proof_type,
            id_proof_url=profile_data.id_proof_url,
            certificate_number=profile_data.certificate_number,
            tourism_certificate_number=profile_data.tourism_certificate_number,
            tourism_certificate_issued_by=profile_data.tourism_certificate_issued_by,
            tourism_certificate_photos=profile_data.tourism_certificate_photos,
            trade_license_number=profile_data.trade_license_number,
            trade_license_images=profile_data.trade_license_images,
            # Property image fields
            cover_image=profile_data.cover_image,
            exterior_images=profile_data.exterior_images,
            bedroom_images=profile_data.bedroom_images,
            bathroom_images=profile_data.bathroom_images,
            living_dining_images=profile_data.living_dining_images,
            status=profile_data.status,
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
    
    @staticmethod
    def search_properties(db: Session, search_request) -> dict:
        """Search properties with pagination and filters"""
        try:
            # Build base query with joins for property type
            query = db.query(Property).join(Property.property_type, isouter=True)
            filters = []
            
            # Apply user ID filter
            if search_request.user_id:
                filters.append(Property.user_id == search_request.user_id)
            
            # Apply property type ID filter (array support)
            if search_request.property_type_id:
                if len(search_request.property_type_id) == 1:
                    filters.append(Property.property_type_id == search_request.property_type_id[0])
                else:
                    filters.append(Property.property_type_id.in_(search_request.property_type_id))
            
            # Apply property type name filter (array support)
            if search_request.property_type_name:
                if len(search_request.property_type_name) == 1:
                    filters.append(PropertyType.name == search_request.property_type_name[0])
                else:
                    filters.append(PropertyType.name.in_(search_request.property_type_name))
            
            # Apply status filter (array support)
            if search_request.status:
                if len(search_request.status) == 1:
                    filters.append(Property.status == search_request.status[0])
                else:
                    filters.append(Property.status.in_(search_request.status))
            
            # Apply date filter
            if search_request.date_filter:
                if search_request.date_filter.from_date:
                    from_date = datetime.fromtimestamp(search_request.date_filter.from_date / 1000)
                    filters.append(Property.created_at >= from_date)
                
                if search_request.date_filter.to_date:
                    to_date = datetime.fromtimestamp(search_request.date_filter.to_date / 1000)
                    filters.append(Property.created_at <= to_date)
            
            # Apply search query filter
            if search_request.search_query:
                search_term = f"%{search_request.search_query}%"
                filters.append(Property.property_name.ilike(search_term))
            
            # Apply all filters
            if filters:
                query = query.filter(and_(*filters))
            
            # Order by created_at desc BEFORE pagination
            query = query.order_by(Property.created_at.desc())
            
            # Get total count for pagination
            total = query.count()
            
            # Calculate pagination
            total_pages = (total + search_request.limit - 1) // search_request.limit
            skip = (search_request.page - 1) * search_request.limit
            
            # Apply pagination AFTER ordering
            query = query.offset(skip).limit(search_request.limit)
            
            # Execute query
            properties = query.all()
            
            # Build pagination info
            pagination_info = {
                "page": search_request.page,
                "limit": search_request.limit,
                "total": total,
                "total_pages": total_pages,
                "has_next": search_request.page < total_pages,
                "has_prev": search_request.page > 1
            }
            
            return {
                "properties": properties,
                "pagination": pagination_info
            }
            
        except Exception as e:
            raise create_server_error_http_exception(
                message=f"Property search failed: {str(e)}",
                component="property_search"
            )

    @staticmethod
    def activate_property(db: Session, property_id: int) -> Optional[Property]:
        """Activate property by changing status to ACTIVE"""
        try:
            property_obj = db.query(Property).filter(Property.id == property_id).first()
            if not property_obj:
                return None
            
            # Change status to ACTIVE
            property_obj.status = PropertyStatus.ACTIVE
            db.commit()
            db.refresh(property_obj)
            return property_obj
            
        except Exception as e:
            db.rollback()
            raise create_server_error_http_exception(
                message=f"Failed to activate property: {str(e)}",
                component="property_activate"
            )

    @staticmethod
    def deactivate_property(db: Session, property_id: int) -> Optional[Property]:
        """Deactivate property by changing status to INACTIVE"""
        try:
            property_obj = db.query(Property).filter(Property.id == property_id).first()
            if not property_obj:
                return None
            
            # Change status to INACTIVE
            property_obj.status = PropertyStatus.INACTIVE
            db.commit()
            db.refresh(property_obj)
            return property_obj
            
        except Exception as e:
            db.rollback()
            raise create_server_error_http_exception(
                message=f"Failed to deactivate property: {str(e)}",
                component="property_deactivate"
            )

    @staticmethod
    def block_property(db: Session, property_id: int) -> Optional[Property]:
        """Block property by changing status to BLOCKED"""
        try:
            property_obj = db.query(Property).filter(Property.id == property_id).first()
            if not property_obj:
                return None
            
            # Change status to BLOCKED
            property_obj.status = PropertyStatus.BLOCKED
            db.commit()
            db.refresh(property_obj)
            return property_obj
            
        except Exception as e:
            db.rollback()
            raise create_server_error_http_exception(
                message=f"Failed to block property: {str(e)}",
                component="property_block"
            )

    @staticmethod
    def soft_delete_property(db: Session, property_id: int) -> Optional[Property]:
        """Soft delete property by changing status to DELETED"""
        try:
            property_obj = db.query(Property).filter(Property.id == property_id).first()
            if not property_obj:
                return None
            
            # Change status to DELETED
            property_obj.status = PropertyStatus.DELETED
            db.commit()
            db.refresh(property_obj)
            return property_obj
            
        except Exception as e:
            db.rollback()
            raise create_server_error_http_exception(
                message=f"Failed to delete property: {str(e)}",
                component="property_soft_delete"
            )

    @staticmethod
    def update_property_images(
        db: Session, 
        property_id: int, 
        cover_image: Optional[str] = None,
        exterior_images: Optional[List[str]] = None,
        bedroom_images: Optional[List[str]] = None,
        bathroom_images: Optional[List[str]] = None,
        living_dining_images: Optional[List[str]] = None
    ) -> Optional[Property]:
        """Update property images"""
        try:
            property_obj = db.query(Property).filter(Property.id == property_id).first()
            if not property_obj:
                return None
            
            # Update image fields if provided
            if cover_image is not None:
                property_obj.cover_image = cover_image
            if exterior_images is not None:
                property_obj.exterior_images = exterior_images
            if bedroom_images is not None:
                property_obj.bedroom_images = bedroom_images
            if bathroom_images is not None:
                property_obj.bathroom_images = bathroom_images
            if living_dining_images is not None:
                property_obj.living_dining_images = living_dining_images
            
            db.commit()
            db.refresh(property_obj)
            return property_obj
            
        except Exception as e:
            db.rollback()
            raise create_server_error_http_exception(
                message=f"Failed to update property images: {str(e)}",
                component="property_images_update"
            )

    @staticmethod
    def create_property_approval(
        db: Session,
        property_id: int,
        atp_id: int,
        approval_type: str,
        verification_type: str,
        note: Optional[str] = None
    ) -> PropertyApproval:
        """Create a property approval/rejection record by ATP"""
        try:
            # Verify that the property exists
            property_obj = db.query(Property).filter(Property.id == property_id).first()
            if not property_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Property not found"
                )
            
            # Verify that the ATP exists and is an area coordinator
            atp = db.query(User).filter(User.id == atp_id).first()
            if not atp:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="ATP not found"
                )
            
            # Convert verification_type string to enum
            try:
                verification_status = VerificationStatus[verification_type]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid verification_type. Must be one of: {[e.name for e in VerificationStatus]}"
                )
            
            # Create the approval record
            approval = PropertyApproval(
                property_id=property_id,
                atp_id=atp_id,
                approval_type=approval_type,
                verification_type=verification_status,
                note=note
            )
            
            db.add(approval)
            
            # If verification_type is REJECTED, update property verification_status to REJECTED
            if verification_status == VerificationStatus.REJECTED:
                property_obj.verification_status = PropertyVerificationStatus.REJECTED
            else:
                # If APPROVED, check if all required approvals are done
                # This logic can be enhanced based on business requirements
                pass
            
            db.commit()
            db.refresh(approval)
            
            return approval
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise create_server_error_http_exception(
                message=f"Failed to create property approval: {str(e)}",
                component="property_approval_create"
            )

    @staticmethod
    def get_property_approvals(db: Session, property_id: int) -> List[PropertyApproval]:
        """Get all approvals for a specific property"""
        try:
            # Verify that the property exists
            property_obj = db.query(Property).filter(Property.id == property_id).first()
            if not property_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Property not found"
                )
            
            # Get all approvals for this property, ordered by created_at descending
            approvals = db.query(PropertyApproval).filter(
                PropertyApproval.property_id == property_id
            ).order_by(PropertyApproval.created_at.desc()).all()
            
            return approvals
            
        except HTTPException:
            raise
        except Exception as e:
            raise create_server_error_http_exception(
                message=f"Failed to get property approvals: {str(e)}",
                component="property_approvals_get"
            )
    
    @staticmethod
    def update_property_verification_status(
        db: Session,
        property_id: int,
        verification_status: PropertyVerificationStatus
    ) -> Property:
        """Update property verification status (DRAFT, PENDING, APPROVED, REJECTED)"""
        try:
            property_obj = db.query(Property).filter(Property.id == property_id).first()
            if not property_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Property not found"
                )
            
            property_obj.verification_status = verification_status
            
            # If status is APPROVED, mark as verified
            if verification_status == PropertyVerificationStatus.APPROVED:
                property_obj.is_verified = True
            
            db.commit()
            db.refresh(property_obj)
            return property_obj
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise create_server_error_http_exception(
                message=f"Failed to update property verification status: {str(e)}",
                component="property_verification_status_update"
            ) 