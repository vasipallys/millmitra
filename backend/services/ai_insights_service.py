"""
AI Insights Service - Generates intelligent insights and recommendations
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import func, desc
from models.user import User
from models.production import ProductionBatch, QualityTest
from models.inventory import PaddyStock, ProductStock
from models.sales import SalesOrder, Customer
from models.finance import Payment, Expense
from extensions import db

logger = logging.getLogger(__name__)

class AIInsightsService:
    """Service for generating AI-powered insights and recommendations"""
    
    def __init__(self):
        self.insight_types = {
            'production': self._generate_production_insights,
            'quality': self._generate_quality_insights,
            'inventory': self._generate_inventory_insights,
            'sales': self._generate_sales_insights,
            'financial': self._generate_financial_insights,
            'operational': self._generate_operational_insights
        }
    
    def generate_insights(self, user: User, insight_types: List[str] = None, 
                         time_range: int = 7) -> List[Dict[str, Any]]:
        """Generate AI insights based on user role and data"""
        try:
            if insight_types is None:
                insight_types = self._get_default_insights_for_role(user.role)
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=time_range)
            
            insights = []
            
            for insight_type in insight_types:
                if insight_type in self.insight_types:
                    try:
                        insight_data = self.insight_types[insight_type](
                            user, start_date, end_date
                        )
                        if insight_data:
                            insights.extend(insight_data)
                    except Exception as e:
                        logger.error(f"Error generating {insight_type} insights: {str(e)}")
                        continue
            
            # Sort insights by priority and relevance
            insights = self._prioritize_insights(insights, user)
            
            return insights[:10]  # Return top 10 insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []
    
    def _get_default_insights_for_role(self, role: str) -> List[str]:
        """Get default insight types based on user role"""
        role_insights = {
            'admin': ['production', 'quality', 'inventory', 'sales', 'financial', 'operational'],
            'manager': ['production', 'quality', 'inventory', 'sales', 'financial'],
            'supervisor': ['production', 'quality', 'inventory', 'operational'],
            'operator': ['production', 'quality', 'operational'],
            'sales': ['sales', 'inventory', 'financial'],
            'quality_control': ['quality', 'production'],
            'finance': ['financial', 'sales', 'inventory']
        }
        
        return role_insights.get(role, ['production', 'quality', 'operational'])
    
    def _generate_production_insights(self, user: User, start_date: datetime, 
                                    end_date: datetime) -> List[Dict[str, Any]]:
        """Generate production-related insights"""
        insights = []
        
        try:
            # Production efficiency analysis
            batches = ProductionBatch.query.filter(
                ProductionBatch.start_time >= start_date,
                ProductionBatch.start_time <= end_date
            ).all()
            
            if batches:
                total_batches = len(batches)
                completed_batches = len([b for b in batches if b.status == 'completed'])
                avg_efficiency = sum([b.efficiency_percentage or 0 for b in batches]) / total_batches
                
                if avg_efficiency < 75:
                    insights.append({
                        'type': 'production',
                        'priority': 'high',
                        'title': 'Production Efficiency Below Target',
                        'description': f'Average efficiency is {avg_efficiency:.1f}%, below the 75% target',
                        'recommendation': 'Review machine maintenance schedules and operator training',
                        'impact': 'high',
                        'data': {
                            'current_efficiency': avg_efficiency,
                            'target_efficiency': 75,
                            'total_batches': total_batches,
                            'completed_batches': completed_batches
                        }
                    })
                
                # Identify best performing shifts
                shift_performance = {}
                for batch in batches:
                    shift = batch.shift or 'unknown'
                    if shift not in shift_performance:
                        shift_performance[shift] = []
                    shift_performance[shift].append(batch.efficiency_percentage or 0)
                
                if len(shift_performance) > 1:
                    best_shift = max(shift_performance.keys(), 
                                   key=lambda x: sum(shift_performance[x]) / len(shift_performance[x]))
                    best_avg = sum(shift_performance[best_shift]) / len(shift_performance[best_shift])
                    
                    insights.append({
                        'type': 'production',
                        'priority': 'medium',
                        'title': f'Best Performing Shift: {best_shift}',
                        'description': f'Shift {best_shift} has {best_avg:.1f}% average efficiency',
                        'recommendation': 'Analyze best practices from this shift and apply to others',
                        'impact': 'medium',
                        'data': {
                            'best_shift': best_shift,
                            'best_efficiency': best_avg,
                            'shift_performance': shift_performance
                        }
                    })
            
        except Exception as e:
            logger.error(f"Error generating production insights: {str(e)}")
        
        return insights
    
    def _generate_quality_insights(self, user: User, start_date: datetime, 
                                 end_date: datetime) -> List[Dict[str, Any]]:
        """Generate quality-related insights"""
        insights = []
        
        try:
            # Quality trend analysis
            quality_tests = QualityTest.query.filter(
                QualityTest.test_date >= start_date,
                QualityTest.test_date <= end_date
            ).all()
            
            if quality_tests:
                grade_distribution = {}
                for test in quality_tests:
                    grade = test.grade or 'unknown'
                    grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
                
                total_tests = len(quality_tests)
                premium_percentage = (grade_distribution.get('A', 0) / total_tests) * 100
                
                if premium_percentage < 60:
                    insights.append({
                        'type': 'quality',
                        'priority': 'high',
                        'title': 'Low Premium Grade Production',
                        'description': f'Only {premium_percentage:.1f}% of production is Grade A',
                        'recommendation': 'Review paddy selection criteria and processing parameters',
                        'impact': 'high',
                        'data': {
                            'premium_percentage': premium_percentage,
                            'grade_distribution': grade_distribution,
                            'total_tests': total_tests
                        }
                    })
                
                # Moisture content analysis
                moisture_levels = [test.moisture_content for test in quality_tests 
                                 if test.moisture_content is not None]
                if moisture_levels:
                    avg_moisture = sum(moisture_levels) / len(moisture_levels)
                    if avg_moisture > 14:
                        insights.append({
                            'type': 'quality',
                            'priority': 'medium',
                            'title': 'High Moisture Content Detected',
                            'description': f'Average moisture content is {avg_moisture:.1f}%',
                            'recommendation': 'Improve drying process or adjust storage conditions',
                            'impact': 'medium',
                            'data': {
                                'average_moisture': avg_moisture,
                                'target_moisture': 14,
                                'samples_tested': len(moisture_levels)
                            }
                        })
            
        except Exception as e:
            logger.error(f"Error generating quality insights: {str(e)}")
        
        return insights
    
    def _generate_inventory_insights(self, user: User, start_date: datetime, 
                                   end_date: datetime) -> List[Dict[str, Any]]:
        """Generate inventory-related insights"""
        insights = []
        
        try:
            # Low stock alerts
            low_stock_products = ProductStock.query.filter(
                ProductStock.quantity < ProductStock.minimum_stock_level
            ).all()
            
            if low_stock_products:
                insights.append({
                    'type': 'inventory',
                    'priority': 'high',
                    'title': f'{len(low_stock_products)} Products Below Minimum Stock',
                    'description': 'Critical stock levels detected for multiple products',
                    'recommendation': 'Schedule immediate production or procurement',
                    'impact': 'high',
                    'data': {
                        'low_stock_count': len(low_stock_products),
                        'products': [{'name': p.product_name, 'current': p.quantity, 
                                    'minimum': p.minimum_stock_level} for p in low_stock_products]
                    }
                })
            
            # Aging paddy stock
            aging_paddy = PaddyStock.query.filter(
                PaddyStock.purchase_date < datetime.utcnow() - timedelta(days=30),
                PaddyStock.quantity > 0
            ).all()
            
            if aging_paddy:
                total_aging_value = sum([p.quantity * p.purchase_price for p in aging_paddy])
                insights.append({
                    'type': 'inventory',
                    'priority': 'medium',
                    'title': f'Aging Paddy Stock Worth ₹{total_aging_value:,.0f}',
                    'description': f'{len(aging_paddy)} paddy lots are over 30 days old',
                    'recommendation': 'Prioritize processing of aging stock to prevent quality degradation',
                    'impact': 'medium',
                    'data': {
                        'aging_lots': len(aging_paddy),
                        'total_value': total_aging_value,
                        'oldest_date': min([p.purchase_date for p in aging_paddy]).isoformat()
                    }
                })
            
        except Exception as e:
            logger.error(f"Error generating inventory insights: {str(e)}")
        
        return insights
    
    def _generate_sales_insights(self, user: User, start_date: datetime, 
                               end_date: datetime) -> List[Dict[str, Any]]:
        """Generate sales-related insights"""
        insights = []
        
        try:
            # Sales performance analysis
            orders = SalesOrder.query.filter(
                SalesOrder.order_date >= start_date,
                SalesOrder.order_date <= end_date
            ).all()
            
            if orders:
                total_revenue = sum([order.total_amount for order in orders])
                avg_order_value = total_revenue / len(orders)
                
                # Customer concentration analysis
                customer_revenue = {}
                for order in orders:
                    customer_id = order.customer_id
                    customer_revenue[customer_id] = customer_revenue.get(customer_id, 0) + order.total_amount
                
                top_customer_revenue = max(customer_revenue.values()) if customer_revenue else 0
                concentration_percentage = (top_customer_revenue / total_revenue) * 100 if total_revenue > 0 else 0
                
                if concentration_percentage > 40:
                    insights.append({
                        'type': 'sales',
                        'priority': 'medium',
                        'title': 'High Customer Concentration Risk',
                        'description': f'Top customer represents {concentration_percentage:.1f}% of revenue',
                        'recommendation': 'Diversify customer base to reduce dependency risk',
                        'impact': 'medium',
                        'data': {
                            'concentration_percentage': concentration_percentage,
                            'total_revenue': total_revenue,
                            'customer_count': len(customer_revenue)
                        }
                    })
            
        except Exception as e:
            logger.error(f"Error generating sales insights: {str(e)}")
        
        return insights
    
    def _generate_financial_insights(self, user: User, start_date: datetime, 
                                   end_date: datetime) -> List[Dict[str, Any]]:
        """Generate financial insights"""
        insights = []
        
        try:
            # Cash flow analysis
            payments = Payment.query.filter(
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            ).all()
            
            expenses = Expense.query.filter(
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date
            ).all()
            
            total_inflow = sum([p.amount for p in payments if p.payment_type == 'received'])
            total_outflow = sum([p.amount for p in payments if p.payment_type == 'paid']) + \
                           sum([e.amount for e in expenses])
            
            net_cash_flow = total_inflow - total_outflow
            
            if net_cash_flow < 0:
                insights.append({
                    'type': 'financial',
                    'priority': 'high',
                    'title': f'Negative Cash Flow: ₹{abs(net_cash_flow):,.0f}',
                    'description': 'Cash outflow exceeds inflow in the selected period',
                    'recommendation': 'Review payment terms and expense optimization opportunities',
                    'impact': 'high',
                    'data': {
                        'net_cash_flow': net_cash_flow,
                        'total_inflow': total_inflow,
                        'total_outflow': total_outflow
                    }
                })
            
        except Exception as e:
            logger.error(f"Error generating financial insights: {str(e)}")
        
        return insights
    
    def _generate_operational_insights(self, user: User, start_date: datetime, 
                                     end_date: datetime) -> List[Dict[str, Any]]:
        """Generate operational insights"""
        insights = []
        
        try:
            # Machine utilization analysis
            batches = ProductionBatch.query.filter(
                ProductionBatch.start_time >= start_date,
                ProductionBatch.start_time <= end_date
            ).all()
            
            if batches:
                machine_usage = {}
                for batch in batches:
                    machine = batch.machine_id or 'unknown'
                    if machine not in machine_usage:
                        machine_usage[machine] = {'batches': 0, 'total_time': 0}
                    
                    machine_usage[machine]['batches'] += 1
                    if batch.end_time and batch.start_time:
                        duration = (batch.end_time - batch.start_time).total_seconds() / 3600
                        machine_usage[machine]['total_time'] += duration
                
                # Find underutilized machines
                for machine, usage in machine_usage.items():
                    if usage['total_time'] < 40:  # Less than 40 hours in the period
                        insights.append({
                            'type': 'operational',
                            'priority': 'low',
                            'title': f'Machine {machine} Underutilized',
                            'description': f'Only {usage["total_time"]:.1f} hours of operation',
                            'recommendation': 'Consider maintenance or reallocation of workload',
                            'impact': 'low',
                            'data': {
                                'machine_id': machine,
                                'operating_hours': usage['total_time'],
                                'batch_count': usage['batches']
                            }
                        })
            
        except Exception as e:
            logger.error(f"Error generating operational insights: {str(e)}")
        
        return insights
    
    def _prioritize_insights(self, insights: List[Dict[str, Any]], user: User) -> List[Dict[str, Any]]:
        """Prioritize insights based on user role and impact"""
        priority_weights = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        impact_weights = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        # Calculate priority scores
        for insight in insights:
            priority_score = priority_weights.get(insight.get('priority', 'low'), 1)
            impact_score = impact_weights.get(insight.get('impact', 'low'), 1)
            insight['score'] = priority_score * impact_score
        
        # Sort by score (descending)
        return sorted(insights, key=lambda x: x.get('score', 0), reverse=True)
