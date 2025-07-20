import requests
import json
from datetime import datetime, timedelta
from models.farmer import Farmer, PaddyProcurement, FarmerContract
import numpy as np

class AIFarmerService:
    def __init__(self):
        self.ai_service_url = "http://ai-services:8000"
    
    def verify_farmer_details(self, farmer_data: dict):
        """AI verification of farmer details"""
        try:
            response = requests.post(f"{self.ai_service_url}/farmer/verify", json=farmer_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # Fallback verification
        return self._fallback_farmer_verification(farmer_data)
    
    def check_duplicate_farmer(self, farmer_data: dict):
        """AI duplicate farmer detection"""
        try:
            response = requests.post(f"{self.ai_service_url}/farmer/duplicate-check", json=farmer_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # Fallback duplicate check
        return self._fallback_duplicate_check(farmer_data)
    
    def assess_paddy_quality(self, procurement_data: dict):
        """AI paddy quality assessment"""
        try:
            response = requests.post(f"{self.ai_service_url}/farmer/quality-assessment", json=procurement_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # Fallback quality assessment
        return self._fallback_quality_assessment(procurement_data)
    
    def optimize_contract_terms(self, contract_data: dict):
        """AI contract terms optimization"""
        try:
            response = requests.post(f"{self.ai_service_url}/farmer/optimize-contract", json=contract_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # Fallback optimization
        return self._fallback_contract_optimization(contract_data)
    
    def recommend_procurement_price(self, procurement_data: dict, quality_assessment: dict):
        """AI procurement price recommendation"""
        try:
            payload = {**procurement_data, 'quality_assessment': quality_assessment}
            response = requests.post(f"{self.ai_service_url}/farmer/price-recommendation", json=payload)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # Fallback pricing
        return self._fallback_price_recommendation(procurement_data, quality_assessment)
    
    def analyze_farmer_performance(self, farmer_data: dict):
        """AI farmer performance analysis"""
        try:
            response = requests.post(f"{self.ai_service_url}/farmer/performance-analysis", json=farmer_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # Fallback analysis
        return self._fallback_performance_analysis(farmer_data)
    
    def predict_seasonal_yield(self, planning_data: dict):
        """AI seasonal yield prediction"""
        try:
            response = requests.post(f"{self.ai_service_url}/farmer/yield-prediction", json=planning_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # Fallback prediction
        return self._fallback_yield_prediction(planning_data)
    
    def _fallback_farmer_verification(self, farmer_data: dict):
        """Fallback farmer verification logic"""
        verification_score = 0
        issues = []
        
        # Check required fields
        required_fields = ['name', 'phone', 'village', 'district']
        for field in required_fields:
            if farmer_data.get(field):
                verification_score += 25
            else:
                issues.append(f"Missing {field}")
        
        # Check phone number format
        phone = farmer_data.get('phone', '')
        if len(phone) == 10 and phone.isdigit():
            verification_score += 10
        else:
            issues.append("Invalid phone number format")
        
        # Check Aadhar number
        aadhar = farmer_data.get('aadhar_number', '')
        if len(aadhar) == 12 and aadhar.isdigit():
            verification_score += 15
        elif aadhar:
            issues.append("Invalid Aadhar number format")
        
        status = 'verified' if verification_score >= 80 else 'pending' if verification_score >= 60 else 'rejected'
        
        return {
            'status': status,
            'score': verification_score,
            'issues': issues,
            'auto_verify': verification_score >= 90
        }
    
    def _fallback_duplicate_check(self, farmer_data: dict):
        """Fallback duplicate check logic"""
        # Simple duplicate check based on phone and Aadhar
        phone = farmer_data.get('phone')
        aadhar = farmer_data.get('aadhar_number')
        
        existing_farmers = []
        
        if phone:
            phone_matches = Farmer.query.filter_by(phone=phone).all()
            existing_farmers.extend(phone_matches)
        
        if aadhar:
            aadhar_matches = Farmer.query.filter_by(aadhar_number=aadhar).all()
            existing_farmers.extend(aadhar_matches)
        
        is_duplicate = len(existing_farmers) > 0
        
        return {
            'is_duplicate': is_duplicate,
            'matches': [farmer.to_dict() for farmer in existing_farmers[:5]],
            'confidence': 0.9 if is_duplicate else 0.1
        }
    
    def _fallback_quality_assessment(self, procurement_data: dict):
        """Fallback quality assessment logic"""
        moisture = procurement_data.get('moisture_content', 14)
        foreign_matter = procurement_data.get('foreign_matter', 2)
        broken_grains = procurement_data.get('broken_grains', 5)
        
        # Calculate quality score (0-100)
        moisture_score = max(0, 100 - (abs(moisture - 14) * 5))  # Optimal moisture: 14%
        foreign_matter_score = max(0, 100 - (foreign_matter * 10))  # Lower is better
        broken_grains_score = max(0, 100 - (broken_grains * 8))  # Lower is better
        
        overall_score = (moisture_score + foreign_matter_score + broken_grains_score) / 3
        
        # Determine grade
        if overall_score >= 90:
            grade = 'A'
            bonus_rate = 50  # ₹50 per quintal bonus
        elif overall_score >= 80:
            grade = 'B'
            bonus_rate = 25
        elif overall_score >= 70:
            grade = 'C'
            bonus_rate = 0
        else:
            grade = 'D'
            bonus_rate = -25  # Penalty
        
        return {
            'grade': grade,
            'score': round(overall_score, 2),
            'bonus_rate': bonus_rate,
            'penalty_rate': abs(bonus_rate) if bonus_rate < 0 else 0,
            'test_results': {
                'moisture_score': round(moisture_score, 2),
                'foreign_matter_score': round(foreign_matter_score, 2),
                'broken_grains_score': round(broken_grains_score, 2)
            },
            'recommendations': self._get_quality_recommendations(grade, moisture, foreign_matter, broken_grains)
        }
    
    def _fallback_contract_optimization(self, contract_data: dict):
        """Fallback contract optimization logic"""
        base_price = contract_data.get('base_price', 2000)
        expected_quantity = contract_data.get('expected_quantity', 100)
        
        # Simple optimization based on quantity and season
        season = contract_data.get('season', 'kharif')
        
        # Seasonal price adjustment
        if season == 'kharif':
            price_multiplier = 1.0
        else:  # rabi
            price_multiplier = 1.05
        
        # Quantity-based discount
        if expected_quantity >= 500:
            quantity_bonus = 50
        elif expected_quantity >= 200:
            quantity_bonus = 25
        else:
            quantity_bonus = 0
        
        optimized_price = (base_price * price_multiplier) + quantity_bonus
        
        return {
            'optimized_price': round(optimized_price, 2),
            'price_adjustments': {
                'seasonal_adjustment': round((price_multiplier - 1) * base_price, 2),
                'quantity_bonus': quantity_bonus
            },
            'recommendations': [
                f"Seasonal adjustment: {((price_multiplier - 1) * 100):.1f}%",
                f"Quantity bonus: ₹{quantity_bonus}/quintal"
            ]
        }
    
    def _fallback_price_recommendation(self, procurement_data: dict, quality_assessment: dict):
        """Fallback price recommendation logic"""
        base_price = procurement_data.get('base_price', 2000)
        quality_grade = quality_assessment.get('grade', 'C')
        
        # Market price adjustment (simplified)
        market_adjustment = 0
        
        # Quality-based adjustment
        quality_adjustments = {
            'A': 100,
            'B': 50,
            'C': 0,
            'D': -50
        }
        
        quality_adjustment = quality_adjustments.get(quality_grade, 0)
        recommended_price = base_price + market_adjustment + quality_adjustment
        
        return {
            'recommended_price': round(recommended_price, 2),
            'adjustments': {
                'market_adjustment': market_adjustment,
                'quality_adjustment': quality_adjustment
            },
            'confidence': 0.75,
            'reasoning': f"Price adjusted by ₹{quality_adjustment} based on {quality_grade} grade quality"
        }
    
    def _fallback_performance_analysis(self, farmer_data: dict):
        """Fallback performance analysis logic"""
        farmer = farmer_data.get('farmer', {})
        procurements = farmer_data.get('recent_procurements', [])
        
        if not procurements:
            return {
                'overall_score': 0,
                'quality_trend': 'insufficient_data',
                'reliability_score': farmer.get('reliability_score', 0),
                'recommendations': ['Insufficient data for analysis']
            }
        
        # Calculate average quality
        quality_scores = [p.get('quality_score', 0) for p in procurements if p.get('quality_score')]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Calculate delivery consistency
        delivery_count = len(procurements)
        consistency_score = min(100, delivery_count * 10)  # Max 100 for 10+ deliveries
        
        overall_score = (avg_quality + consistency_score) / 2
        
        return {
            'overall_score': round(overall_score, 2),
            'quality_trend': 'improving' if avg_quality > 75 else 'stable' if avg_quality > 60 else 'declining',
            'delivery_consistency': round(consistency_score, 2),
            'recommendations': self._get_performance_recommendations(overall_score, avg_quality)
        }
    
    def _fallback_yield_prediction(self, planning_data: dict):
        """Fallback yield prediction logic"""
        land_area = planning_data.get('land_area', 10)
        variety = planning_data.get('variety', 'IR64')
        season = planning_data.get('season', 'kharif')
        
        # Base yield per acre (quintals)
        base_yields = {
            'kharif': 25,
            'rabi': 30
        }
        
        base_yield = base_yields.get(season, 25)
        
        # Variety adjustment
        variety_multipliers = {
            'IR64': 1.0,
            'Basmati': 0.8,
            'Sona Masuri': 1.1,
            'Swarna': 1.05
        }
        
        variety_multiplier = variety_multipliers.get(variety, 1.0)
        predicted_yield = land_area * base_yield * variety_multiplier
        
        return {
            'predicted_yield': round(predicted_yield, 2),
            'yield_per_acre': round(base_yield * variety_multiplier, 2),
            'confidence': 0.7,
            'factors': {
                'season': season,
                'variety': variety,
                'land_area': land_area
            }
        }
    
    def _get_quality_recommendations(self, grade: str, moisture: float, foreign_matter: float, broken_grains: float):
        """Get quality improvement recommendations"""
        recommendations = []
        
        if moisture > 15:
            recommendations.append("Reduce moisture content through proper drying")
        elif moisture < 12:
            recommendations.append("Increase moisture content to optimal level (13-14%)")
        
        if foreign_matter > 3:
            recommendations.append("Improve cleaning process to reduce foreign matter")
        
        if broken_grains > 8:
            recommendations.append("Handle paddy more carefully to reduce broken grains")
        
        if grade in ['C', 'D']:
            recommendations.append("Consider improved storage and handling practices")
        
        return recommendations
    
    def _get_performance_recommendations(self, overall_score: float, quality_score: float):
        """Get farmer performance recommendations"""
        recommendations = []
        
        if overall_score < 60:
            recommendations.append("Focus on improving overall quality and consistency")
        
        if quality_score < 70:
            recommendations.append("Implement better post-harvest handling practices")
            recommendations.append("Consider training on quality improvement techniques")
        
        if overall_score >= 80:
            recommendations.append("Excellent performance! Consider premium variety cultivation")
        
        return recommendations