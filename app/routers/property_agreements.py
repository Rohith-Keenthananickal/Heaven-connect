from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.property_agreements import PropertyAgreementCreate, PropertyAgreementUpdate, PropertyAgreementResponse, PropertyAgreementListResponse
from app.services.property_service import PropertyService


router = APIRouter(prefix="/property-agreements", tags=["Property Agreements"])


@router.post("/", response_model=PropertyAgreementResponse, status_code=status.HTTP_201_CREATED)
async def create_property_agreement(
    agreement: PropertyAgreementCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Create a new property agreement"""
    try:
        # Convert AsyncSession to Session for PropertyService
        from sqlalchemy.orm import Session
        session = Session(bind=db.bind)
        try:
            property_agreement = PropertyService.create_property_agreement(session, agreement.property_id, agreement)
            return property_agreement
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[PropertyAgreementResponse])
async def get_property_agreements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_id: int = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get property agreements with pagination and filters"""
    try:
        # Convert AsyncSession to Session for PropertyService
        from sqlalchemy.orm import Session
        session = Session(bind=db.bind)
        try:
            if property_id:
                property_obj = PropertyService.get_property_by_id(session, property_id)
                if property_obj and property_obj.agreements:
                    return [property_obj.agreements]
                return []
            else:
                # Get all properties and their agreements
                properties = PropertyService.get_all_properties(session, skip=skip, limit=limit)
                agreements = []
                for prop in properties:
                    if prop.agreements:
                        agreements.append(prop.agreements)
                return agreements
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{agreement_id}", response_model=PropertyAgreementResponse)
async def get_property_agreement(agreement_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific property agreement by ID"""
    try:
        # Convert AsyncSession to Session for PropertyService
        from sqlalchemy.orm import Session
        session = Session(bind=db.bind)
        try:
            # Search through all properties to find the agreement
            properties = PropertyService.get_all_properties(session, skip=0, limit=1000)
            for prop in properties:
                if prop.agreements and prop.agreements.id == agreement_id:
                    return prop.agreements
            
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property agreement not found")
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{agreement_id}", response_model=PropertyAgreementResponse)
async def update_property_agreement(
    agreement_id: int, 
    agreement_update: PropertyAgreementUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update a property agreement"""
    try:
        # Convert AsyncSession to Session for PropertyService
        from sqlalchemy.orm import Session
        session = Session(bind=db.bind)
        try:
            # Search through all properties to find the agreement
            properties = PropertyService.get_all_properties(session, skip=0, limit=1000)
            for prop in properties:
                if prop.agreements and prop.agreements.id == agreement_id:
                    # Update the agreement
                    if agreement_update.owns_property is not None:
                        prop.agreements.owns_property = agreement_update.owns_property
                    if agreement_update.agreed_to_rules is not None:
                        prop.agreements.agreed_to_rules = agreement_update.agreed_to_rules
                    if agreement_update.allow_verification is not None:
                        prop.agreements.allow_verification = agreement_update.allow_verification
                    if agreement_update.payout_after_checkout is not None:
                        prop.agreements.payout_after_checkout = agreement_update.payout_after_checkout
                    
                    session.commit()
                    session.refresh(prop.agreements)
                    return prop.agreements
            
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property agreement not found")
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{agreement_id}")
async def delete_property_agreement(agreement_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a property agreement"""
    try:
        # Convert AsyncSession to Session for PropertyService
        from sqlalchemy.orm import Session
        session = Session(bind=db.bind)
        try:
            # Search through all properties to find the agreement
            properties = PropertyService.get_all_properties(session, skip=0, limit=1000)
            for prop in properties:
                if prop.agreements and prop.agreements.id == agreement_id:
                    session.delete(prop.agreements)
                    prop.agreements = None
                    prop.progress_step = 8  # Reset to step 8
                    session.commit()
                    return {"status": "success", "data": {"message": "Property agreement deleted successfully"}}
            
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property agreement not found")
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 