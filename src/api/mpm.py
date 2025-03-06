"""MPM (Management Performance Measurement) API endpoints for Performance Management System."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from decimal import Decimal
import pandas as pd
import io

from src.schemas.base import DataResponse, PaginatedResponse
from src.schemas.mpm import (
    MPMIndicatorCreate, MPMIndicatorUpdate, MPMIndicatorResponse, MPMIndicatorWithRelatedResponse,
    MPMMonthlyTargetCreate, MPMMonthlyTargetUpdate, MPMMonthlyTargetResponse,
    MPMActionPlanCreate, MPMActionPlanUpdate, MPMActionPlanResponse, MPMActionPlanWithRelatedResponse,
    MPMQuarterlyDataCreate, MPMQuarterlyDataUpdate, MPMQuarterlyDataResponse,
    MPMActualCreate, MPMActualUpdate, MPMActualResponse,
    MPMApproverCreate, MPMApproverUpdate, MPMApproverResponse,
    MPMQuarterlySummary, MPMQueryParams, MPMDashboardResponse, MPMBulkImport,
    MPMPerspective, MPMUOM, MPMCategory, MPMCalculation, MPMStatus
)
from src.services.mpm import (
    MPMIndicatorService, MPMMonthlyTargetService, MPMActionPlanService,
    MPMQuarterlyDataService, MPMActualService, MPMApproverService
)
from src.auth.dependencies import get_current_user, get_current_active_user, check_user_role

router = APIRouter(prefix="/mpm", tags=["mpm"])


# MPM Indicator endpoints
@router.post(
    "/indicators", 
    response_model=DataResponse[MPMIndicatorResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new MPM indicator",
    description="Create a new MPM indicator with the given details."
)
async def create_indicator(
    indicator_in: MPMIndicatorCreate,
    current_user: dict = Depends(get_current_active_user),
    indicator_service: MPMIndicatorService = Depends()
):
    """Create a new MPM indicator."""
    try:
        indicator = await indicator_service.create_indicator(
            indicator_in=indicator_in, 
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=indicator, message="MPM indicator created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the MPM indicator: {str(e)}"
        )


@router.get(
    "/indicators", 
    response_model=PaginatedResponse[MPMIndicatorResponse],
    summary="Get all MPM indicators",
    description="Get a list of all MPM indicators with optional filtering and pagination."
)
async def get_indicators(
    query_params: MPMQueryParams = Depends(),
    current_user: dict = Depends(get_current_user),
    indicator_service: MPMIndicatorService = Depends()
):
    """Get all MPM indicators with optional filtering."""
    try:
        result = await indicator_service.search_indicators(
            perspective=query_params.perspective,
            period_id=query_params.period_id,
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
            message="MPM indicators retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving MPM indicators: {str(e)}"
        )


@router.get(
    "/indicators/{indicator_id}", 
    response_model=DataResponse[MPMIndicatorResponse],
    summary="Get a MPM indicator by ID",
    description="Get details of a specific MPM indicator by its ID."
)
async def get_indicator(
    indicator_id: UUID,
    current_user: dict = Depends(get_current_user),
    indicator_service: MPMIndicatorService = Depends()
):
    """Get a MPM indicator by ID."""
    try:
        indicator = await indicator_service.get_or_404(id=indicator_id)
        return DataResponse(data=indicator, message="MPM indicator retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the MPM indicator: {str(e)}"
        )


@router.get(
    "/indicators/{indicator_id}/related", 
    response_model=DataResponse[Dict[str, Any]],
    summary="Get a MPM indicator with related data",
    description="Get a MPM indicator with its related data (monthly targets, action plans, actuals)."
)
async def get_indicator_with_related(
    indicator_id: UUID,
    current_user: dict = Depends(get_current_user),
    indicator_service: MPMIndicatorService = Depends()
):
    """Get a MPM indicator with its related data."""
    try:
        result = await indicator_service.get_indicator_with_related(indicator_id=indicator_id)
        return DataResponse(data=result, message="MPM indicator with related data retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the MPM indicator with related data: {str(e)}"
        )


@router.patch(
    "/indicators/{indicator_id}", 
    response_model=DataResponse[MPMIndicatorResponse],
    summary="Update a MPM indicator",
    description="Update details of a specific MPM indicator by its ID."
)
async def update_indicator(
    indicator_id: UUID,
    indicator_in: MPMIndicatorUpdate,
    current_user: dict = Depends(get_current_active_user),
    indicator_service: MPMIndicatorService = Depends()
):
    """Update a MPM indicator."""
    try:
        indicator = await indicator_service.update_indicator(
            indicator_id=indicator_id, 
            indicator_in=indicator_in,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=indicator, message="MPM indicator updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the MPM indicator: {str(e)}"
        )


@router.delete(
    "/indicators/{indicator_id}", 
    response_model=DataResponse[MPMIndicatorResponse],
    summary="Delete a MPM indicator",
    description="Delete a MPM indicator by its ID (soft delete)."
)
async def delete_indicator(
    indicator_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    indicator_service: MPMIndicatorService = Depends()
):
    """Delete a MPM indicator (soft delete)."""
    try:
        indicator = await indicator_service.delete(
            id=indicator_id,
            soft_delete=True,
            deleted_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=indicator, message="MPM indicator deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the MPM indicator: {str(e)}"
        )


@router.get(
    "/dashboard/{period_id}", 
    response_model=DataResponse[MPMDashboardResponse],
    summary="Get MPM dashboard data",
    description="Get MPM dashboard data for a specific period, grouped by perspective."
)
async def get_mpm_dashboard(
    period_id: UUID,
    current_user: dict = Depends(get_current_user),
    indicator_service: MPMIndicatorService = Depends()
):
    """Get MPM dashboard data."""
    try:
        result = await indicator_service.get_mpm_dashboard(period_id=period_id)
        return DataResponse(data=result, message="MPM dashboard data retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving MPM dashboard data: {str(e)}"
        )


@router.post(
    "/indicators/bulk", 
    response_model=DataResponse[List[Dict[str, Any]]],
    status_code=status.HTTP_201_CREATED,
    summary="Bulk import MPM indicators",
    description="Import multiple MPM indicators at once."
)
async def bulk_import_indicators(
    bulk_import: MPMBulkImport,
    current_user: dict = Depends(get_current_active_user),
    indicator_service: MPMIndicatorService = Depends()
):
    """Bulk import MPM indicators."""
    try:
        indicators = await indicator_service.bulk_import_indicators(
            bulk_import=bulk_import,
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(
            data=indicators, 
            message=f"{len(indicators)} MPM indicators imported successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while importing MPM indicators: {str(e)}"
        )


@router.post(
    "/indicators/upload", 
    response_model=DataResponse[List[Dict[str, Any]]],
    status_code=status.HTTP_201_CREATED,
    summary="Upload MPM indicators from Excel",
    description="Upload and import MPM indicators from an Excel file."
)
async def upload_indicators(
    period_id: UUID,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_active_user),
    indicator_service: MPMIndicatorService = Depends()
):
    """Upload MPM indicators from Excel file."""
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
            "KPI", "KPI Definition", "Weight", "UOM", "Category", 
            "YTD Calculation", "Target", "Perspective"
        ]
        
        # Check if required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Transform Excel data to MPMBulkImport format
        indicators = []
        monthly_targets_columns = [col for col in df.columns if col.startswith("Target_")]
        
        for _, row in df.iterrows():
            try:
                # Validate enum values
                perspective = row.get("Perspective")
                if perspective and not any(perspective == p.value for p in MPMPerspective):
                    perspective = None
                
                uom = row["UOM"]
                if not any(uom == u.value for u in MPMUOM):
                    raise ValueError(f"Invalid UOM: {uom}")
                
                category = row["Category"]
                if not any(category == c.value for c in MPMCategory):
                    raise ValueError(f"Invalid category: {category}")
                
                ytd_calculation = row["YTD Calculation"]
                if not any(ytd_calculation == c.value for c in MPMCalculation):
                    raise ValueError(f"Invalid YTD calculation: {ytd_calculation}")
                
                # Create indicator
                indicator = {
                    "kpi": str(row["KPI"]),
                    "kpi_definition": str(row["KPI Definition"]),
                    "weight": Decimal(str(row["Weight"])),
                    "uom": uom,
                    "category": category,
                    "ytd_calculation": ytd_calculation,
                    "perspective": perspective,
                    "target": Decimal(str(row["Target"])),
                    "period_id": period_id,
                    "monthly_targets": {},
                    "action_plans": []
                }
                
                # Process monthly targets if available
                for col in monthly_targets_columns:
                    month = col.replace("Target_", "")
                    if not pd.isna(row[col]):
                        indicator["monthly_targets"][month] = Decimal(str(row[col]))
                
                # Add action plans if available
                action_plan_columns = [col for col in df.columns if col.startswith("ActionPlan_")]
                for col in action_plan_columns:
                    if not pd.isna(row[col]):
                        parts = col.split("_")
                        if len(parts) >= 3:
                            plan_num = parts[1]
                            field = "_".join(parts[2:])
                            
                            # Ensure action plan list is long enough
                            while len(indicator["action_plans"]) <= int(plan_num):
                                indicator["action_plans"].append({
                                    "description": "",
                                    "responsible_person": "",
                                    "deadline": "2025-01-01"  # Default date
                                })
                            
                            # Set action plan field
                            if field == "Description":
                                indicator["action_plans"][int(plan_num)]["description"] = str(row[col])
                            elif field == "ResponsiblePerson":
                                indicator["action_plans"][int(plan_num)]["responsible_person"] = str(row[col])
                            elif field == "Deadline":
                                try:
                                    # Try to parse date
                                    date_str = str(row[col])
                                    indicator["action_plans"][int(plan_num)]["deadline"] = date_str
                                except:
                                    # Fallback to default date
                                    indicator["action_plans"][int(plan_num)]["deadline"] = "2025-01-01"
                
                # Remove empty action plans
                indicator["action_plans"] = [plan for plan in indicator["action_plans"] 
                                            if plan["description"] and plan["responsible_person"]]
                
                indicators.append(indicator)
                
            except Exception as e:
                # Log error but continue with next row
                print(f"Error processing row: {row}")
                print(f"Error details: {str(e)}")
                continue
        
        # Import indicators
        bulk_import = MPMBulkImport(indicators=indicators)
        created_indicators = await indicator_service.bulk_import_indicators(
            bulk_import=bulk_import,
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        
        return DataResponse(
            data=created_indicators, 
            message=f"{len(created_indicators)} MPM indicators imported successfully from {file.filename}"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the Excel file: {str(e)}"
        )


# MPM Monthly Target endpoints
@router.post(
    "/monthly-targets", 
    response_model=DataResponse[MPMMonthlyTargetResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new MPM monthly target",
    description="Create a new MPM monthly target for an indicator."
)
async def create_monthly_target(
    target_in: MPMMonthlyTargetCreate,
    current_user: dict = Depends(get_current_active_user),
    target_service: MPMMonthlyTargetService = Depends()
):
    """Create a new MPM monthly target."""
    try:
        target = await target_service.create_monthly_target(
            target_in=target_in, 
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=target, message="MPM monthly target created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the MPM monthly target: {str(e)}"
        )


@router.get(
    "/monthly-targets/{target_id}", 
    response_model=DataResponse[MPMMonthlyTargetResponse],
    summary="Get a MPM monthly target by ID",
    description="Get details of a specific MPM monthly target by its ID."
)
async def get_monthly_target(
    target_id: UUID,
    current_user: dict = Depends(get_current_user),
    target_service: MPMMonthlyTargetService = Depends()
):
    """Get a MPM monthly target by ID."""
    try:
        target = await target_service.get_or_404(id=target_id)
        return DataResponse(data=target, message="MPM monthly target retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the MPM monthly target: {str(e)}"
        )


@router.get(
    "/indicators/{indicator_id}/monthly-targets", 
    response_model=DataResponse[List[MPMMonthlyTargetResponse]],
    summary="Get monthly targets for indicator",
    description="Get all monthly targets for a specific MPM indicator."
)
async def get_monthly_targets_by_indicator(
    indicator_id: UUID,
    current_user: dict = Depends(get_current_user),
    target_service: MPMMonthlyTargetService = Depends()
):
    """Get all monthly targets for an indicator."""
    try:
        targets = await target_service.get_targets_by_indicator(indicator_id=indicator_id)
        return DataResponse(data=targets, message="MPM monthly targets retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the MPM monthly targets: {str(e)}"
        )


@router.patch(
    "/monthly-targets/{target_id}", 
    response_model=DataResponse[MPMMonthlyTargetResponse],
    summary="Update a MPM monthly target",
    description="Update details of a specific MPM monthly target by its ID."
)
async def update_monthly_target(
    target_id: UUID,
    target_in: MPMMonthlyTargetUpdate,
    current_user: dict = Depends(get_current_active_user),
    target_service: MPMMonthlyTargetService = Depends()
):
    """Update a MPM monthly target."""
    try:
        target = await target_service.update_monthly_target(
            target_id=target_id, 
            target_in=target_in,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=target, message="MPM monthly target updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the MPM monthly target: {str(e)}"
        )


@router.delete(
    "/monthly-targets/{target_id}", 
    response_model=DataResponse[MPMMonthlyTargetResponse],
    summary="Delete a MPM monthly target",
    description="Delete a MPM monthly target by its ID (soft delete)."
)
async def delete_monthly_target(
    target_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    target_service: MPMMonthlyTargetService = Depends()
):
    """Delete a MPM monthly target (soft delete)."""
    try:
        target = await target_service.delete(
            id=target_id,
            soft_delete=True,
            deleted_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=target, message="MPM monthly target deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the MPM monthly target: {str(e)}"
        )


# MPM Action Plan endpoints
@router.post(
    "/action-plans", 
    response_model=DataResponse[MPMActionPlanResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new MPM action plan",
    description="Create a new MPM action plan for an indicator."
)
async def create_action_plan(
    plan_in: MPMActionPlanCreate,
    current_user: dict = Depends(get_current_active_user),
    plan_service: MPMActionPlanService = Depends()
):
    """Create a new MPM action plan."""
    try:
        plan = await plan_service.create_action_plan(
            plan_in=plan_in, 
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=plan, message="MPM action plan created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the MPM action plan: {str(e)}"
        )


@router.get(
    "/action-plans/{plan_id}", 
    response_model=DataResponse[MPMActionPlanResponse],
    summary="Get a MPM action plan by ID",
    description="Get details of a specific MPM action plan by its ID."
)
async def get_action_plan(
    plan_id: UUID,
    current_user: dict = Depends(get_current_user),
    plan_service: MPMActionPlanService = Depends()
):
    """Get a MPM action plan by ID."""
    try:
        plan = await plan_service.get_or_404(id=plan_id)
        return DataResponse(data=plan, message="MPM action plan retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the MPM action plan: {str(e)}"
        )


@router.get(
    "/action-plans/{plan_id}/quarters", 
    response_model=DataResponse[Dict[str, Any]],
    summary="Get a MPM action plan with quarterly data",
    description="Get a MPM action plan with its quarterly data."
)
async def get_action_plan_with_quarters(
    plan_id: UUID,
    current_user: dict = Depends(get_current_user),
    plan_service: MPMActionPlanService = Depends()
):
    """Get a MPM action plan with its quarterly data."""
    try:
        result = await plan_service.get_action_plan_with_quarters(plan_id=plan_id)
        return DataResponse(data=result, message="MPM action plan with quarterly data retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the MPM action plan with quarterly data: {str(e)}"
        )


@router.get(
    "/indicators/{indicator_id}/action-plans", 
    response_model=DataResponse[List[MPMActionPlanResponse]],
    summary="Get action plans for indicator",
    description="Get all action plans for a specific MPM indicator."
)
async def get_action_plans_by_indicator(
    indicator_id: UUID,
    current_user: dict = Depends(get_current_user),
    plan_service: MPMActionPlanService = Depends()
):
    """Get all action plans for an indicator."""
    try:
        plans = await plan_service.get_action_plans_by_indicator(indicator_id=indicator_id)
        return DataResponse(data=plans, message="MPM action plans retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the MPM action plans: {str(e)}"
        )


@router.patch(
    "/action-plans/{plan_id}", 
    response_model=DataResponse[MPMActionPlanResponse],
    summary="Update a MPM action plan",
    description="Update details of a specific MPM action plan by its ID."
)
async def update_action_plan(
    plan_id: UUID,
    plan_in: MPMActionPlanUpdate,
    current_user: dict = Depends(get_current_active_user),
    plan_service: MPMActionPlanService = Depends()
):
    """Update a MPM action plan."""
    try:
        plan = await plan_service.update_action_plan(
            plan_id=plan_id, 
            plan_in=plan_in,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=plan, message="MPM action plan updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the MPM action plan: {str(e)}"
        )


@router.patch(
    "/action-plans/{plan_id}/status", 
    response_model=DataResponse[MPMActionPlanResponse],
    summary="Update a MPM action plan status",
    description="Update the status of a specific MPM action plan based on quarterly data."
)
async def update_action_plan_status(
    plan_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    plan_service: MPMActionPlanService = Depends()
):
    """Update a MPM action plan status."""
    try:
        plan = await plan_service.update_action_plan_status(
            plan_id=plan_id,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=plan, message="MPM action plan status updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the MPM action plan status: {str(e)}"
        )


@router.get(
    "/action-plans/quarterly-summary", 
    response_model=DataResponse[List[MPMQuarterlySummary]],
    summary="Get quarterly summary of action plans",
    description="Get a summary of action plans grouped by quarter."
)
async def get_quarterly_summary(
    current_user: dict = Depends(get_current_user),
    plan_service: MPMActionPlanService = Depends()
):
    """Get quarterly summary of action plans."""
    try:
        summary = await plan_service.get_quarterly_summary()
        return DataResponse(data=summary, message="Quarterly summary retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the quarterly summary: {str(e)}"
        )


@router.delete(
    "/action-plans/{plan_id}", 
    response_model=DataResponse[MPMActionPlanResponse],
    summary="Delete a MPM action plan",
    description="Delete a MPM action plan by its ID (soft delete)."
)
async def delete_action_plan(
    plan_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    plan_service: MPMActionPlanService = Depends()
):
    """Delete a MPM action plan (soft delete)."""
    try:
        plan = await plan_service.delete(
            id=plan_id,
            soft_delete=True,
            deleted_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=plan, message="MPM action plan deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the MPM action plan: {str(e)}"
        )


# MPM Quarterly Data endpoints
@router.post(
    "/quarterly-data", 
    response_model=DataResponse[MPMQuarterlyDataResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Create new MPM quarterly data",
    description="Create new MPM quarterly data for an action plan."
)
async def create_quarterly_data(
    data_in: MPMQuarterlyDataCreate,
    current_user: dict = Depends(get_current_active_user),
    data_service: MPMQuarterlyDataService = Depends()
):
    """Create new MPM quarterly data."""
    try:
        data = await data_service.create_quarterly_data(
            data_in=data_in, 
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=data, message="MPM quarterly data created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the MPM quarterly data: {str(e)}"
        )


@router.get(
    "/quarterly-data/{data_id}", 
    response_model=DataResponse[MPMQuarterlyDataResponse],
    summary="Get MPM quarterly data by ID",
    description="Get details of specific MPM quarterly data by its ID."
)
async def get_quarterly_data(
    data_id: UUID,
    current_user: dict = Depends(get_current_user),
    data_service: MPMQuarterlyDataService = Depends()
):
    """Get MPM quarterly data by ID."""
    try:
        data = await data_service.get_or_404(id=data_id)
        return DataResponse(data=data, message="MPM quarterly data retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the MPM quarterly data: {str(e)}"
        )


@router.get(
    "/action-plans/{action_plan_id}/quarterly-data", 
    response_model=DataResponse[List[MPMQuarterlyDataResponse]],
    summary="Get quarterly data for action plan",
    description="Get all quarterly data for a specific MPM action plan."
)
async def get_quarterly_data_by_action_plan(
    action_plan_id: UUID,
    current_user: dict = Depends(get_current_user),
    data_service: MPMQuarterlyDataService = Depends()
):
    """Get all quarterly data for an action plan."""
    try:
        data = await data_service.get_quarterly_data_by_action_plan(action_plan_id=action_plan_id)
        return DataResponse(data=data, message="MPM quarterly data retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the MPM quarterly data: {str(e)}"
        )


@router.patch(
    "/quarterly-data/{data_id}", 
    response_model=DataResponse[MPMQuarterlyDataResponse],
    summary="Update MPM quarterly data",
    description="Update details of specific MPM quarterly data by its ID."
)
async def update_quarterly_data(
    data_id: UUID,
    data_in: MPMQuarterlyDataUpdate,
    current_user: dict = Depends(get_current_active_user),
    data_service: MPMQuarterlyDataService = Depends()
):
    """Update MPM quarterly data."""
    try:
        data = await data_service.update_quarterly_data(
            data_id=data_id, 
            data_in=data_in,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=data, message="MPM quarterly data updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the MPM quarterly data: {str(e)}"
        )


@router.delete(
    "/quarterly-data/{data_id}", 
    response_model=DataResponse[MPMQuarterlyDataResponse],
    summary="Delete MPM quarterly data",
    description="Delete MPM quarterly data by its ID (soft delete)."
)
async def delete_quarterly_data(
    data_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    data_service: MPMQuarterlyDataService = Depends()
):
    """Delete MPM quarterly data (soft delete)."""
    try:
        data = await data_service.delete(
            id=data_id,
            soft_delete=True,
            deleted_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=data, message="MPM quarterly data deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the MPM quarterly data: {str(e)}"
        )


# MPM Actual endpoints
@router.post(
    "/actuals", 
    response_model=DataResponse[MPMActualResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new MPM actual",
    description="Create a new MPM actual value for an indicator."
)
async def create_actual(
    actual_in: MPMActualCreate,
    current_user: dict = Depends(get_current_active_user),
    actual_service: MPMActualService = Depends()
):
    """Create a new MPM actual."""
    try:
        actual = await actual_service.create_actual(
            actual_in=actual_in, 
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=actual, message="MPM actual created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the MPM actual: {str(e)}"
        )


@router.get(
    "/actuals/{actual_id}", 
    response_model=DataResponse[MPMActualResponse],
    summary="Get a MPM actual by ID",
    description="Get details of a specific MPM actual by its ID."
)
async def get_actual(
    actual_id: UUID,
    current_user: dict = Depends(get_current_user),
    actual_service: MPMActualService = Depends()
):
    """Get a MPM actual by ID."""
    try:
        actual = await actual_service.get_or_404(id=actual_id)
        return DataResponse(data=actual, message="MPM actual retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the MPM actual: {str(e)}"
        )


@router.get(
    "/indicators/{indicator_id}/actuals", 
    response_model=DataResponse[List[MPMActualResponse]],
    summary="Get actuals for indicator",
    description="Get all actual values for a specific MPM indicator."
)
async def get_actuals_by_indicator(
    indicator_id: UUID,
    current_user: dict = Depends(get_current_user),
    actual_service: MPMActualService = Depends()
):
    """Get all actuals for an indicator."""
    try:
        actuals = await actual_service.get_actuals_by_indicator(indicator_id=indicator_id)
        return DataResponse(data=actuals, message="MPM actuals retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the MPM actuals: {str(e)}"
        )


@router.get(
    "/indicators/{indicator_id}/actuals/latest", 
    response_model=DataResponse[Optional[MPMActualResponse]],
    summary="Get latest MPM actual for an indicator",
    description="Get the most recent MPM actual value for a specific indicator."
)
async def get_latest_actual(
    indicator_id: UUID,
    current_user: dict = Depends(get_current_user),
    actual_service: MPMActualService = Depends()
):
    """Get the latest MPM actual for an indicator."""
    try:
        actual = await actual_service.get_latest_actual(indicator_id=indicator_id)
        if not actual:
            return DataResponse(
                data=None,
                message=f"No actuals found for indicator {indicator_id}",
                success=True
            )
        
        return DataResponse(data=actual, message="Latest MPM actual retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the latest MPM actual: {str(e)}"
        )


@router.patch(
    "/actuals/{actual_id}", 
    response_model=DataResponse[MPMActualResponse],
    summary="Update a MPM actual",
    description="Update details of a specific MPM actual by its ID."
)
async def update_actual(
    actual_id: UUID,
    actual_in: MPMActualUpdate,
    current_user: dict = Depends(get_current_active_user),
    actual_service: MPMActualService = Depends()
):
    """Update a MPM actual."""
    try:
        actual = await actual_service.update_actual(
            actual_id=actual_id, 
            actual_in=actual_in,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=actual, message="MPM actual updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the MPM actual: {str(e)}"
        )


@router.delete(
    "/actuals/{actual_id}", 
    response_model=DataResponse[MPMActualResponse],
    summary="Delete a MPM actual",
    description="Delete a MPM actual by its ID (soft delete)."
)
async def delete_actual(
    actual_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    actual_service: MPMActualService = Depends()
):
    """Delete a MPM actual (soft delete)."""
    try:
        actual = await actual_service.delete(
            id=actual_id,
            soft_delete=True,
            deleted_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=actual, message="MPM actual deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the MPM actual: {str(e)}"
        )


# MPM Approver endpoints
@router.post(
    "/approvers", 
    response_model=DataResponse[MPMApproverResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new MPM approver",
    description="Create a new MPM approver."
)
async def create_approver(
    approver_in: MPMApproverCreate,
    current_user: dict = Depends(check_user_role(["admin", "hr"])),
    approver_service: MPMApproverService = Depends()
):
    """Create a new MPM approver."""
    try:
        approver = await approver_service.create_approver(
            approver_in=approver_in, 
            created_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=approver, message="MPM approver created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the MPM approver: {str(e)}"
        )


@router.get(
    "/approvers", 
    response_model=DataResponse[List[MPMApproverResponse]],
    summary="Get all MPM approvers",
    description="Get a list of all MPM approvers."
)
async def get_all_approvers(
    current_user: dict = Depends(get_current_user),
    approver_service: MPMApproverService = Depends()
):
    """Get all MPM approvers."""
    try:
        approvers = await approver_service.get_all_approvers()
        return DataResponse(data=approvers, message="MPM approvers retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving MPM approvers: {str(e)}"
        )


@router.get(
    "/approvers/{approver_id}", 
    response_model=DataResponse[MPMApproverResponse],
    summary="Get a MPM approver by ID",
    description="Get details of a specific MPM approver by its ID."
)
async def get_approver(
    approver_id: UUID,
    current_user: dict = Depends(get_current_user),
    approver_service: MPMApproverService = Depends()
):
    """Get a MPM approver by ID."""
    try:
        approver = await approver_service.get_or_404(id=approver_id)
        return DataResponse(data=approver, message="MPM approver retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the MPM approver: {str(e)}"
        )


@router.get(
    "/approvers/user/{user_id}", 
    response_model=DataResponse[Optional[MPMApproverResponse]],
    summary="Get a MPM approver by user ID",
    description="Get a MPM approver for a specific user by user ID."
)
async def get_approver_by_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    approver_service: MPMApproverService = Depends()
):
    """Get a MPM approver by user ID."""
    try:
        approver = await approver_service.get_approver_by_user(user_id=user_id)
        if not approver:
            return DataResponse(
                data=None,
                message=f"No approver found for user {user_id}",
                success=True
            )
        
        return DataResponse(data=approver, message="MPM approver retrieved successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the MPM approver: {str(e)}"
        )


@router.patch(
    "/approvers/{approver_id}", 
    response_model=DataResponse[MPMApproverResponse],
    summary="Update a MPM approver",
    description="Update details of a specific MPM approver by its ID."
)
async def update_approver(
    approver_id: UUID,
    approver_in: MPMApproverUpdate,
    current_user: dict = Depends(check_user_role(["admin", "hr"])),
    approver_service: MPMApproverService = Depends()
):
    """Update a MPM approver."""
    try:
        approver = await approver_service.update_approver(
            approver_id=approver_id, 
            approver_in=approver_in,
            updated_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=approver, message="MPM approver updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the MPM approver: {str(e)}"
        )


@router.delete(
    "/approvers/{approver_id}", 
    response_model=DataResponse[MPMApproverResponse],
    summary="Delete a MPM approver",
    description="Delete a MPM approver by its ID (soft delete)."
)
async def delete_approver(
    approver_id: UUID,
    current_user: dict = Depends(check_user_role(["admin"])),
    approver_service: MPMApproverService = Depends()
):
    """Delete a MPM approver (soft delete)."""
    try:
        approver = await approver_service.delete(
            id=approver_id,
            soft_delete=True,
            deleted_by=UUID(current_user["id"]) if "id" in current_user else None
        )
        return DataResponse(data=approver, message="MPM approver deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the MPM approver: {str(e)}"
        )