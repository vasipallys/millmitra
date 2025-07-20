import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

class QualityAI:
    def __init__(self):
        self.quality_thresholds = {
            'A': {'min_score': 90, 'max_defects': 2},
            'B': {'min_score': 80, 'max_defects': 5},
            'C': {'min_score': 70, 'max_defects': 8},
            'D': {'min_score': 60, 'max_defects': 12}
        }
    
    def analyze_quality_test(self, test_data: Dict) -> Dict:
        """Comprehensive AI analysis of quality test results"""
        try:
            # Calculate quality score
            quality_score = self._calculate_quality_score(test_data)
            
            # Determine grade
            grade = self._determine_grade(quality_score, test_data)
            
            # Detect anomalies
            anomalies = self._detect_anomalies(test_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(test_data, quality_score, anomalies)
            
            # Risk assessment
            risk_assessment = self._assess_quality_risk(test_data, anomalies)
            
            return {
                'quality_score': quality_score,
                'recommended_grade': grade,
                'anomalies_detected': anomalies,
                'recommendations': recommendations,
                'risk_assessment': risk_assessment,
                'confidence': self._calculate_confidence(test_data),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            return {
                'quality_score': 50,
                'recommended_grade': 'C',
                'anomalies_detected': [],
                'recommendations': ['Manual review required'],
                'risk_assessment': {'level': 'medium', 'factors': ['Analysis error']},
                'confidence': 0.5,
                'error': str(e)
            }
    
    def _calculate_quality_score(self, test_data: Dict) -> float:
        """Calculate overall quality score based on test parameters"""
        scores = []
        weights = {
            'moisture_content': 0.2,
            'broken_grains': 0.15,
            'foreign_matter': 0.15,
            'chalky_grains': 0.1,
            'damaged_grains': 0.1,
            'grain_length': 0.1,
            'grain_width': 0.05,
            'whiteness_index': 0.1,
            'transparency': 0.05
        }
        
        # Moisture content scoring (optimal around 14%)
        moisture = test_data.get('moisture_content', 14)
        moisture_score = max(0, 100 - abs(moisture - 14) * 5)
        scores.append(moisture_score * weights.get('moisture_content', 0.2))
        
        # Broken grains (lower is better)
        broken = test_data.get('broken_grains', 0)
        broken_score = max(0, 100 - broken * 8)
        scores.append(broken_score * weights.get('broken_grains', 0.15))
        
        # Foreign matter (lower is better)
        foreign = test_data.get('foreign_matter', 0)
        foreign_score = max(0, 100 - foreign * 20)
        scores.append(foreign_score * weights.get('foreign_matter', 0.15))
        
        # Chalky grains (lower is better)
        chalky = test_data.get('chalky_grains', 0)
        chalky_score = max(0, 100 - chalky * 10)
        scores.append(chalky_score * weights.get('chalky_grains', 0.1))
        
        # Damaged grains (lower is better)
        damaged = test_data.get('damaged_grains', 0)
        damaged_score = max(0, 100 - damaged * 15)
        scores.append(damaged_score * weights.get('damaged_grains', 0.1))
        
        # Physical parameters
        grain_length = test_data.get('grain_length', 5.5)
        length_score = min(100, max(0, (grain_length - 4) * 25))  # 4-6mm range
        scores.append(length_score * weights.get('grain_length', 0.1))
        
        whiteness = test_data.get('whiteness_index', 70)
        whiteness_score = min(100, max(0, whiteness))
        scores.append(whiteness_score * weights.get('whiteness_index', 0.1))
        
        return round(sum(scores), 2)
    
    def _determine_grade(self, quality_score: float, test_data: Dict) -> str:
        """Determine quality grade based on score and specific parameters"""
        # Check critical failures first
        moisture = test_data.get('moisture_content', 14)
        foreign_matter = test_data.get('foreign_matter', 0)
        broken_grains = test_data.get('broken_grains', 0)
        
        # Critical failure conditions
        if moisture > 18 or foreign_matter > 3 or broken_grains > 15:
            return 'D'
        
        # Grade based on quality score
        if quality_score >= 90:
            return 'A'
        elif quality_score >= 80:
            return 'B'
        elif quality_score >= 70:
            return 'C'
        else:
            return 'D'
    
    def _detect_anomalies(self, test_data: Dict) -> List[Dict]:
        """Detect anomalies in test results"""
        anomalies = []
        
        # Moisture content anomalies
        moisture = test_data.get('moisture_content', 14)
        if moisture > 16:
            anomalies.append({
                'parameter': 'moisture_content',
                'value': moisture,
                'severity': 'high' if moisture > 18 else 'medium',
                'description': f'High moisture content: {moisture}%',
                'impact': 'Storage risk, potential spoilage'
            })
        elif moisture < 12:
            anomalies.append({
                'parameter': 'moisture_content',
                'value': moisture,
                'severity': 'medium',
                'description': f'Low moisture content: {moisture}%',
                'impact': 'Over-drying, potential quality loss'
            })
        
        # Foreign matter anomalies
        foreign_matter = test_data.get('foreign_matter', 0)
        if foreign_matter > 1:
            anomalies.append({
                'parameter': 'foreign_matter',
                'value': foreign_matter,
                'severity': 'high' if foreign_matter > 2 else 'medium',
                'description': f'High foreign matter: {foreign_matter}%',
                'impact': 'Quality degradation, processing issues'
            })
        
        # Broken grains anomalies
        broken_grains = test_data.get('broken_grains', 0)
        if broken_grains > 8:
            anomalies.append({
                'parameter': 'broken_grains',
                'value': broken_grains,
                'severity': 'high' if broken_grains > 12 else 'medium',
                'description': f'High broken grains: {broken_grains}%',
                'impact': 'Reduced market value, processing efficiency'
            })
        
        return anomalies
    
    def _generate_recommendations(self, test_data: Dict, quality_score: float, anomalies: List) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Score-based recommendations
        if quality_score < 70:
            recommendations.append("Consider rejecting this batch or downgrading")
            recommendations.append("Investigate source quality issues")
        elif quality_score < 85:
            recommendations.append("Acceptable for processing with monitoring")
            recommendations.append("Review supplier quality standards")
        
        # Anomaly-based recommendations
        for anomaly in anomalies:
            if anomaly['parameter'] == 'moisture_content':
                if anomaly['value'] > 16:
                    recommendations.append("Immediate drying required before storage")
                    recommendations.append("Monitor for mold development")
                elif anomaly['value'] < 12:
                    recommendations.append("Check drying process parameters")
            
            elif anomaly['parameter'] == 'foreign_matter':
                recommendations.append("Additional cleaning/sorting required")
                recommendations.append("Review cleaning equipment efficiency")
            
            elif anomaly['parameter'] == 'broken_grains':
                recommendations.append("Investigate handling and processing methods")
                recommendations.append("Consider separate processing for broken grains")
        
        # General recommendations
        if not anomalies and quality_score > 85:
            recommendations.append("Excellent quality - suitable for premium markets")
            recommendations.append("Maintain current processing parameters")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _assess_quality_risk(self, test_data: Dict, anomalies: List) -> Dict:
        """Assess quality-related risks"""
        risk_factors = []
        risk_score = 0
        
        # Calculate risk based on anomalies
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                risk_score += 30
                risk_factors.append(f"High {anomaly['parameter']}")
            elif anomaly['severity'] == 'medium':
                risk_score += 15
                risk_factors.append(f"Elevated {anomaly['parameter']}")
        
        # Additional risk factors
        moisture = test_data.get('moisture_content', 14)
        if moisture > 15:
            risk_score += 20
            risk_factors.append("Storage deterioration risk")
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = 'high'
        elif risk_score >= 25:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'level': risk_level,
            'score': min(100, risk_score),
            'factors': risk_factors,
            'mitigation_required': risk_score >= 25
        }
    
    def _calculate_confidence(self, test_data: Dict) -> float:
        """Calculate confidence in the analysis"""
        # Base confidence
        confidence = 0.8
        
        # Reduce confidence for missing critical parameters
        critical_params = ['moisture_content', 'broken_grains', 'foreign_matter']
        missing_params = [param for param in critical_params if param not in test_data]
        confidence -= len(missing_params) * 0.1
        
        # Reduce confidence for extreme values (might be measurement errors)
        moisture = test_data.get('moisture_content', 14)
        if moisture > 25 or moisture < 8:
            confidence -= 0.2
        
        return max(0.5, min(1.0, confidence))
    
    def predict_quality_trends(self, historical_data: List[Dict]) -> Dict:
        """Predict quality trends based on historical data"""
        try:
            if len(historical_data) < 5:
                return {
                    'trend_prediction': 'insufficient_data',
                    'confidence': 0.3,
                    'recommendations': ['Collect more historical data for trend analysis']
                }
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['test_date'])
            df = df.sort_values('date')
            
            trends = {}
            parameters = ['moisture_content', 'broken_grains', 'foreign_matter', 'quality_score']
            
            for param in parameters:
                if param in df.columns:
                    values = df[param].dropna()
                    if len(values) >= 3:
                        # Calculate trend
                        x = np.arange(len(values))
                        z = np.polyfit(x, values, 1)
                        trend_slope = z[0]
                        
                        # Determine trend direction
                        if abs(trend_slope) < 0.1:
                            direction = 'stable'
                        elif trend_slope > 0:
                            direction = 'increasing'
                        else:
                            direction = 'decreasing'
                        
                        trends[param] = {
                            'direction': direction,
                            'slope': float(trend_slope),
                            'current_avg': float(values.tail(3).mean()),
                            'predicted_next': float(values.iloc[-1] + trend_slope)
                        }
            
            # Overall assessment
            quality_trend = trends.get('quality_score', {})
            overall_direction = quality_trend.get('direction', 'stable')
            
            recommendations = self._generate_trend_recommendations(trends)
            
            return {
                'overall_trend': overall_direction,
                'parameter_trends': trends,
                'recommendations': recommendations,
                'confidence': 0.75,
                'analysis_period': f"{df['date'].min().date()} to {df['date'].max().date()}"
            }
        
        except Exception as e:
            return {
                'trend_prediction': 'analysis_error',
                'error': str(e),
                'confidence': 0.3,
                'recommendations': ['Manual trend analysis required']
            }
    
    def _generate_trend_recommendations(self, trends: Dict) -> List[str]:
        """Generate recommendations based on trend analysis"""
        recommendations = []
        
        # Quality score trends
        quality_trend = trends.get('quality_score', {})
        if quality_trend.get('direction') == 'decreasing':
            recommendations.append("Quality declining - investigate process changes")
            recommendations.append("Review supplier quality and processing parameters")
        elif quality_trend.get('direction') == 'increasing':
            recommendations.append("Quality improving - maintain current practices")
        
        # Moisture content trends
        moisture_trend = trends.get('moisture_content', {})
        if moisture_trend.get('direction') == 'increasing':
            recommendations.append("Moisture levels rising - check drying efficiency")
        
        # Broken grains trends
        broken_trend = trends.get('broken_grains', {})
        if broken_trend.get('direction') == 'increasing':
            recommendations.append("Broken grains increasing - review handling procedures")
        
        return recommendations[:5]
    
    def generate_quality_report(self, inspection_data: Dict) -> Dict:
        """Generate comprehensive quality report with AI insights"""
        try:
            # Basic analysis
            analysis = self.analyze_quality_test(inspection_data.get('test_results', {}))
            
            # Compliance check
            compliance = self._check_compliance(inspection_data)
            
            # Improvement suggestions
            improvements = self._suggest_improvements(inspection_data, analysis)
            
            # Risk mitigation
            risk_mitigation = self._suggest_risk_mitigation(analysis.get('risk_assessment', {}))
            
            return {
                'inspection_summary': {
                    'overall_grade': analysis.get('recommended_grade'),
                    'quality_score': analysis.get('quality_score'),
                    'pass_fail': analysis.get('quality_score', 0) >= 70
                },
                'detailed_analysis': analysis,
                'compliance_status': compliance,
                'improvement_suggestions': improvements,
                'risk_mitigation': risk_mitigation,
                'report_generated_at': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            return {
                'inspection_summary': {'error': 'Report generation failed'},
                'error': str(e)
            }
    
    def _check_compliance(self, inspection_data: Dict) -> Dict:
        """Check compliance with quality standards"""
        test_results = inspection_data.get('test_results', {})
        product_type = inspection_data.get('product_type', 'rice')
        
        # Standard limits (example for rice)
        standards = {
            'moisture_content': {'max': 14.5},
            'foreign_matter': {'max': 1.0},
            'broken_grains': {'max': 5.0},
            'damaged_grains': {'max': 2.0}
        }
        
        compliance_results = {}
        overall_compliant = True
        
        for param, limits in standards.items():
            value = test_results.get(param)
            if value is not None:
                compliant = True
                if 'max' in limits and value > limits['max']:
                    compliant = False
                    overall_compliant = False
                elif 'min' in limits and value < limits['min']:
                    compliant = False
                    overall_compliant = False
                
                compliance_results[param] = {
                    'value': value,
                    'limit': limits,
                    'compliant': compliant
                }
        
        return {
            'overall_compliant': overall_compliant,
            'parameter_compliance': compliance_results,
            'standard_reference': 'Internal Quality Standards v1.0'
        }
    
    def _suggest_improvements(self, inspection_data: Dict, analysis: Dict) -> List[str]:
        """Suggest process improvements based on analysis"""
        suggestions = []
        test_results = inspection_data.get('test_results', {})
        
        # Moisture-related improvements
        moisture = test_results.get('moisture_content', 14)
        if moisture > 14.5:
            suggestions.append("Optimize drying process - extend drying time or increase temperature")
            suggestions.append("Improve moisture monitoring during drying")
        
        # Foreign matter improvements
        foreign_matter = test_results.get('foreign_matter', 0)
        if foreign_matter > 0.5:
            suggestions.append("Enhance cleaning process - check destoner and separator efficiency")
            suggestions.append("Improve raw material inspection at intake")
        
        # Broken grains improvements
        broken_grains = test_results.get('broken_grains', 0)
        if broken_grains > 3:
            suggestions.append("Review milling parameters - adjust roller pressure and speed")
            suggestions.append("Improve handling procedures to reduce mechanical damage")
        
        # Quality score improvements
        quality_score = analysis.get('quality_score', 0)
        if quality_score < 85:
            suggestions.append("Implement statistical process control for key parameters")
            suggestions.append("Enhance operator training on quality procedures")
        
        return suggestions[:5]
    
    def _suggest_risk_mitigation(self, risk_assessment: Dict) -> List[str]:
        """Suggest risk mitigation strategies"""
        mitigation_strategies = []
        risk_level = risk_assessment.get('level', 'low')
        risk_factors = risk_assessment.get('factors', [])
        
        if risk_level in ['high', 'medium']:
            mitigation_strategies.append("Increase inspection frequency for this product type")
            mitigation_strategies.append("Implement additional quality checkpoints")
        
        for factor in risk_factors:
            if 'moisture' in factor.lower():
                mitigation_strategies.append("Install continuous moisture monitoring system")
            elif 'foreign' in factor.lower():
                mitigation_strategies.append("Upgrade cleaning equipment and procedures")
            elif 'broken' in factor.lower():
                mitigation_strategies.append("Review and optimize milling process parameters")
        
        if risk_level == 'high':
            mitigation_strategies.append("Consider batch segregation until issues resolved")
            mitigation_strategies.append("Notify quality manager for immediate review")
        
        return mitigation_strategies[:5]
    
    def detect_equipment_issues(self, quality_data: List[Dict]) -> Dict:
        """Detect potential equipment issues based on quality patterns"""
        try:
            if len(quality_data) < 10:
                return {'status': 'insufficient_data'}
            
            # Analyze patterns that might indicate equipment issues
            issues = []
            
            # Check for sudden quality drops
            quality_scores = [item.get('quality_score', 0) for item in quality_data[-10:]]
            if len(quality_scores) >= 5:
                recent_avg = np.mean(quality_scores[-5:])
                previous_avg = np.mean(quality_scores[-10:-5])
                
                if recent_avg < previous_avg - 10:
                    issues.append({
                        'type': 'quality_drop',
                        'severity': 'high',
                        'description': 'Sudden quality score drop detected',
                        'possible_causes': ['Equipment malfunction', 'Process parameter drift']
                    })
            
            # Check for increasing variability
            moisture_values = [item.get('moisture_content', 14) for item in quality_data[-10:]]
            if len(moisture_values) >= 5 and np.std(moisture_values) > 2:
                issues.append({
                    'type': 'high_variability',
                    'severity': 'medium',
                    'description': 'High moisture content variability',
                    'possible_causes': ['Dryer malfunction', 'Inconsistent feed rate']
                })
            
            return {
                'status': 'analysis_complete',
                'issues_detected': len(issues),
                'equipment_issues': issues,
                'recommendations': self._generate_equipment_recommendations(issues)
            }
        
        except Exception as e:
            return {
                'status': 'analysis_error',
                'error': str(e)
            }
    
    def _generate_equipment_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate equipment maintenance recommendations"""
        recommendations = []
        
        for issue in issues:
            if issue['type'] == 'quality_drop':
                recommendations.append("Schedule immediate equipment inspection")
                recommendations.append("Calibrate quality measurement instruments")
            elif issue['type'] == 'high_variability':
                recommendations.append("Check equipment calibration and maintenance")
                recommendations.append("Review process control parameters")
        
        if not issues:
            recommendations.append("Equipment performance appears normal")
            recommendations.append("Continue regular maintenance schedule")
        
        return recommendations