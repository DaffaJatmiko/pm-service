"""BSC (Balanced Scorecard) API endpoints for Performance Management System."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from decimal import Decimal
import pandas as pd
import io

from src.schemas.base import DataResponse, PaginatedResponse
from src.schemas.bsc import (
    BSCIndicatorCreate,
    BSCIndicatorUpdate,
    BSCIndicatorResponse,
    BSCActualCreate,
    BSCActualUpdate,
    BSCActualResponse,
    BSCQueryParams,
    BSCDashboardResponse,
    BSCBulkImport,
    BSCBulkImportItem,
    BSCPerspective,
    BSCUOM,
    BSCCategory,
    BSCCalculation
)
from src.services.bsc import BSCIndicatorService, BSCActualService
from src.auth.dependencies import get_current_user, get_current_active_user, check_user_role

router = APIRouter(prefix="/bsc", tags=["bsc"])


# BSC Indicator endpoints
@router.post(
    "/indicators", 
    response_model=DataResponse[BSCIndicatorResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new BSC indicator",
    description="Create a new BSC indicator with the given details."
)
async def create_indicator(
    indicator_in: BSCIndicatorCreate,
    current_user: dict = Depends(get_current_active_user),
    indicator_service: BSCIndicatorService = Depends()
):
    """Create a new BSC indicator."""
    try:
        indicator = await indicator_service.create_indicator(
            indicator_in=indicator_in, 
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=indicator, message="BSC indicator created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the BSC indicator: {str(e)}"
        )


@router.get(
    "/indicators", 
    response_model=PaginatedResponse[BSCIndicatorResponse],
    summary="Get all BSC indicators",
    description="Get a list of all BSC indicators with optional filtering and pagination."
)
async def get_indicators(
    query_params: BSCQueryParams = Depends(),
    current_user: dict = Depends(get_current_user),
    indicator_service: BSCIndicatorService = Depends()
):
    """Get all BSC indicators with optional filtering."""
    try:
        result = await indicator_service.search_indicators(
            perspective=query_params.perspective,
            period_id=query_params.period_id,
            code=query_params.code,
            is_active=query_params.is_active,
            page=query_params.page,
            page_size=query_params.page_size
        )
        
        return PaginatedResponse(
            data=result["data"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"],
            message="BSC indicators retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving BSC indicators: {str(e)}"
        )


@router.get(
    "/indicators/{indicator_id}", 
    response_model=DataResponse[BSCIndicatorResponse],
    summary="Get a BSC indicator by ID",
    description="Get details of a specific BSC indicator by its ID."
)
async def get_indicator(
    indicator_id: UUID,
    current_user: dict = Depends(get_current_user),
    indicator_service: BSCIndicatorService = Depends()
):
    """Get a BSC indicator by ID."""
    try:
        indicator = await indicator_service.get_or_404(id=indicator_id)
        return DataResponse(data=indicator, message="BSC indicator retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the BSC indicator: {str(e)}"
        )


@router.get(
    "/indicators/{indicator_id}/actuals", 
    response_model=DataResponse[dict],
    summary="Get a BSC indicator with actuals",
    description="Get a BSC indicator with its actual values."
)
async def get_indicator_with_actuals(
    indicator_id: UUID,
    current_user: dict = Depends(get_current_user),
    indicator_service: BSCIndicatorService = Depends()
):
    """Get a BSC indicator with its actuals."""
    try:
        result = await indicator_service.get_indicator_with_actuals(indicator_id=indicator_id)
        return DataResponse(data=result, message="BSC indicator with actuals retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the BSC indicator with actuals: {str(e)}"
        )


@router.patch(
    "/indicators/{indicator_id}", 
    response_model=DataResponse[BSCIndicatorResponse],
    summary="Update a BSC indicator",
    description="Update details of a specific BSC indicator by its ID."
)
async def update_indicator(
    indicator_id: UUID,
    indicator_in: BSCIndicatorUpdate,
    current_user: dict = Depends(get_current_active_user),
    indicator_service: BSCIndicatorService = Depends()
):
    """Update a BSC indicator."""
    try:
        indicator = await indicator_service.update_indicator(
            indicator_id=indicator_id, 
            indicator_in=indicator_in,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=indicator, message="BSC indicator updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the BSC indicator: {str(e)}"
        )


@router.delete(
    "/indicators/{indicator_id}", 
    response_model=DataResponse[BSCIndicatorResponse],
    summary="Delete a BSC indicator",
    description="Delete a BSC indicator by its ID (soft delete)."
)
async def delete_indicator(
    indicator_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    indicator_service: BSCIndicatorService = Depends()
):
    """Delete a BSC indicator (soft delete)."""
    try:
        indicator = await indicator_service.delete(
            id=indicator_id,
            soft_delete=True,
            deleted_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=indicator, message="BSC indicator deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the BSC indicator: {str(e)}"
        )


@router.get(
    "/dashboard/{period_id}", 
    response_model=DataResponse[BSCDashboardResponse],
    summary="Get BSC dashboard data",
    description="Get BSC dashboard data for a specific period, grouped by perspective."
)
async def get_bsc_dashboard(
    period_id: UUID,
    current_user: dict = Depends(get_current_user),
    indicator_service: BSCIndicatorService = Depends()
):
    """Get BSC dashboard data."""
    try:
        result = await indicator_service.get_bsc_dashboard(period_id=period_id)
        return DataResponse(data=result, message="BSC dashboard data retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving BSC dashboard data: {str(e)}"
        )


@router.post(
    "/indicators/bulk", 
    response_model=DataResponse[List[BSCIndicatorResponse]],
    status_code=status.HTTP_201_CREATED,
    summary="Bulk import BSC indicators",
    description="Import multiple BSC indicators at once."
)
async def bulk_import_indicators(
    bulk_import: BSCBulkImport,
    current_user: dict = Depends(get_current_active_user),
    indicator_service: BSCIndicatorService = Depends()
):
    """Bulk import BSC indicators."""
    try:
        indicators = await indicator_service.bulk_import_indicators(
            bulk_import=bulk_import,
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(
            data=indicators, 
            message=f"{len(indicators)} BSC indicators imported successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while importing BSC indicators: {str(e)}"
        )


@router.post(
    "/indicators/upload", 
    response_model=DataResponse[List[BSCIndicatorResponse]],
    status_code=status.HTTP_201_CREATED,
    summary="Upload BSC indicators from Excel",
    description="Upload and import BSC indicators from an Excel file."
)
async def upload_indicators(
    period_id: UUID,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_active_user),
    indicator_service: BSCIndicatorService = Depends()
):
    """Upload BSC indicators from Excel file."""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are supported"
        )
    
    try:
        # Read Excel file
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Required columns for the Excel file (matching frontend structure)
        required_columns = [
            "Perspective", "Code", "KPI", "KPI Definition", 
            "Weight", "UOM", "Category", "Calculation", "Target", "Related PIC"
        ]
        
        # Check if required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Transform Excel data to BSCBulkImport format
        indicators = []
        for _, row in df.iterrows():
            try:
                # Map perspective
                perspective = row["Perspective"]
                if not any(perspective == p.value for p in BSCPerspective):
                    raise ValueError(f"Invalid perspective: {perspective}")
                
                # Map UOM
                uom = row["UOM"]
                if not any(uom == u.value for u in BSCUOM):
                    raise ValueError(f"Invalid UOM: {uom}")
                
                # Map category
                category = row["Category"]
                if not any(category == c.value for c in BSCCategory):
                    raise ValueError(f"Invalid category: {category}")
                
                # Map calculation
                calculation = row["Calculation"]
                if not any(calculation == c.value for c in BSCCalculation):
                    raise ValueError(f"Invalid calculation: {calculation}")
                
                # Create indicator item
                indicator = BSCBulkImportItem(
                    perspective=perspective,
                    code=str(row["Code"]),
                    kpi=str(row["KPI"]),
                    kpi_definition=str(row["KPI Definition"]),
                    weight=Decimal(str(row["Weight"])),
                    uom=uom,
                    category=category,
                    calculation=calculation,
                    target=Decimal(str(row["Target"])) if isinstance(row["Target"], (int, float)) else str(row["Target"]),
                    related_pic=str(row["Related PIC"]) if not pd.isna(row["Related PIC"]) else None,
                    period_id=period_id
                )
                indicators.append(indicator)
            except Exception as e:
                # Log error but continue with next row
                print(f"Error processing row: {row}")
                print(f"Error details: {str(e)}")
                continue
        
        # Import indicators
        bulk_import = BSCBulkImport(indicators=indicators)
        created_indicators = await indicator_service.bulk_import_indicators(
            bulk_import=bulk_import,
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        
        return DataResponse(
            data=created_indicators, 
            message=f"{len(created_indicators)} BSC indicators imported successfully from {file.filename}"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the Excel file: {str(e)}"
        )


# BSC Actual endpoints
@router.post(
    "/actuals", 
    response_model=DataResponse[BSCActualResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new BSC actual",
    description="Create a new BSC actual value for an indicator."
)
async def create_actual(
    actual_in: BSCActualCreate,
    current_user: dict = Depends(get_current_active_user),
    actual_service: BSCActualService = Depends()
):
    """Create a new BSC actual."""
    try:
        actual = await actual_service.create_actual(
            actual_in=actual_in, 
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=actual, message="BSC actual created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the BSC actual: {str(e)}"
        )


@router.get(
    "/actuals/{actual_id}", 
    response_model=DataResponse[BSCActualResponse],
    summary="Get a BSC actual by ID",
    description="Get details of a specific BSC actual by its ID."
)
async def get_actual(
    actual_id: UUID,
    current_user: dict = Depends(get_current_user),
    actual_service: BSCActualService = Depends()
):
    """Get a BSC actual by ID."""
    try:
        actual = await actual_service.get_or_404(id=actual_id)
        return DataResponse(data=actual, message="BSC actual retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the BSC actual: {str(e)}"
        )


@router.get(
    "/indicators/{indicator_id}/actuals/latest", 
    response_model=DataResponse[Optional[BSCActualResponse]],
    summary="Get latest BSC actual for an indicator",
    description="Get the most recent BSC actual value for a specific indicator."
)
async def get_latest_actual(
    indicator_id: UUID,
    current_user: dict = Depends(get_current_user),
    actual_service: BSCActualService = Depends()
):
    """Get the latest BSC actual for an indicator."""
    try:
        actual = await actual_service.get_latest_actual(indicator_id=indicator_id)
        if not actual:
            return DataResponse(
                data=None,
                message=f"No actuals found for indicator {indicator_id}",
                success=True
            )
        
        return DataResponse(data=actual, message="Latest BSC actual retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the latest BSC actual: {str(e)}"
        )


@router.patch(
    "/actuals/{actual_id}", 
    response_model=DataResponse[BSCActualResponse],
    summary="Update a BSC actual",
    description="Update details of a specific BSC actual by its ID."
)
async def update_actual(
    actual_id: UUID,
    actual_in: BSCActualUpdate,
    current_user: dict = Depends(get_current_active_user),
    actual_service: BSCActualService = Depends()
):
    """Update a BSC actual."""
    try:
        actual = await actual_service.update_actual(
            actual_id=actual_id, 
            actual_in=actual_in,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=actual, message="BSC actual updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the BSC actual: {str(e)}"
        )


@router.delete(
    "/actuals/{actual_id}", 
    response_model=DataResponse[BSCActualResponse],
    summary="Delete a BSC actual",
    description="Delete a BSC actual by its ID (soft delete)."
)
async def delete_actual(
    actual_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    actual_service: BSCActualService = Depends()
):
    """Delete a BSC actual (soft delete)."""
    try:
        actual = await actual_service.delete(
            id=actual_id,
            soft_delete=True,
            deleted_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=actual, message="BSC actual deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the BSC actual: {str(e)}"
        )