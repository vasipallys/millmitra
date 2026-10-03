from models.production import ProductionBatch, ProductionStep, QualityTest, ProductionSchedule, MaintenanceLog
from models.inventory import PaddyStock, ProductStock
from models.user import User
from extensions import db
from services.tenant_scope import tq, t_get, t_get_or_404
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import json

class ProductionService:
    
    def get_batches(self, status=None, start_date=None, end_date=None, page=1, per_page=20):
        """Get production batches with filtering and pagination"""
        
        query = tq(ProductionBatch)
        
        if status:
            query = query.filter(ProductionBatch.status == status)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(ProductionBatch.start_time >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(ProductionBatch.start_time <= end_dt)
        
        query = query.order_by(ProductionBatch.start_time.desc())
        
        paginated = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'batches': [batch.to_dict() for batch in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'per_page': per_page
        }
    
    def create_batch(self, user: User, batch_data: dict):
        """Create a new production batch with AI optimization"""
        
        # Generate batch number
        batch_number = self._generate_batch_number()
        
        # Calculate planned output based on variety and input
        planned_output = self._calculate_planned_output(
            batch_data['paddy_variety'], 
            batch_data['input_quantity']
        )
        
        batch = ProductionBatch(
            batch_number=batch_number,
            paddy_variety=batch_data['paddy_variety'],
            input_quantity=batch_data['input_quantity'],
            input_source=batch_data.get('input_source', 'procurement'),
            source_reference_id=batch_data.get('source_reference_id'),
            planned_start_time=batch_data.get('planned_start_time'),
            planned_end_time=batch_data.get('planned_end_time'),
            planned_output_quantity=planned_output,
            target_rice_variety=batch_data.get('target_rice_variety'),
            machine_settings=batch_data.get('machine_settings', {}),
            priority=batch_data.get('priority', 'normal'),
            production_notes=batch_data.get('notes'),
            created_by=user.id,
            supervisor_id=batch_data.get('supervisor_id')
        )
        
        db.session.add(batch)
        db.session.commit()
        
        return batch
    
    def start_batch(self, batch: ProductionBatch, user: User):
        """Start production batch"""
        
        if batch.status != 'planned':
            return {'success': False, 'message': 'Batch is not in planned status'}
        
        # Check resource availability
        resource_check = self._check_resource_availability(batch)
        if not resource_check['available']:
            return {
                'success': False, 
                'message': 'Resources not available',
                'missing_resources': resource_check['missing']
            }
        
        # Update batch status
        batch.status = 'in_progress'
        batch.start_time = datetime.utcnow()
        batch.started_by = user.id
        
        # Create initial production step
        initial_step = ProductionStep(
            batch_id=batch.id,
            step_name='cleaning',
            step_order=1,
            status='in_progress',
            start_time=datetime.utcnow(),
            operator_id=user.id,
            parameters=batch.machine_settings.get('cleaning', {}),
            input_quantity=batch.input_quantity,
            notes='Batch started - cleaning phase initiated'
        )
        
        db.session.add(initial_step)
        db.session.commit()
        from services.notification_service import batch_started
        batch_started(batch)
        
        return {
            'success': True,
            'message': 'Batch started successfully',
            'batch': batch.to_dict(),
            'current_step': initial_step.to_dict()
        }
    
    def complete_batch(self, batch: ProductionBatch, user: User, completion_data: dict):
        """Complete a production batch"""
        
        if batch.status != 'in_progress':
            return {'success': False, 'message': 'Batch is not in progress'}
        
        # Update batch with completion data
        batch.status = 'completed'
        batch.end_time = datetime.utcnow()
        batch.completed_by = user.id
        batch.output_quantity = completion_data['output_quantity']
        batch.waste_quantity = completion_data.get('waste_quantity', 0)
        batch.byproduct_quantity = completion_data.get('byproduct_quantity', 0)
        batch.efficiency_score = self._calculate_efficiency_score(batch)
        batch.yield_percentage = (batch.output_quantity / batch.input_quantity) * 100
        batch.completion_notes = completion_data.get('notes')
        
        # Complete any open steps
        open_steps = ProductionStep.query.filter(
            ProductionStep.batch_id == batch.id,
            ProductionStep.status == 'in_progress'
        ).all()
        
        for step in open_steps:
            step.status = 'completed'
            step.end_time = datetime.utcnow()
            if step.start_time:
                step.actual_duration = int((step.end_time - step.start_time).total_seconds() / 60)
        
        # Update inventory
        self._update_inventory_after_completion(batch, completion_data)
        
        db.session.commit()
        from services.notification_service import batch_completed
        batch_completed(batch)
        
        return {
            'success': True,
            'message': 'Batch completed successfully',
            'batch': batch.to_dict(),
            'efficiency_score': batch.efficiency_score,
            'yield_percentage': batch.yield_percentage
        }
    
    def add_production_step(self, batch: ProductionBatch, user: User, step_data: dict):
        """Add a production step to a batch"""
        
        # Complete previous step if exists
        current_step = ProductionStep.query.filter(
            ProductionStep.batch_id == batch.id,
            ProductionStep.status == 'in_progress'
        ).first()
        
        if current_step:
            current_step.status = 'completed'
            current_step.end_time = datetime.utcnow()
            current_step.output_quantity = step_data.get('previous_output_quantity', current_step.input_quantity)
            if current_step.start_time:
                current_step.actual_duration = int((current_step.end_time - current_step.start_time).total_seconds() / 60)
                current_step.step_efficiency = self._calculate_step_efficiency(current_step)
        
        # Determine step order
        max_order = db.session.query(func.max(ProductionStep.step_order)).filter(
            ProductionStep.batch_id == batch.id
        ).scalar() or 0
        
        # Create new step
        step = ProductionStep(
            batch_id=batch.id,
            step_name=step_data['step_name'],
            step_order=max_order + 1,
            status='in_progress',
            start_time=datetime.utcnow(),
            operator_id=user.id,
            parameters=step_data.get('parameters', {}),
            machine_id=step_data.get('machine_id'),
            input_quantity=current_step.output_quantity if current_step else batch.input_quantity,
            expected_duration=step_data.get('expected_duration'),
            notes=step_data.get('notes'),
            ai_optimization=step_data.get('ai_optimization', {})
        )
        
        db.session.add(step)
        db.session.commit()
        
        return step
    
    def create_quality_test(self, batch: ProductionBatch, user: User, test_data: dict, ai_analysis: dict = None):
        """Create a quality test for a batch"""
        
        quality_test = QualityTest(
            batch_id=batch.id,
            test_type=test_data['test_type'],
            test_stage=test_data.get('test_stage'),
            sample_size=test_data.get('sample_size', 1.0),
            moisture_content=test_data.get('moisture_content'),
            broken_grains=test_data.get('broken_grains'),
            foreign_matter=test_data.get('foreign_matter'),
            chalky_grains=test_data.get('chalky_grains'),
            head_rice_recovery=test_data.get('head_rice_recovery'),
            milling_degree=test_data.get('milling_degree'),
            whiteness_index=test_data.get('whiteness_index'),
            transparency=test_data.get('transparency'),
            grain_length=test_data.get('grain_length'),
            grain_width=test_data.get('grain_width'),
            tested_by=user.id,
            test_method=test_data.get('test_method', 'manual'),
            notes=test_data.get('notes'),
            ai_analysis=ai_analysis
        )
        
        # Calculate overall grade and score
        quality_score = self._calculate_quality_score(quality_test)
        quality_test.quality_score = quality_score
        quality_test.overall_grade = self._get_quality_grade(quality_score)
        quality_test.pass_fail = quality_score >= 70  # Minimum passing score
        
        if ai_analysis:
            quality_test.confidence_score = ai_analysis.get('confidence', 0.95)
        
        db.session.add(quality_test)
        
        # Update batch quality if this is a final test
        if test_data['test_type'] == 'final':
            batch.quality_grade = quality_test.overall_grade
        
        db.session.commit()
        
        return quality_test
    
    def get_current_production_status(self):
        """Get current production status overview"""
        
        # Active batches
        active_batches = tq(ProductionBatch).filter(
            ProductionBatch.status == 'in_progress'
        ).all()
        
        # Today's completed batches
        today = datetime.utcnow().date()
        completed_today = tq(ProductionBatch).filter(
            and_(
                ProductionBatch.status == 'completed',
                func.date(ProductionBatch.end_time) == today
            )
        ).all()
        
        # Current capacity utilization
        total_capacity = 1000  # quintals per day (configurable)
        today_input = sum(batch.input_quantity for batch in completed_today)
        active_input = sum(batch.input_quantity for batch in active_batches)
        
        utilization = ((today_input + active_input) / total_capacity) * 100
        
        # Quality metrics
        quality_stats = self._get_quality_statistics(today)
        
        return {
            'active_batches': len(active_batches),
            'completed_today': len(completed_today),
            'capacity_utilization': round(utilization, 2),
            'total_input_today': today_input,
            'total_output_today': sum(batch.output_quantity or 0 for batch in completed_today),
            'average_efficiency': self._calculate_average_efficiency(completed_today),
            'quality_stats': quality_stats,
            'active_batch_details': [batch.to_dict() for batch in active_batches]
        }
    
    def get_production_analytics(self, days: int = 30):
        """Get production analytics for specified period"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Batch analytics
        batches = tq(ProductionBatch).filter(
            ProductionBatch.created_at >= start_date
        ).all()
        
        completed_batches = [b for b in batches if b.status == 'completed']
        
        # Daily production data
        daily_data = self._get_daily_production_data(start_date, days)
        
        # Efficiency trends
        efficiency_trend = self._get_efficiency_trend(completed_batches)
        
        # Quality trends
        quality_trend = self._get_quality_trend(start_date)
        
        # Variety analysis
        variety_analysis = self._get_variety_analysis(completed_batches)
        
        return {
            'total_batches': len(batches),
            'completed_batches': len(completed_batches),
            'total_input': sum(b.input_quantity for b in completed_batches),
            'total_output': sum(b.output_quantity or 0 for b in completed_batches),
            'average_efficiency': sum(b.efficiency_score or 0 for b in completed_batches) / len(completed_batches) if completed_batches else 0,
            'daily_production': daily_data,
            'efficiency_trend': efficiency_trend,
            'quality_trend': quality_trend,
            'variety_analysis': variety_analysis
        }
    
    def create_production_schedule(self, user: User, schedule_data: dict):
        """Create production schedule"""
        
        schedule = ProductionSchedule(
            schedule_date=schedule_data['schedule_date'],
            shift=schedule_data['shift'],
            planned_batches=schedule_data.get('planned_batches', 0),
            planned_quantity=schedule_data.get('planned_quantity', 0),
            available_capacity=schedule_data.get('available_capacity'),
            utilization_target=schedule_data.get('utilization_target', 85),
            assigned_operators=schedule_data.get('assigned_operators', []),
            machine_allocation=schedule_data.get('machine_allocation', {}),
            created_by=user.id
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return schedule
    
    def log_maintenance(self, user: User, maintenance_data: dict):
        """Log machine maintenance"""
        
        maintenance = MaintenanceLog(
            machine_id=maintenance_data['machine_id'],
            machine_name=maintenance_data.get('machine_name'),
            maintenance_type=maintenance_data['maintenance_type'],
            description=maintenance_data['description'],
            scheduled_date=maintenance_data.get('scheduled_date'),
            technician_id=maintenance_data.get('technician_id'),
            supervisor_id=user.id,
            cost=maintenance_data.get('cost', 0),
            parts_used=maintenance_data.get('parts_used', []),
            impact_on_production=maintenance_data.get('impact_on_production', 'none'),
            ai_predicted=maintenance_data.get('ai_predicted', False),
            failure_probability=maintenance_data.get('failure_probability'),
            notes=maintenance_data.get('notes')
        )
        
        db.session.add(maintenance)
        db.session.commit()
        
        return maintenance
    
    # Helper methods
    def _generate_batch_number(self):
        """Generate unique batch number"""
        prefix = f"B{datetime.now().strftime('%Y%m')}"
        count = tq(ProductionBatch).filter(
            ProductionBatch.batch_number.like(f"{prefix}%")
        ).count() + 1
        return f"{prefix}{count:04d}"
    
    def _calculate_planned_output(self, variety: str, input_quantity: float):
        """Calculate planned output based on variety and input"""
        # Variety-specific yield rates
        yield_rates = {
            'IR64': 0.68,
            'Swarna': 0.65,
            'Sona Masuri': 0.70,
            'Basmati 1121': 0.62,
            'Pusa Basmati': 0.64
        }
        
        rate = yield_rates.get(variety, 0.65)  # Default rate
        return input_quantity * rate
    
    def _calculate_efficiency_score(self, batch: ProductionBatch):
        """Calculate batch efficiency score"""
        if not batch.output_quantity or not batch.input_quantity:
            return 0
        
        # Base efficiency from yield
        yield_efficiency = (batch.output_quantity / batch.input_quantity) * 100
        
        # Time efficiency (if planned vs actual time available)
        time_efficiency = 100  # Default if no time data
        if batch.planned_start_time and batch.planned_end_time and batch.start_time and batch.end_time:
            planned_duration = (batch.planned_end_time - batch.planned_start_time).total_seconds()
            actual_duration = (batch.end_time - batch.start_time).total_seconds()
            if actual_duration > 0:
                time_efficiency = min(100, (planned_duration / actual_duration) * 100)
        
        # Quality factor
        quality_factor = 1.0
        if batch.quality_grade:
            quality_factors = {'A': 1.1, 'B': 1.0, 'C': 0.9, 'D': 0.8}
            quality_factor = quality_factors.get(batch.quality_grade, 1.0)
        
        # Waste factor
        waste_factor = 1.0
        if batch.waste_quantity and batch.input_quantity:
            waste_percentage = (batch.waste_quantity / batch.input_quantity) * 100
            waste_factor = max(0.5, 1.0 - (waste_percentage / 100))
        
        # Combined efficiency score
        efficiency = (yield_efficiency * 0.4 + time_efficiency * 0.3) * quality_factor * waste_factor
        return min(100, max(0, efficiency))
    
    def _calculate_step_efficiency(self, step: ProductionStep):
        """Calculate step efficiency"""
        if not step.output_quantity or not step.input_quantity:
            return 0
        
        yield_efficiency = (step.output_quantity / step.input_quantity) * 100
        
        time_efficiency = 100
        if step.expected_duration and step.actual_duration:
            time_efficiency = min(100, (step.expected_duration / step.actual_duration) * 100)
        
        return (yield_efficiency * 0.7 + time_efficiency * 0.3)
    
    def _calculate_quality_score(self, test: QualityTest):
        """Calculate overall quality score from test parameters"""
        score = 100
        
        # Moisture content (optimal: 12-14%)
        if test.moisture_content:
            if test.moisture_content < 12 or test.moisture_content > 14:
                score -= abs(test.moisture_content - 13) * 2
        
        # Broken grains (lower is better)
        if test.broken_grains:
            score -= test.broken_grains * 1.5
        
        # Foreign matter (lower is better)
        if test.foreign_matter:
            score -= test.foreign_matter * 3
        
        # Head rice recovery (higher is better)
        if test.head_rice_recovery:
            if test.head_rice_recovery < 60:
                score -= (60 - test.head_rice_recovery) * 0.5
        
        return max(0, min(100, score))
    
    def _get_quality_grade(self, score: float):
        """Convert quality score to grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        else:
            return 'D'
    
    def _check_resource_availability(self, batch: ProductionBatch):
        """Check if resources are available for batch"""
        # Simplified check - in real implementation, check machine availability,
        # operator schedules, raw material availability, etc.
        return {'available': True, 'missing': []}
    
    def _update_inventory_after_completion(self, batch: ProductionBatch, completion_data: dict):
        """Update inventory after batch completion"""
        # This would update ProductStock with the output
        # and reduce PaddyStock if sourced from inventory
        pass
    
    def _get_quality_statistics(self, date):
        """Get quality statistics for a specific date"""
        tests = tq(QualityTest).filter(
            func.date(QualityTest.test_date) == date
        ).all()
        
        if not tests:
            return {'average_score': 0, 'grade_distribution': {}}
        
        average_score = sum(test.quality_score or 0 for test in tests) / len(tests)
        
        grade_distribution = {}
        for test in tests:
            grade = test.overall_grade or 'Unknown'
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        return {
            'average_score': round(average_score, 2),
            'grade_distribution': grade_distribution,
            'total_tests': len(tests)
        }
    
    def _calculate_average_efficiency(self, batches):
        """Calculate average efficiency for a list of batches"""
        if not batches:
            return 0
        
        total_efficiency = sum(batch.efficiency_score or 0 for batch in batches)
        return round(total_efficiency / len(batches), 2)
    
    def _get_daily_production_data(self, start_date, days):
        """Get daily production data for analytics"""
        daily_data = []
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            
            batches = tq(ProductionBatch).filter(
                and_(
                    ProductionBatch.status == 'completed',
                    func.date(ProductionBatch.end_time) == date.date()
                )
            ).all()
            
            daily_data.append({
                'date': date.date().isoformat(),
                'batches': len(batches),
                'input_quantity': sum(b.input_quantity for b in batches),
                'output_quantity': sum(b.output_quantity or 0 for b in batches),
                'average_efficiency': self._calculate_average_efficiency(batches)
            })
        
        return daily_data
    
    def _get_efficiency_trend(self, batches):
        """Get efficiency trend data"""
        if not batches:
            return []
        
        # Group by date and calculate daily average efficiency
        daily_efficiency = {}
        for batch in batches:
            if batch.end_time and batch.efficiency_score:
                date = batch.end_time.date()
                if date not in daily_efficiency:
                    daily_efficiency[date] = []
                daily_efficiency[date].append(batch.efficiency_score)
        
        trend_data = []
        for date, efficiencies in sorted(daily_efficiency.items()):
            avg_efficiency = sum(efficiencies) / len(efficiencies)
            trend_data.append({
                'date': date.isoformat(),
                'efficiency': round(avg_efficiency, 2)
            })
        
        return trend_data
    
    def _get_quality_trend(self, start_date):
        """Get quality trend data"""
        tests = tq(QualityTest).filter(
            QualityTest.test_date >= start_date
        ).all()
        
        daily_quality = {}
        for test in tests:
            if test.quality_score:
                date = test.test_date.date()
                if date not in daily_quality:
                    daily_quality[date] = []
                daily_quality[date].append(test.quality_score)
        
        trend_data = []
        for date, scores in sorted(daily_quality.items()):
            avg_score = sum(scores) / len(scores)
            trend_data.append({
                'date': date.isoformat(),
                'quality_score': round(avg_score, 2)
            })
        
        return trend_data
    
    def _get_variety_analysis(self, batches):
        """Get variety-wise analysis"""
        variety_data = {}
        
        for batch in batches:
            variety = batch.paddy_variety
            if variety not in variety_data:
                variety_data[variety] = {
                    'count': 0,
                    'total_input': 0,
                    'total_output': 0,
                    'total_efficiency': 0
                }
            
            variety_data[variety]['count'] += 1
            variety_data[variety]['total_input'] += batch.input_quantity
            variety_data[variety]['total_output'] += batch.output_quantity or 0
            variety_data[variety]['total_efficiency'] += batch.efficiency_score or 0
        
        # Calculate averages
        for variety, data in variety_data.items():
            if data['count'] > 0:
                data['average_efficiency'] = round(data['total_efficiency'] / data['count'], 2)
                data['yield_rate'] = round((data['total_output'] / data['total_input']) * 100, 2) if data['total_input'] > 0 else 0
        
        return variety_data
