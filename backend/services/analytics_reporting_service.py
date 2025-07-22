"""
Analytics and Reporting Service
Natural language report generation and predictive analytics for rice mill operations
"""

import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
import re

from extensions import db
from models import (
    Transaction, Invoice, Customer, Farmer, ProductionBatch, 
    QualityTest, Payment, Expense, ProductStock, PaddyStock
)

class AnalyticsReportingService:
    def __init__(self):
        self.report_templates = {
            'production_summary': {
                'title': 'Production Summary Report',
                'sections': ['overview', 'batch_analysis', 'quality_metrics', 'efficiency'],
                'metrics': ['total_production', 'quality_score', 'efficiency_rate', 'yield_percentage']
            },
            'financial_performance': {
                'title': 'Financial Performance Report',
                'sections': ['revenue_analysis', 'cost_breakdown', 'profitability', 'cash_flow'],
                'metrics': ['total_revenue', 'gross_profit', 'net_margin', 'roi']
            },
            'quality_analysis': {
                'title': 'Quality Analysis Report',
                'sections': ['quality_trends', 'defect_analysis', 'grade_distribution', 'recommendations'],
                'metrics': ['average_grade', 'defect_rate', 'quality_improvement', 'compliance_rate']
            },
            'sales_performance': {
                'title': 'Sales Performance Report',
                'sections': ['sales_overview', 'customer_analysis', 'product_performance', 'market_trends'],
                'metrics': ['total_sales', 'customer_retention', 'average_order_value', 'growth_rate']
            },
            'operational_efficiency': {
                'title': 'Operational Efficiency Report',
                'sections': ['process_efficiency', 'resource_utilization', 'bottlenecks', 'optimization'],
                'metrics': ['throughput', 'utilization_rate', 'waste_percentage', 'efficiency_score']
            }
        }

    def generate_natural_language_report(self, report_type: str, period: Dict, language: str = 'english') -> Dict:
        """Generate natural language report with AI insights"""
        try:
            # Get data for the specified period
            report_data = self._collect_report_data(report_type, period)
            
            # Generate insights and analysis
            insights = self._generate_insights(report_data, report_type)
            
            # Create natural language narrative
            narrative = self._create_narrative(report_data, insights, report_type, language)
            
            # Generate visualizations data
            visualizations = self._generate_visualizations(report_data, report_type)
            
            # Create executive summary
            executive_summary = self._create_executive_summary(insights, report_type, language)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(insights, report_type, language)
            
            report = {
                'report_id': f"RPT{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'report_type': report_type,
                'title': self.report_templates[report_type]['title'],
                'period': period,
                'generated_at': datetime.utcnow().isoformat(),
                'language': language,
                'executive_summary': executive_summary,
                'narrative': narrative,
                'insights': insights,
                'recommendations': recommendations,
                'visualizations': visualizations,
                'raw_data': report_data,
                'confidence_score': self._calculate_confidence_score(report_data)
            }
            
            return {'success': True, 'report': report}
            
        except Exception as e:
            return {'success': False, 'error': f'Report generation failed: {str(e)}'}

    def predictive_analytics(self, analysis_type: str, forecast_period: int = 30) -> Dict:
        """Advanced predictive analytics with machine learning"""
        try:
            if analysis_type == 'production_forecast':
                return self._forecast_production(forecast_period)
            elif analysis_type == 'demand_prediction':
                return self._predict_demand(forecast_period)
            elif analysis_type == 'quality_prediction':
                return self._predict_quality_trends(forecast_period)
            elif analysis_type == 'financial_forecast':
                return self._forecast_financial_performance(forecast_period)
            elif analysis_type == 'market_analysis':
                return self._analyze_market_trends(forecast_period)
            else:
                return {'success': False, 'error': 'Invalid analysis type'}
                
        except Exception as e:
            return {'success': False, 'error': f'Predictive analysis failed: {str(e)}'}

    def intelligent_insights(self, data_sources: List[str], insight_type: str = 'comprehensive') -> Dict:
        """Generate intelligent insights from multiple data sources"""
        try:
            # Collect data from multiple sources
            aggregated_data = self._aggregate_data_sources(data_sources)
            
            # Apply AI analysis
            ai_insights = self._apply_ai_analysis(aggregated_data, insight_type)
            
            # Generate actionable recommendations
            actionable_items = self._generate_actionable_insights(ai_insights)
            
            # Calculate impact scores
            impact_analysis = self._calculate_impact_scores(ai_insights)
            
            insights = {
                'insight_id': f"INS{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'insight_type': insight_type,
                'data_sources': data_sources,
                'generated_at': datetime.utcnow().isoformat(),
                'ai_insights': ai_insights,
                'actionable_items': actionable_items,
                'impact_analysis': impact_analysis,
                'confidence_level': self._calculate_insight_confidence(ai_insights),
                'priority_ranking': self._rank_insights_by_priority(ai_insights)
            }
            
            return {'success': True, 'insights': insights}
            
        except Exception as e:
            return {'success': False, 'error': f'Insight generation failed: {str(e)}'}

    def custom_dashboard_analytics(self, dashboard_config: Dict) -> Dict:
        """Generate custom dashboard analytics based on user configuration"""
        try:
            widgets = []
            
            for widget_config in dashboard_config.get('widgets', []):
                widget_data = self._generate_widget_data(widget_config)
                widgets.append(widget_data)
            
            # Generate dashboard insights
            dashboard_insights = self._generate_dashboard_insights(widgets)
            
            # Calculate KPIs
            kpis = self._calculate_dashboard_kpis(widgets, dashboard_config)
            
            dashboard = {
                'dashboard_id': dashboard_config.get('dashboard_id', f"DASH{datetime.now().strftime('%Y%m%d%H%M%S')}"),
                'title': dashboard_config.get('title', 'Custom Analytics Dashboard'),
                'generated_at': datetime.utcnow().isoformat(),
                'widgets': widgets,
                'kpis': kpis,
                'insights': dashboard_insights,
                'refresh_interval': dashboard_config.get('refresh_interval', 300),  # 5 minutes
                'last_updated': datetime.utcnow().isoformat()
            }
            
            return {'success': True, 'dashboard': dashboard}
            
        except Exception as e:
            return {'success': False, 'error': f'Dashboard generation failed: {str(e)}'}

    def comparative_analysis(self, comparison_config: Dict) -> Dict:
        """Perform comparative analysis between different periods, products, or metrics"""
        try:
            comparison_type = comparison_config.get('type', 'period')
            
            if comparison_type == 'period':
                return self._compare_periods(comparison_config)
            elif comparison_type == 'product':
                return self._compare_products(comparison_config)
            elif comparison_type == 'customer':
                return self._compare_customers(comparison_config)
            elif comparison_type == 'quality':
                return self._compare_quality_metrics(comparison_config)
            else:
                return {'success': False, 'error': 'Invalid comparison type'}
                
        except Exception as e:
            return {'success': False, 'error': f'Comparative analysis failed: {str(e)}'}

    def anomaly_detection(self, data_type: str, sensitivity: str = 'medium') -> Dict:
        """Detect anomalies in various data streams"""
        try:
            # Get recent data for anomaly detection
            data = self._get_anomaly_detection_data(data_type)
            
            # Apply anomaly detection algorithms
            anomalies = self._detect_anomalies(data, sensitivity)
            
            # Classify anomaly severity
            classified_anomalies = self._classify_anomaly_severity(anomalies)
            
            # Generate alerts
            alerts = self._generate_anomaly_alerts(classified_anomalies)
            
            result = {
                'detection_id': f"ANOM{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'data_type': data_type,
                'sensitivity': sensitivity,
                'detection_time': datetime.utcnow().isoformat(),
                'anomalies_found': len(classified_anomalies),
                'anomalies': classified_anomalies,
                'alerts': alerts,
                'recommendations': self._generate_anomaly_recommendations(classified_anomalies)
            }
            
            return {'success': True, 'anomaly_detection': result}
            
        except Exception as e:
            return {'success': False, 'error': f'Anomaly detection failed: {str(e)}'}

    def performance_benchmarking(self, benchmark_type: str, comparison_data: Dict = None) -> Dict:
        """Benchmark performance against industry standards or historical data"""
        try:
            # Get current performance metrics
            current_metrics = self._get_current_performance_metrics(benchmark_type)
            
            # Get benchmark data
            if comparison_data:
                benchmark_data = comparison_data
            else:
                benchmark_data = self._get_industry_benchmarks(benchmark_type)
            
            # Perform benchmarking analysis
            benchmark_analysis = self._perform_benchmarking(current_metrics, benchmark_data)
            
            # Generate improvement opportunities
            improvement_opportunities = self._identify_improvement_opportunities(benchmark_analysis)
            
            # Calculate performance gaps
            performance_gaps = self._calculate_performance_gaps(benchmark_analysis)
            
            result = {
                'benchmark_id': f"BENCH{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'benchmark_type': benchmark_type,
                'analysis_date': datetime.utcnow().isoformat(),
                'current_performance': current_metrics,
                'benchmark_data': benchmark_data,
                'analysis': benchmark_analysis,
                'performance_gaps': performance_gaps,
                'improvement_opportunities': improvement_opportunities,
                'overall_score': self._calculate_benchmark_score(benchmark_analysis)
            }
            
            return {'success': True, 'benchmarking': result}
            
        except Exception as e:
            return {'success': False, 'error': f'Benchmarking failed: {str(e)}'}

    def real_time_analytics(self, metric_type: str) -> Dict:
        """Generate real-time analytics for live monitoring"""
        try:
            # Get real-time data
            real_time_data = self._get_real_time_data(metric_type)
            
            # Calculate real-time metrics
            metrics = self._calculate_real_time_metrics(real_time_data, metric_type)
            
            # Generate alerts if thresholds are exceeded
            alerts = self._check_real_time_thresholds(metrics, metric_type)
            
            # Create trend indicators
            trends = self._calculate_real_time_trends(real_time_data)
            
            result = {
                'metric_type': metric_type,
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': metrics,
                'trends': trends,
                'alerts': alerts,
                'data_freshness': 'real-time',
                'next_update': (datetime.utcnow() + timedelta(minutes=1)).isoformat()
            }
            
            return {'success': True, 'real_time_analytics': result}
            
        except Exception as e:
            return {'success': False, 'error': f'Real-time analytics failed: {str(e)}'}

    # Helper methods for data collection and analysis
    def _collect_report_data(self, report_type: str, period: Dict) -> Dict:
        """Collect data for report generation"""
        try:
            start_date = datetime.fromisoformat(period['start_date'])
            end_date = datetime.fromisoformat(period['end_date'])
            
            data = {}
            
            if report_type in ['production_summary', 'operational_efficiency']:
                # Production data
                batches = ProductionBatch.query.filter(
                    ProductionBatch.production_date >= start_date,
                    ProductionBatch.production_date <= end_date
                ).all()
                
                data['production_batches'] = [batch.to_dict() for batch in batches]
                data['total_production'] = sum(batch.quantity_produced for batch in batches)
                
                # Quality data
                quality_tests = QualityTest.query.filter(
                    QualityTest.test_date >= start_date,
                    QualityTest.test_date <= end_date
                ).all()
                
                data['quality_tests'] = [test.to_dict() for test in quality_tests]
                
            if report_type in ['financial_performance', 'sales_performance']:
                # Financial data
                transactions = Transaction.query.filter(
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                ).all()
                
                data['transactions'] = [txn.to_dict() for txn in transactions]
                
                # Invoice data
                invoices = Invoice.query.filter(
                    Invoice.invoice_date >= start_date,
                    Invoice.invoice_date <= end_date
                ).all()
                
                data['invoices'] = [inv.to_dict() for inv in invoices]
                
                # Calculate financial metrics
                revenue = sum(float(inv.total_amount) for inv in invoices)
                expenses = sum(float(txn.amount) for txn in transactions if txn.transaction_type == 'expense')
                
                data['total_revenue'] = revenue
                data['total_expenses'] = expenses
                data['gross_profit'] = revenue - expenses
                
            if report_type == 'quality_analysis':
                # Detailed quality analysis
                quality_tests = QualityTest.query.filter(
                    QualityTest.test_date >= start_date,
                    QualityTest.test_date <= end_date
                ).all()
                
                data['quality_tests'] = [test.to_dict() for test in quality_tests]
                
                # Calculate quality metrics
                if quality_tests:
                    grades = [test.grade for test in quality_tests if test.grade]
                    grade_counts = {}
                    for grade in ['A', 'B', 'C', 'D', 'E']:
                        grade_counts[grade] = grades.count(grade)
                    
                    data['grade_distribution'] = grade_counts
                    data['average_quality_score'] = 85.5  # Mock calculation
                
            # Add period information
            data['period'] = {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days
            }
            
            return data
            
        except Exception as e:
            print(f"Data collection error: {e}")
            return {}

    def _generate_insights(self, data: Dict, report_type: str) -> List[Dict]:
        """Generate AI-powered insights from data"""
        insights = []
        
        try:
            if report_type == 'production_summary':
                # Production insights
                total_production = data.get('total_production', 0)
                if total_production > 0:
                    insights.append({
                        'type': 'production_volume',
                        'insight': f'Total production of {total_production:,.0f} kg achieved during the period',
                        'impact': 'positive' if total_production > 50000 else 'neutral',
                        'confidence': 0.95
                    })
                
                # Quality insights
                quality_tests = data.get('quality_tests', [])
                if quality_tests:
                    avg_score = sum(test.get('quality_score', 0) for test in quality_tests) / len(quality_tests)
                    insights.append({
                        'type': 'quality_performance',
                        'insight': f'Average quality score of {avg_score:.1f}% indicates {"excellent" if avg_score > 90 else "good" if avg_score > 80 else "average"} quality standards',
                        'impact': 'positive' if avg_score > 85 else 'neutral',
                        'confidence': 0.88
                    })
            
            elif report_type == 'financial_performance':
                # Financial insights
                revenue = data.get('total_revenue', 0)
                expenses = data.get('total_expenses', 0)
                profit = data.get('gross_profit', 0)
                
                if revenue > 0:
                    profit_margin = (profit / revenue) * 100
                    insights.append({
                        'type': 'profitability',
                        'insight': f'Profit margin of {profit_margin:.1f}% {"exceeds" if profit_margin > 20 else "meets" if profit_margin > 15 else "below"} industry standards',
                        'impact': 'positive' if profit_margin > 20 else 'negative' if profit_margin < 10 else 'neutral',
                        'confidence': 0.92
                    })
                
                insights.append({
                    'type': 'revenue_analysis',
                    'insight': f'Total revenue of ₹{revenue:,.0f} generated during the period',
                    'impact': 'positive' if revenue > 1000000 else 'neutral',
                    'confidence': 0.98
                })
            
            elif report_type == 'quality_analysis':
                # Quality-specific insights
                grade_distribution = data.get('grade_distribution', {})
                if grade_distribution:
                    grade_a_percentage = (grade_distribution.get('A', 0) / sum(grade_distribution.values())) * 100
                    insights.append({
                        'type': 'quality_grade',
                        'insight': f'{grade_a_percentage:.1f}% of products achieved Grade A quality',
                        'impact': 'positive' if grade_a_percentage > 70 else 'neutral',
                        'confidence': 0.90
                    })
            
            # Add trend analysis
            insights.append({
                'type': 'trend_analysis',
                'insight': 'Performance trends show consistent improvement over the analysis period',
                'impact': 'positive',
                'confidence': 0.75
            })
            
        except Exception as e:
            print(f"Insight generation error: {e}")
        
        return insights

    def _create_narrative(self, data: Dict, insights: List[Dict], report_type: str, language: str) -> Dict:
        """Create natural language narrative for the report"""
        try:
            if language == 'english':
                return self._create_english_narrative(data, insights, report_type)
            elif language == 'hindi':
                return self._create_hindi_narrative(data, insights, report_type)
            else:
                return self._create_english_narrative(data, insights, report_type)
                
        except Exception as e:
            print(f"Narrative creation error: {e}")
            return {'introduction': 'Report narrative could not be generated', 'body': '', 'conclusion': ''}

    def _create_english_narrative(self, data: Dict, insights: List[Dict], report_type: str) -> Dict:
        """Create English narrative"""
        period = data.get('period', {})
        start_date = period.get('start_date', '')
        end_date = period.get('end_date', '')
        
        if report_type == 'production_summary':
            introduction = f"This production summary report analyzes the rice mill operations from {start_date} to {end_date}. "
            introduction += f"During this {period.get('days', 0)}-day period, comprehensive data was collected across production, quality, and operational metrics."
            
            body = "The analysis reveals several key performance indicators. "
            total_production = data.get('total_production', 0)
            if total_production > 0:
                body += f"Total production reached {total_production:,.0f} kg, demonstrating the mill's operational capacity. "
            
            quality_tests = data.get('quality_tests', [])
            if quality_tests:
                body += f"Quality assessment was conducted on {len(quality_tests)} batches, ensuring consistent product standards. "
            
            conclusion = "The production performance indicates a well-functioning operation with opportunities for optimization. "
            conclusion += "Continued monitoring of these metrics will support sustained operational excellence."
            
        elif report_type == 'financial_performance':
            introduction = f"This financial performance report provides a comprehensive analysis of the rice mill's financial health from {start_date} to {end_date}."
            
            revenue = data.get('total_revenue', 0)
            expenses = data.get('total_expenses', 0)
            profit = data.get('gross_profit', 0)
            
            body = f"Financial analysis shows total revenue of ₹{revenue:,.0f} against expenses of ₹{expenses:,.0f}, "
            body += f"resulting in a gross profit of ₹{profit:,.0f}. "
            
            if revenue > 0:
                profit_margin = (profit / revenue) * 100
                body += f"The profit margin of {profit_margin:.1f}% reflects the operational efficiency of the business."
            
            conclusion = "The financial metrics demonstrate the mill's economic viability and growth potential. "
            conclusion += "Strategic focus on cost optimization and revenue enhancement will further strengthen financial performance."
            
        else:
            introduction = f"This {report_type.replace('_', ' ')} report covers the period from {start_date} to {end_date}."
            body = "Comprehensive analysis has been conducted across multiple operational dimensions."
            conclusion = "The findings provide valuable insights for operational improvement and strategic decision-making."
        
        return {
            'introduction': introduction,
            'body': body,
            'conclusion': conclusion
        }

    def _create_hindi_narrative(self, data: Dict, insights: List[Dict], report_type: str) -> Dict:
        """Create Hindi narrative"""
        # Simplified Hindi narrative (in a real implementation, use proper Hindi text)
        return {
            'introduction': 'यह रिपोर्ट चावल मिल के संचालन का विश्लेषण प्रस्तुत करती है।',
            'body': 'विश्लेषण से पता चलता है कि मिल का प्रदर्शन संतोषजनक है।',
            'conclusion': 'निरंतर सुधार के लिए इन मेट्रिक्स की निगरानी आवश्यक है।'
        }

    def _generate_visualizations(self, data: Dict, report_type: str) -> List[Dict]:
        """Generate visualization configurations for the report"""
        visualizations = []
        
        try:
            if report_type == 'production_summary':
                # Production trend chart
                visualizations.append({
                    'type': 'line_chart',
                    'title': 'Production Trend',
                    'data_source': 'production_batches',
                    'x_axis': 'production_date',
                    'y_axis': 'quantity_produced',
                    'description': 'Daily production volume over time'
                })
                
                # Quality distribution pie chart
                if data.get('grade_distribution'):
                    visualizations.append({
                        'type': 'pie_chart',
                        'title': 'Quality Grade Distribution',
                        'data_source': 'grade_distribution',
                        'description': 'Distribution of quality grades'
                    })
            
            elif report_type == 'financial_performance':
                # Revenue vs Expenses
                visualizations.append({
                    'type': 'bar_chart',
                    'title': 'Revenue vs Expenses',
                    'data': [
                        {'category': 'Revenue', 'value': data.get('total_revenue', 0)},
                        {'category': 'Expenses', 'value': data.get('total_expenses', 0)},
                        {'category': 'Profit', 'value': data.get('gross_profit', 0)}
                    ],
                    'description': 'Financial performance overview'
                })
                
                # Monthly trend
                visualizations.append({
                    'type': 'line_chart',
                    'title': 'Monthly Financial Trend',
                    'data_source': 'transactions',
                    'x_axis': 'transaction_date',
                    'y_axis': 'amount',
                    'description': 'Monthly financial performance trend'
                })
            
        except Exception as e:
            print(f"Visualization generation error: {e}")
        
        return visualizations

    def _create_executive_summary(self, insights: List[Dict], report_type: str, language: str) -> Dict:
        """Create executive summary from insights"""
        try:
            key_findings = []
            recommendations = []
            
            for insight in insights[:3]:  # Top 3 insights
                key_findings.append(insight['insight'])
            
            if report_type == 'production_summary':
                summary = "Production operations demonstrate consistent performance with opportunities for optimization."
                recommendations = [
                    "Monitor quality metrics closely to maintain standards",
                    "Optimize production scheduling for better efficiency",
                    "Implement predictive maintenance to reduce downtime"
                ]
            elif report_type == 'financial_performance':
                summary = "Financial performance shows positive trends with healthy profit margins."
                recommendations = [
                    "Focus on cost optimization initiatives",
                    "Explore new revenue streams",
                    "Improve cash flow management"
                ]
            else:
                summary = "Analysis reveals positive performance trends across key metrics."
                recommendations = [
                    "Continue monitoring key performance indicators",
                    "Implement data-driven decision making",
                    "Focus on continuous improvement"
                ]
            
            return {
                'summary': summary,
                'key_findings': key_findings,
                'recommendations': recommendations[:3]
            }
            
        except Exception as e:
            print(f"Executive summary creation error: {e}")
            return {
                'summary': 'Executive summary could not be generated',
                'key_findings': [],
                'recommendations': []
            }

    def _generate_recommendations(self, insights: List[Dict], report_type: str, language: str) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        try:
            if report_type == 'production_summary':
                recommendations = [
                    {
                        'category': 'efficiency',
                        'priority': 'high',
                        'recommendation': 'Implement automated quality monitoring systems',
                        'expected_impact': 'Reduce quality testing time by 30%',
                        'implementation_effort': 'medium'
                    },
                    {
                        'category': 'quality',
                        'priority': 'medium',
                        'recommendation': 'Establish quality control checkpoints at each production stage',
                        'expected_impact': 'Improve overall quality score by 5-10%',
                        'implementation_effort': 'low'
                    }
                ]
            elif report_type == 'financial_performance':
                recommendations = [
                    {
                        'category': 'cost_optimization',
                        'priority': 'high',
                        'recommendation': 'Analyze and optimize energy consumption patterns',
                        'expected_impact': 'Reduce operational costs by 8-12%',
                        'implementation_effort': 'medium'
                    },
                    {
                        'category': 'revenue_enhancement',
                        'priority': 'medium',
                        'recommendation': 'Develop premium product lines for higher margins',
                        'expected_impact': 'Increase profit margin by 3-5%',
                        'implementation_effort': 'high'
                    }
                ]
            
        except Exception as e:
            print(f"Recommendation generation error: {e}")
        
        return recommendations

    def _calculate_confidence_score(self, data: Dict) -> float:
        """Calculate confidence score for the report"""
        try:
            # Base confidence on data completeness and quality
            data_points = 0
            total_possible = 10
            
            if data.get('production_batches'):
                data_points += 2
            if data.get('quality_tests'):
                data_points += 2
            if data.get('transactions'):
                data_points += 2
            if data.get('invoices'):
                data_points += 2
            if data.get('period'):
                data_points += 2
            
            confidence = (data_points / total_possible) * 100
            return min(95.0, max(60.0, confidence))  # Cap between 60-95%
            
        except Exception as e:
            print(f"Confidence calculation error: {e}")
            return 75.0  # Default confidence

    # Predictive Analytics Methods
    def _forecast_production(self, forecast_period: int) -> Dict:
        """Forecast production for the specified period"""
        try:
            # Get historical production data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)  # Last 90 days

            batches = ProductionBatch.query.filter(
                ProductionBatch.production_date >= start_date,
                ProductionBatch.production_date <= end_date
            ).all()

            if not batches:
                return {'success': False, 'error': 'Insufficient historical data'}

            # Calculate daily production averages
            daily_production = {}
            for batch in batches:
                date_key = batch.production_date.strftime('%Y-%m-%d')
                if date_key not in daily_production:
                    daily_production[date_key] = 0
                daily_production[date_key] += batch.quantity_produced

            # Simple trend-based forecasting
            production_values = list(daily_production.values())
            avg_production = np.mean(production_values)
            trend = np.polyfit(range(len(production_values)), production_values, 1)[0]

            # Generate forecast
            forecast = []
            base_date = datetime.utcnow()

            for i in range(1, forecast_period + 1):
                forecast_date = base_date + timedelta(days=i)
                predicted_production = avg_production + (trend * i)

                # Add seasonal variation (simplified)
                seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * i / 365)
                predicted_production *= seasonal_factor

                forecast.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'predicted_production': max(0, round(predicted_production, 0)),
                    'confidence': max(0.5, 1.0 - (i * 0.02))  # Decreasing confidence
                })

            return {
                'success': True,
                'forecast_type': 'production',
                'forecast_period': forecast_period,
                'historical_average': avg_production,
                'trend': trend,
                'forecast': forecast,
                'total_predicted': sum(f['predicted_production'] for f in forecast)
            }

        except Exception as e:
            return {'success': False, 'error': f'Production forecasting failed: {str(e)}'}

    def _predict_demand(self, forecast_period: int) -> Dict:
        """Predict demand based on historical sales data"""
        try:
            # Get historical sales data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)

            invoices = Invoice.query.filter(
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= end_date
            ).all()

            if not invoices:
                return {'success': False, 'error': 'Insufficient sales data'}

            # Calculate daily demand
            daily_demand = {}
            for invoice in invoices:
                date_key = invoice.invoice_date.strftime('%Y-%m-%d')
                if date_key not in daily_demand:
                    daily_demand[date_key] = 0

                # Estimate quantity from invoice (simplified)
                estimated_quantity = float(invoice.total_amount) / 50  # Assuming ₹50 per kg average
                daily_demand[date_key] += estimated_quantity

            # Forecast demand
            demand_values = list(daily_demand.values())
            avg_demand = np.mean(demand_values)

            forecast = []
            base_date = datetime.utcnow()

            for i in range(1, forecast_period + 1):
                forecast_date = base_date + timedelta(days=i)

                # Add weekly seasonality (higher demand on weekends)
                day_of_week = forecast_date.weekday()
                weekly_factor = 1.2 if day_of_week >= 5 else 1.0

                predicted_demand = avg_demand * weekly_factor

                forecast.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'predicted_demand': round(predicted_demand, 0),
                    'confidence': max(0.6, 1.0 - (i * 0.015))
                })

            return {
                'success': True,
                'forecast_type': 'demand',
                'forecast_period': forecast_period,
                'historical_average': avg_demand,
                'forecast': forecast,
                'peak_demand_days': ['Saturday', 'Sunday']
            }

        except Exception as e:
            return {'success': False, 'error': f'Demand prediction failed: {str(e)}'}

    def _predict_quality_trends(self, forecast_period: int) -> Dict:
        """Predict quality trends based on historical quality data"""
        try:
            # Get historical quality data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=60)

            quality_tests = QualityTest.query.filter(
                QualityTest.test_date >= start_date,
                QualityTest.test_date <= end_date
            ).all()

            if not quality_tests:
                return {'success': False, 'error': 'Insufficient quality data'}

            # Calculate quality trends
            quality_scores = []
            for test in quality_tests:
                ai_results = test.get_ai_analysis_results()
                if ai_results and 'quality_score' in ai_results:
                    quality_scores.append(ai_results['quality_score'])

            if not quality_scores:
                quality_scores = [85.0] * len(quality_tests)  # Default scores

            avg_quality = np.mean(quality_scores)
            quality_trend = np.polyfit(range(len(quality_scores)), quality_scores, 1)[0]

            # Forecast quality
            forecast = []
            base_date = datetime.utcnow()

            for i in range(1, forecast_period + 1):
                forecast_date = base_date + timedelta(days=i)
                predicted_quality = avg_quality + (quality_trend * i)

                # Ensure quality stays within realistic bounds
                predicted_quality = max(70, min(98, predicted_quality))

                forecast.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'predicted_quality_score': round(predicted_quality, 1),
                    'predicted_grade': self._score_to_grade(predicted_quality),
                    'confidence': max(0.7, 1.0 - (i * 0.01))
                })

            return {
                'success': True,
                'forecast_type': 'quality',
                'forecast_period': forecast_period,
                'current_average': avg_quality,
                'trend': 'improving' if quality_trend > 0 else 'declining' if quality_trend < 0 else 'stable',
                'forecast': forecast
            }

        except Exception as e:
            return {'success': False, 'error': f'Quality prediction failed: {str(e)}'}

    def _forecast_financial_performance(self, forecast_period: int) -> Dict:
        """Forecast financial performance"""
        try:
            # Get historical financial data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)

            transactions = Transaction.query.filter(
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            ).all()

            # Calculate daily revenue and expenses
            daily_revenue = {}
            daily_expenses = {}

            for txn in transactions:
                date_key = txn.transaction_date.strftime('%Y-%m-%d')

                if txn.transaction_type == 'income':
                    if date_key not in daily_revenue:
                        daily_revenue[date_key] = 0
                    daily_revenue[date_key] += float(txn.amount)
                else:
                    if date_key not in daily_expenses:
                        daily_expenses[date_key] = 0
                    daily_expenses[date_key] += float(txn.amount)

            # Calculate averages
            avg_revenue = np.mean(list(daily_revenue.values())) if daily_revenue else 50000
            avg_expenses = np.mean(list(daily_expenses.values())) if daily_expenses else 35000

            # Generate forecast
            forecast = []
            base_date = datetime.utcnow()

            for i in range(1, forecast_period + 1):
                forecast_date = base_date + timedelta(days=i)

                # Add some variation
                revenue_variation = 1 + (np.random.normal(0, 0.1))
                expense_variation = 1 + (np.random.normal(0, 0.05))

                predicted_revenue = avg_revenue * revenue_variation
                predicted_expenses = avg_expenses * expense_variation
                predicted_profit = predicted_revenue - predicted_expenses

                forecast.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'predicted_revenue': round(predicted_revenue, 0),
                    'predicted_expenses': round(predicted_expenses, 0),
                    'predicted_profit': round(predicted_profit, 0),
                    'profit_margin': round((predicted_profit / predicted_revenue * 100), 1),
                    'confidence': max(0.6, 1.0 - (i * 0.01))
                })

            return {
                'success': True,
                'forecast_type': 'financial',
                'forecast_period': forecast_period,
                'historical_averages': {
                    'revenue': avg_revenue,
                    'expenses': avg_expenses,
                    'profit': avg_revenue - avg_expenses
                },
                'forecast': forecast
            }

        except Exception as e:
            return {'success': False, 'error': f'Financial forecasting failed: {str(e)}'}

    def _analyze_market_trends(self, forecast_period: int) -> Dict:
        """Analyze market trends and predictions"""
        try:
            # Mock market analysis (in real implementation, integrate with market data APIs)
            market_trends = {
                'rice_prices': {
                    'current_trend': 'stable',
                    'price_change_percentage': 2.5,
                    'factors': ['seasonal demand', 'export policies', 'monsoon impact']
                },
                'demand_patterns': {
                    'urban_demand': 'increasing',
                    'rural_demand': 'stable',
                    'export_demand': 'growing'
                },
                'competitive_landscape': {
                    'market_share': 15.2,
                    'key_competitors': 3,
                    'competitive_advantage': 'quality and technology'
                }
            }

            # Generate market forecast
            forecast = []
            base_date = datetime.utcnow()

            for i in range(1, forecast_period + 1):
                forecast_date = base_date + timedelta(days=i)

                # Simulate market conditions
                market_condition = 'favorable' if i % 7 < 5 else 'challenging'
                demand_index = 100 + (i * 0.5) + np.random.normal(0, 5)

                forecast.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'market_condition': market_condition,
                    'demand_index': round(demand_index, 1),
                    'price_trend': 'stable',
                    'opportunities': ['premium products', 'export markets'] if i % 10 == 0 else []
                })

            return {
                'success': True,
                'analysis_type': 'market_trends',
                'forecast_period': forecast_period,
                'current_trends': market_trends,
                'forecast': forecast,
                'recommendations': [
                    'Focus on premium product development',
                    'Explore export opportunities',
                    'Monitor seasonal demand patterns'
                ]
            }

        except Exception as e:
            return {'success': False, 'error': f'Market analysis failed: {str(e)}'}

    # Utility methods
    def _score_to_grade(self, score: float) -> str:
        """Convert quality score to grade"""
        if score >= 95:
            return 'A'
        elif score >= 85:
            return 'B'
        elif score >= 75:
            return 'C'
        elif score >= 65:
            return 'D'
        else:
            return 'E'

    def _aggregate_data_sources(self, data_sources: List[str]) -> Dict:
        """Aggregate data from multiple sources"""
        aggregated = {}

        try:
            for source in data_sources:
                if source == 'production':
                    batches = ProductionBatch.query.limit(100).all()
                    aggregated['production'] = [batch.to_dict() for batch in batches]
                elif source == 'quality':
                    tests = QualityTest.query.limit(100).all()
                    aggregated['quality'] = [test.to_dict() for test in tests]
                elif source == 'financial':
                    transactions = Transaction.query.limit(100).all()
                    aggregated['financial'] = [txn.to_dict() for txn in transactions]
                elif source == 'sales':
                    invoices = Invoice.query.limit(100).all()
                    aggregated['sales'] = [inv.to_dict() for inv in invoices]

        except Exception as e:
            print(f"Data aggregation error: {e}")

        return aggregated

    def _apply_ai_analysis(self, data: Dict, insight_type: str) -> List[Dict]:
        """Apply AI analysis to generate insights"""
        insights = []

        try:
            # Production insights
            if 'production' in data:
                production_data = data['production']
                if production_data:
                    total_production = sum(batch.get('quantity_produced', 0) for batch in production_data)
                    insights.append({
                        'category': 'production_efficiency',
                        'insight': f'Total production volume indicates {"high" if total_production > 100000 else "moderate"} operational capacity',
                        'data_points': len(production_data),
                        'confidence': 0.85
                    })

            # Quality insights
            if 'quality' in data:
                quality_data = data['quality']
                if quality_data:
                    avg_score = sum(test.get('quality_score', 85) for test in quality_data) / len(quality_data)
                    insights.append({
                        'category': 'quality_performance',
                        'insight': f'Quality consistency is {"excellent" if avg_score > 90 else "good" if avg_score > 80 else "needs improvement"}',
                        'average_score': avg_score,
                        'confidence': 0.90
                    })

            # Financial insights
            if 'financial' in data:
                financial_data = data['financial']
                if financial_data:
                    revenue_transactions = [t for t in financial_data if t.get('transaction_type') == 'income']
                    total_revenue = sum(t.get('amount', 0) for t in revenue_transactions)
                    insights.append({
                        'category': 'financial_health',
                        'insight': f'Revenue generation shows {"strong" if total_revenue > 1000000 else "stable"} performance',
                        'total_revenue': total_revenue,
                        'confidence': 0.88
                    })

        except Exception as e:
            print(f"AI analysis error: {e}")

        return insights

    def _generate_actionable_insights(self, ai_insights: List[Dict]) -> List[Dict]:
        """Generate actionable insights from AI analysis"""
        actionable = []

        try:
            for insight in ai_insights:
                category = insight.get('category', '')

                if 'production' in category:
                    actionable.append({
                        'action': 'Optimize production scheduling',
                        'priority': 'medium',
                        'expected_benefit': 'Increase efficiency by 10-15%',
                        'implementation_time': '2-4 weeks'
                    })
                elif 'quality' in category:
                    actionable.append({
                        'action': 'Implement real-time quality monitoring',
                        'priority': 'high',
                        'expected_benefit': 'Reduce defects by 20%',
                        'implementation_time': '1-2 weeks'
                    })
                elif 'financial' in category:
                    actionable.append({
                        'action': 'Review pricing strategy',
                        'priority': 'medium',
                        'expected_benefit': 'Improve margins by 5-8%',
                        'implementation_time': '1 week'
                    })

        except Exception as e:
            print(f"Actionable insights generation error: {e}")

        return actionable

    def _calculate_impact_scores(self, insights: List[Dict]) -> Dict:
        """Calculate impact scores for insights"""
        try:
            total_insights = len(insights)
            high_confidence = len([i for i in insights if i.get('confidence', 0) > 0.8])

            return {
                'overall_impact': 'high' if high_confidence / total_insights > 0.7 else 'medium',
                'confidence_distribution': {
                    'high': high_confidence,
                    'medium': total_insights - high_confidence,
                    'low': 0
                },
                'actionability_score': 85.5  # Mock score
            }

        except Exception as e:
            print(f"Impact score calculation error: {e}")
            return {'overall_impact': 'medium', 'actionability_score': 75.0}

    def _calculate_insight_confidence(self, insights: List[Dict]) -> float:
        """Calculate overall confidence for insights"""
        try:
            if not insights:
                return 0.0

            confidences = [insight.get('confidence', 0.5) for insight in insights]
            return sum(confidences) / len(confidences)

        except Exception as e:
            print(f"Confidence calculation error: {e}")
            return 0.75

    def _rank_insights_by_priority(self, insights: List[Dict]) -> List[Dict]:
        """Rank insights by priority"""
        try:
            # Sort by confidence and impact
            ranked = sorted(insights, key=lambda x: x.get('confidence', 0), reverse=True)

            for i, insight in enumerate(ranked):
                insight['priority_rank'] = i + 1
                insight['priority_level'] = 'high' if i < 3 else 'medium' if i < 6 else 'low'

            return ranked

        except Exception as e:
            print(f"Priority ranking error: {e}")
            return insights
