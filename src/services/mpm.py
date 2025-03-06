"""MPM (Management Performance Measurement) service implementation for Performance Management System."""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from fastapi import HTTPException, Depends, status
from sqlmodel import Session
from decimal import Decimal

from src.core.database import get_db
from src.models.mpm import (
    MPMIndicator, MPMMonthlyTarget, MPMActionPlan, 
    MPMQuarterlyData, MPMActual, MPMApprover,
    MPMPerspective, MPMUOM, MPMCategory, MPMCalculation, MPMStatus
)
from src.repositories.mpm import (
    MPMIndicatorRepository, MPMMonthlyTargetRepository,
    MPMActionPlanRepository, MPMQuarterlyDataRepository,
    MPMActualRepository, MPMApproverRepository
)
from src.schemas.mpm import (
    MPMIndicatorCreate, MPMIndicatorUpdate,
    MPMMonthlyTargetCreate, MPMMonthlyTargetUpdate,
    MPMActionPlanCreate, MPMActionPlanUpdate,
    MPMQuarterlyDataCreate, MPMQuarterlyDataUpdate,
    MPMActualCreate, MPMActualUpdate,
    MPMApproverCreate, MPMApproverUpdate,
    MPMBulkImport
)
from src.services.base import BaseService


class MPMIndicatorService(BaseService[MPMIndicator, MPMIndicatorRepository]):
    """Service for MPM Indicator management."""
    
    def __init__(self, session: Session = Depends(get_db)):
        """Initialize with database session."""
        super().__init__(repository=MPMIndicatorRepository, session=session)
    
    async def create_indicator(self, indicator_in: MPMIndicatorCreate, created_by: Optional[UUID] = None) -> MPMIndicator:
        """Create a new MPM indicator.
        
        Args:
            indicator_in: MPM indicator creation data
            created_by: UUID of the user creating the indicator
            
        Returns:
            Created MPMIndicator object
            
        Raises:
            HTTPException: If an indicator with the same KPI already exists for the period
        """
        # Check if indicator already exists for this period
        existing_indicator = await self.repository.get_by_kpi(
            kpi=indicator_in.kpi, 
            period_id=indicator_in.period_id
        )
        
        if existing_indicator:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A MPM indicator with KPI '{indicator_in.kpi}' already exists for this period"
            )
        
        # If perspective is provided, assign the next KPI number
        if indicator_in.perspective:
            indicator_in_dict = indicator_in.dict()
            indicator_in_dict["kpi_number"] = await self.repository.get_next_kpi_number(
                perspective=indicator_in.perspective,
                period_id=indicator_in.period_id
            )
            
            # Create the new indicator
            return await self.repository.create(obj_in=indicator_in_dict, created_by=created_by)
        
        # Create the new indicator without KPI number
        return await self.repository.create(obj_in=indicator_in.dict(), created_by=created_by)
    
    async def update_indicator(
        self, 
        indicator_id: UUID, 
        indicator_in: MPMIndicatorUpdate, 
        updated_by: Optional[UUID] = None
    ) -> MPMIndicator:
        """Update a MPM indicator.
        
        Args:
            indicator_id: UUID of the indicator to update
            indicator_in: MPM indicator update data
            updated_by: UUID of the user updating the indicator
            
        Returns:
            Updated MPMIndicator object
            
        Raises:
            HTTPException: If the indicator is not found or if KPI is being updated to one that already exists
        """
        # Get existing indicator
        db_indicator = await self.repository.get_or_404(id=indicator_id)
        
        # Check if KPI is being updated and already exists
        if indicator_in.kpi and indicator_in.kpi != db_indicator.kpi:
            existing_indicator = await self.repository.get_by_kpi(
                kpi=indicator_in.kpi, 
                period_id=db_indicator.period_id
            )
            
            if existing_indicator and existing_indicator.id != indicator_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A MPM indicator with KPI '{indicator_in.kpi}' already exists for this period"
                )
        
        # Update the indicator
        return await self.repository.update(
            db_obj=db_indicator, 
            obj_in=indicator_in.dict(exclude_unset=True), 
            updated_by=updated_by
        )
    
    async def get_indicator_with_related(self, indicator_id: UUID) -> Dict[str, Any]:
        """Get a MPM indicator with its related data.
        
        Args:
            indicator_id: UUID of the indicator
            
        Returns:
            Dict with indicator and its related data
        """
        return await self.repository.get_by_id_with_related(id=indicator_id)
    
    async def get_indicators_by_period(self, period_id: UUID) -> List[MPMIndicator]:
        """Get all MPM indicators for a period.
        
        Args:
            period_id: Period ID
            
        Returns:
            List of MPMIndicator objects
        """
        return await self.repository.get_by_period(period_id=period_id)
    
    async def get_indicators_by_perspective(self, perspective: MPMPerspective, period_id: UUID) -> List[MPMIndicator]:
        """Get all MPM indicators for a specific perspective in a period.
        
        Args:
            perspective: MPM perspective
            period_id: Period ID
            
        Returns:
            List of MPMIndicator objects
        """
        return await self.repository.get_by_perspective(perspective=perspective, period_id=period_id)
    
    async def search_indicators(
        self,
        *,
        perspective: Optional[MPMPerspective] = None,
        period_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Search MPM indicators with pagination.
        
        Args:
            perspective: Optional perspective filter
            period_id: Optional period filter
            is_active: Optional active status filter
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Dictionary with results and pagination info
        """
        skip = (page - 1) * page_size
        
        # Get data with pagination
        indicators = await self.repository.search(
            perspective=perspective,
            period_id=period_id,
            is_active=is_active,
            skip=skip,
            limit=page_size
        )
        
        # Get total count for pagination
        total = await self.repository.search_count(
            perspective=perspective,
            period_id=period_id,
            is_active=is_active
        )
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "data": indicators,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    async def get_mpm_dashboard(self, period_id: UUID) -> Dict[str, Any]:
        """Get MPM dashboard data for a period.
        
        Args:
            period_id: Period ID
            
        Returns:
            Dashboard data with perspectives and totals
        """
        return await self.repository.get_dashboard_data(period_id=period_id)
    
    async def bulk_import_indicators(self, bulk_import: MPMBulkImport, created_by: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """Bulk import MPM indicators.
        
        Args:
            bulk_import: Bulk import data
            created_by: UUID of the user creating the indicators
            
        Returns:
            List of created indicators with their related data
        """
        created_items = []
        
        for indicator_data in bulk_import.indicators:
            try:
                # Check if indicator already exists
                existing_indicator = await self.repository.get_by_kpi(
                    kpi=indicator_data.kpi, 
                    period_id=indicator_data.period_id
                )
                
                if existing_indicator:
                    # Skip existing indicators
                    continue
                
                # Create new indicator
                indicator_dict = indicator_data.dict(exclude={"monthly_targets", "action_plans"})
                
                # If perspective is provided, assign the next KPI number
                if indicator_data.perspective:
                    indicator_dict["kpi_number"] = await self.repository.get_next_kpi_number(
                        perspective=indicator_data.perspective,
                        period_id=indicator_data.period_id
                    )
                
                indicator = await self.repository.create(
                    obj_in=indicator_dict, 
                    created_by=created_by
                )
                
                # Create monthly targets if provided
                monthly_targets_repo = MPMMonthlyTargetRepository(self.repository.session)
                monthly_targets = []
                
                for month, target_value in indicator_data.monthly_targets.items():
                    monthly_target = await monthly_targets_repo.create(
                        obj_in={
                            "month": month,
                            "target_value": target_value,
                            "indicator_id": indicator.id
                        },
                        created_by=created_by
                    )
                    monthly_targets.append(monthly_target)
                
                # Create action plans if provided
                action_plan_repo = MPMActionPlanRepository(self.repository.session)
                action_plans = []
                
                for action_plan_data in indicator_data.action_plans:
                    action_plan_dict = action_plan_data.dict()
                    action_plan_dict["indicator_id"] = indicator.id
                    action_plan = await action_plan_repo.create(
                        obj_in=action_plan_dict,
                        created_by=created_by
                    )
                    action_plans.append(action_plan)
                
                # Add to created items
                created_items.append({
                    "indicator": indicator,
                    "monthly_targets": monthly_targets,
                    "action_plans": action_plans
                })
                
            except Exception as e:
                # Log the error but continue with the next item
                print(f"Error importing indicator {indicator_data.kpi}: {str(e)}")
                continue
        
        return created_items


class MPMMonthlyTargetService(BaseService[MPMMonthlyTarget, MPMMonthlyTargetRepository]):
    """Service for MPM Monthly Target management."""
    
    def __init__(self, session: Session = Depends(get_db)):
        """Initialize with database session."""
        super().__init__(repository=MPMMonthlyTargetRepository, session=session)
    
    async def create_monthly_target(self, target_in: MPMMonthlyTargetCreate, created_by: Optional[UUID] = None) -> MPMMonthlyTarget:
        """Create a new MPM monthly target.
        
        Args:
            target_in: MPM monthly target creation data
            created_by: UUID of the user creating the target
            
        Returns:
            Created MPMMonthlyTarget object
            
        Raises:
            HTTPException: If a target for the same month already exists
        """
        # Check if target already exists for this month
        existing_target = await self.repository.get_by_month(
            indicator_id=target_in.indicator_id,
            month=target_in.month
        )
        
        if existing_target:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A monthly target for {target_in.month} already exists for this indicator"
            )
        
        # Create the new monthly target
        return await self.repository.create(obj_in=target_in.dict(), created_by=created_by)
    
    async def update_monthly_target(
        self, 
        target_id: UUID, 
        target_in: MPMMonthlyTargetUpdate, 
        updated_by: Optional[UUID] = None
    ) -> MPMMonthlyTarget:
        """Update a MPM monthly target.
        
        Args:
            target_id: UUID of the target to update
            target_in: MPM monthly target update data
            updated_by: UUID of the user updating the target
            
        Returns:
            Updated MPMMonthlyTarget object
        """
        # Get existing target
        db_target = await self.repository.get_or_404(id=target_id)
        
        # Update the target
        return await self.repository.update(
            db_obj=db_target, 
            obj_in=target_in.dict(exclude_unset=True), 
            updated_by=updated_by
        )
    
    async def get_targets_by_indicator(self, indicator_id: UUID) -> List[MPMMonthlyTarget]:
        """Get all monthly targets for an indicator.
        
        Args:
            indicator_id: Indicator ID
            
        Returns:
            List of MPMMonthlyTarget objects
        """
        return await self.repository.get_by_indicator(indicator_id=indicator_id)


class MPMActionPlanService(BaseService[MPMActionPlan, MPMActionPlanRepository]):
    """Service for MPM Action Plan management."""
    
    def __init__(self, session: Session = Depends(get_db)):
        """Initialize with database session."""
        super().__init__(repository=MPMActionPlanRepository, session=session)
    
    async def create_action_plan(self, plan_in: MPMActionPlanCreate, created_by: Optional[UUID] = None) -> MPMActionPlan:
        """Create a new MPM action plan.
        
        Args:
            plan_in: MPM action plan creation data
            created_by: UUID of the user creating the action plan
            
        Returns:
            Created MPMActionPlan object
        """
        # Create the new action plan
        return await self.repository.create(obj_in=plan_in.dict(), created_by=created_by)
    
    async def update_action_plan(
        self, 
        plan_id: UUID, 
        plan_in: MPMActionPlanUpdate, 
        updated_by: Optional[UUID] = None
    ) -> MPMActionPlan:
        """Update a MPM action plan.
        
        Args:
            plan_id: UUID of the action plan to update
            plan_in: MPM action plan update data
            updated_by: UUID of the user updating the action plan
            
        Returns:
            Updated MPMActionPlan object
        """
        # Get existing action plan
        db_plan = await self.repository.get_or_404(id=plan_id)
        
        # Update the action plan
        return await self.repository.update(
            db_obj=db_plan, 
            obj_in=plan_in.dict(exclude_unset=True), 
            updated_by=updated_by
        )
    
    async def get_action_plan_with_quarters(self, plan_id: UUID) -> Dict[str, Any]:
        """Get an action plan with its quarterly data.
        
        Args:
            plan_id: UUID of the action plan
            
        Returns:
            Dict with action plan and its quarterly data
        """
        return await self.repository.get_by_id_with_quarters(action_plan_id=plan_id)
    
    async def get_action_plans_by_indicator(self, indicator_id: UUID) -> List[MPMActionPlan]:
        """Get all action plans for an indicator.
        
        Args:
            indicator_id: Indicator ID
            
        Returns:
            List of MPMActionPlan objects
        """
        return await self.repository.get_by_indicator(indicator_id=indicator_id)
    
    async def update_action_plan_status(self, plan_id: UUID, updated_by: Optional[UUID] = None) -> MPMActionPlan:
        """Update the status of an action plan based on quarterly data.
        
        Args:
            plan_id: UUID of the action plan
            updated_by: UUID of the user updating the status
            
        Returns:
            Updated MPMActionPlan object
        """
        # Get existing action plan
        db_plan = await self.repository.get_or_404(id=plan_id)
        
        # Calculate status
        status = await self.repository.calculate_status(action_plan_id=plan_id)
        
        # Update the action plan
        return await self.repository.update(
            db_obj=db_plan, 
            obj_in={"status": status}, 
            updated_by=updated_by
        )
    
    async def get_quarterly_summary(self) -> List[Dict[str, Any]]:
        """Get quarterly summary of action plans.
        
        Returns:
            List of quarterly summary data
        """
        return await self.repository.get_quarterly_summary()


class MPMQuarterlyDataService(BaseService[MPMQuarterlyData, MPMQuarterlyDataRepository]):
    """Service for MPM Quarterly Data management."""
    
    def __init__(self, session: Session = Depends(get_db)):
        """Initialize with database session."""
        super().__init__(repository=MPMQuarterlyDataRepository, session=session)
    
    async def create_quarterly_data(self, data_in: MPMQuarterlyDataCreate, created_by: Optional[UUID] = None) -> MPMQuarterlyData:
        """Create new MPM quarterly data.
        
        Args:
            data_in: MPM quarterly data creation data
            created_by: UUID of the user creating the data
            
        Returns:
            Created MPMQuarterlyData object
            
        Raises:
            HTTPException: If data for the same quarter already exists
        """
        # Check if data already exists for this quarter
        existing_data = await self.repository.get_by_quarter(
            action_plan_id=data_in.action_plan_id,
            quarter=data_in.quarter
        )
        
        if existing_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quarterly data for {data_in.quarter} already exists for this action plan"
            )
        
        # Create the new quarterly data
        quarterly_data = await self.repository.create(obj_in=data_in.dict(), created_by=created_by)
        
        # Update action plan status if actual value is provided
        if data_in.actual_value is not None:
            action_plan_service = MPMActionPlanService(self.repository.session)
            await action_plan_service.update_action_plan_status(
                plan_id=data_in.action_plan_id,
                updated_by=created_by
            )
        
        return quarterly_data
    
    async def update_quarterly_data(
        self, 
        data_id: UUID, 
        data_in: MPMQuarterlyDataUpdate, 
        updated_by: Optional[UUID] = None
    ) -> MPMQuarterlyData:
        """Update MPM quarterly data.
        
        Args:
            data_id: UUID of the quarterly data to update
            data_in: MPM quarterly data update data
            updated_by: UUID of the user updating the data
            
        Returns:
            Updated MPMQuarterlyData object
        """
        # Get existing quarterly data
        db_data = await self.repository.get_or_404(id=data_id)
        
        # Update the quarterly data
        quarterly_data = await self.repository.update(
            db_obj=db_data, 
            obj_in=data_in.dict(exclude_unset=True), 
            updated_by=updated_by
        )
        
        # Update action plan status if actual value is updated
        if data_in.actual_value is not None:
            action_plan_service = MPMActionPlanService(self.repository.session)
            await action_plan_service.update_action_plan_status(
                plan_id=db_data.action_plan_id,
                updated_by=updated_by
            )
        
        return quarterly_data
    
    async def get_quarterly_data_by_action_plan(self, action_plan_id: UUID) -> List[MPMQuarterlyData]:
        """Get all quarterly data for an action plan.
        
        Args:
            action_plan_id: Action Plan ID
            
        Returns:
            List of MPMQuarterlyData objects
        """
        return await self.repository.get_by_action_plan(action_plan_id=action_plan_id)


class MPMActualService(BaseService[MPMActual, MPMActualRepository]):
    """Service for MPM Actual management."""
    
    def __init__(self, session: Session = Depends(get_db)):
        """Initialize with database session."""
        super().__init__(repository=MPMActualRepository, session=session)
    
    async def create_actual(self, actual_in: MPMActualCreate, created_by: Optional[UUID] = None) -> MPMActual:
        """Create a new MPM actual.
        
        Args:
            actual_in: MPM actual creation data
            created_by: UUID of the user creating the actual
            
        Returns:
            Created MPMActual object
        """
        # Calculate score based on indicator's weight and achievement
        indicator_repo = MPMIndicatorRepository(self.repository.session)
        indicator = await indicator_repo.get_or_404(id=actual_in.indicator_id)
        
        # Simple calculation - in a real application this would be more complex
        # based on category and calculation method
        score = (indicator.weight * actual_in.achievement) / Decimal(100)
        
        # Create actual data with calculated score
        actual_data = actual_in.dict()
        actual_data["score"] = score
        
        # Create the new actual
        return await self.repository.create(obj_in=actual_data, created_by=created_by)
    
    async def update_actual(
        self, 
        actual_id: UUID, 
        actual_in: MPMActualUpdate, 
        updated_by: Optional[UUID] = None
    ) -> MPMActual:
        """Update a MPM actual.
        
        Args:
            actual_id: UUID of the actual to update
            actual_in: MPM actual update data
            updated_by: UUID of the user updating the actual
            
        Returns:
            Updated MPMActual object
        """
        # Get existing actual
        db_actual = await self.repository.get_or_404(id=actual_id)
        
        # Update data
        update_data = actual_in.dict(exclude_unset=True)
        
        # Recalculate score if actual_value or achievement changed
        if "actual_value" in update_data or "achievement" in update_data:
            indicator_repo = MPMIndicatorRepository(self.repository.session)
            indicator = await indicator_repo.get_or_404(id=db_actual.indicator_id)
            
            # Get current achievement or use the one from update
            achievement = update_data.get("achievement", db_actual.achievement)
            
            # Recalculate score
            score = (indicator.weight * achievement) / Decimal(100)
            
            # Update calculated fields
            update_data["score"] = score
        
        # Update the actual
        return await self.repository.update(
            db_obj=db_actual, 
            obj_in=update_data, 
            updated_by=updated_by
        )
    
    async def get_actuals_by_indicator(self, indicator_id: UUID) -> List[MPMActual]:
        """Get all actuals for a MPM indicator.
        
        Args:
            indicator_id: Indicator ID
            
        Returns:
            List of MPMActual objects
        """
        return await self.repository.get_by_indicator(indicator_id=indicator_id)
    
    async def get_latest_actual(self, indicator_id: UUID) -> Optional[MPMActual]:
        """Get the latest actual for a MPM indicator.
        
        Args:
            indicator_id: Indicator ID
            
        Returns:
            Most recent MPMActual object, or None if no actuals
        """
        return await self.repository.get_latest_by_indicator(indicator_id=indicator_id)


class MPMApproverService(BaseService[MPMApprover, MPMApproverRepository]):
    """Service for MPM Approver management."""
    
    def __init__(self, session: Session = Depends(get_db)):
        """Initialize with database session."""
        super().__init__(repository=MPMApproverRepository, session=session)
    
    async def create_approver(self, approver_in: MPMApproverCreate, created_by: Optional[UUID] = None) -> MPMApprover:
        """Create a new MPM approver.
        
        Args:
            approver_in: MPM approver creation data
            created_by: UUID of the user creating the approver
            
        Returns:
            Created MPMApprover object
        """
        # Create the new approver
        return await self.repository.create(obj_in=approver_in.dict(), created_by=created_by)
    
    async def update_approver(
        self, 
        approver_id: UUID, 
        approver_in: MPMApproverUpdate, 
        updated_by: Optional[UUID] = None
    ) -> MPMApprover:
        """Update a MPM approver.
        
        Args:
            approver_id: UUID of the approver to update
            approver_in: MPM approver update data
            updated_by: UUID of the user updating the approver
            
        Returns:
            Updated MPMApprover object
        """
        # Get existing approver
        db_approver = await self.repository.get_or_404(id=approver_id)
        
        # Update the approver
        return await self.repository.update(
            db_obj=db_approver, 
            obj_in=approver_in.dict(exclude_unset=True), 
            updated_by=updated_by
        )
    
    async def get_all_approvers(self) -> List[MPMApprover]:
        """Get all MPM approvers.
        
        Returns:
            List of all MPMApprover objects
        """
        return await self.repository.get_all_approvers()
    
    async def get_approver_by_user(self, user_id: UUID) -> Optional[MPMApprover]:
        """Get an approver by user ID.
        
        Args:
            user_id: User ID
            
        Returns:
            MPMApprover object if found, None otherwise
        """
        return await self.repository.get_by_user(user_id=user_id)