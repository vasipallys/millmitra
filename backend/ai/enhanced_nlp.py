"""
Enhanced NLP Processor for Rice Mill Management System

This module implements advanced natural language processing using transformer-based models
for more sophisticated conversational AI capabilities.
"""

import json
import re
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

# Try to load spaCy model with error handling
try:
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except OSError:
    print("Warning: spaCy English model not found. Please install with: python -m spacy download en_core_web_sm")
    SPACY_AVAILABLE = False
except Exception as e:
    print(f"Warning: spaCy import failed: {e}")
    SPACY_AVAILABLE = False

# Try to load transformers with error handling
try:
    # Initialize transformer models for various NLP tasks
    sentiment_classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    zero_shot_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    question_answerer = pipeline("question-answering", model="deepset/roberta-base-squad2")
    SUMMARIZATION_AVAILABLE = True
except Exception as e:
    print(f"Warning: Transformers models not available: {e}")
    SUMMARIZATION_AVAILABLE = False
    sentiment_classifier = None
    zero_shot_classifier = None
    question_answerer = None


class EnhancedNLPProcessor:
    """Enhanced NLP processor with advanced conversational AI capabilities"""
    
    def __init__(self):
        """Initialize the enhanced NLP processor"""
        self.query_patterns = self._load_advanced_query_patterns()
        self.domain_entities = self._load_domain_entities()
        self.response_templates = self._load_response_templates()
        
        # Intent classification categories
        self.intent_categories = [
            "production_inquiry",
            "quality_analysis",
            "financial_inquiry",
            "inventory_check",
            "maintenance_request",
            "customer_service",
            "compliance_check",
            "report_generation",
            "scheduling",
            "general_inquiry"
        ]
        
        # Entity types
        self.entity_types = [
            "date",
            "time",
            "quantity",
            "location",
            "person",
            "organization",
            "product",
            "metric",
            "process"
        ]
    
    def _load_advanced_query_patterns(self) -> Dict:
        """Load advanced query patterns for better understanding"""
        return {
            'production_queries': [
                'production', 'output', 'manufacturing', 'processing', 'batch', 'mill',
                'throughput', 'capacity', 'efficiency', 'yield', 'volume'
            ],
            'quality_queries': [
                'quality', 'grade', 'defect', 'standard', 'test', 'inspection',
                'moisture', 'broken', 'chalky', 'foreign matter', 'purity'
            ],
            'financial_queries': [
                'profit', 'revenue', 'cost', 'margin', 'payment', 'cash', 'finance',
                'expense', 'income', 'budget', 'roi', 'earnings'
            ],
            'customer_queries': [
                'customer', 'client', 'order', 'delivery', 'satisfaction', 'feedback',
                'complaint', 'service', 'support'
            ],
            'inventory_queries': [
                'inventory', 'stock', 'storage', 'warehouse', 'paddy', 'rice',
                'supply', 'demand', 'availability'
            ],
            'maintenance_queries': [
                'maintenance', 'repair', 'machine', 'equipment', 'breakdown', 'service',
                'schedule', 'preventive', 'downtime'
            ],
            'compliance_queries': [
                'compliance', 'regulation', 'license', 'certificate', 'audit',
                'gst', 'tax', 'standard', 'policy'
            ],
            'reporting_queries': [
                'report', 'summary', 'dashboard', 'analytics', 'trend',
                'performance', 'metric', 'kpi'
            ]
        }
    
    def _load_domain_entities(self) -> Dict:
        """Load domain-specific entities for better understanding"""
        return {
            'products': [
                'basmati rice', 'jasmine rice', 'brown rice', 'white rice',
                'parboiled rice', 'steam rice', 'raw rice'
            ],
            'processes': [
                'milling', 'polishing', 'sorting', 'cleaning', 'grading',
                'packaging', 'storage', 'drying'
            ],
            'equipment': [
                'huller', 'sheller', 'polisher', 'separator', 'sifter',
                'color sorter', 'metal detector', 'weighing scale'
            ],
            'metrics': [
                'moisture content', 'broken percentage', 'foreign matter',
                'chalky kernels', 'head rice yield', 'whiteness index'
            ],
            'locations': [
                'mill 1', 'mill 2', 'storage area', 'packing section',
                'quality lab', 'loading bay', 'office'
            ]
        }
    
    def _load_response_templates(self) -> Dict:
        """Load response templates for consistent and professional responses"""
        return {
            'production_summary': "Today's production status: {processed_quantity} kg processed with {efficiency}% efficiency. Current throughput: {throughput} kg/hour.",
            'quality_report': "Quality analysis for batch {batch_id}: Grade {grade} with score {score}/100. Key metrics: Moisture {moisture}%, Broken {broken}%, Foreign matter {foreign}%.",
            'financial_summary': "Financial overview: Revenue of {revenue} with {margin}% profit margin. Expenses: {expenses}. Net profit: {profit}.",
            'inventory_status': "Current inventory: {paddy_stock} tons of paddy, {rice_stock} tons of finished rice. Storage capacity utilization: {utilization}%.",
            'maintenance_alert': "Maintenance alert: {equipment} requires attention. Scheduled for {date}. Estimated downtime: {downtime} hours.",
            'compliance_status': "Compliance status: All licenses current. Next audit scheduled for {audit_date}. {certificates} certificates valid.",
            'general_response': "I understand you're asking about {topic}. Based on current operations, I can provide insights about production, quality, finances, or other areas. Please ask more specific questions for detailed analysis."
        }
    
    def process_query(self, query: str, user_context: Dict) -> Dict:
        """Process natural language query with advanced NLP techniques"""
        try:
            # Handle empty queries
            if not query or not query.strip():
                return {
                    'success': False,
                    'error': 'Query is required',
                    'original_query': query,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Preprocess the query
            processed_query = self._preprocess_query(query)
            
            # Extract entities and intent
            entities = self._extract_entities(processed_query)
            intent = self._classify_intent(processed_query)
            sentiment = self._analyze_sentiment(query)
            
            # Generate context-aware response
            response = self._generate_enhanced_response(
                query, processed_query, entities, intent, sentiment, user_context
            )
            
            # Ensure response always has required fields
            result = {
                'success': True,
                'original_query': query,
                'processed_query': processed_query,
                'intent': intent,
                'entities': entities,
                'sentiment': sentiment,
                'response': response['response'],
                'confidence': response.get('confidence', 0.8),
                'actionable_items': response.get('actionable_items', []),
                'suggestions': response.get('suggestions', []),
                'timestamp': datetime.now().isoformat()
            }
            
            # Add data field if present in response
            if 'data' in response:
                result['data'] = response['data']
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original_query': query,
                'timestamp': datetime.now().isoformat()
            }
    
    def _preprocess_query(self, query: str) -> str:
        """Preprocess the query for better understanding"""
        # Convert to lowercase and remove extra whitespace
        query = re.sub(r'\s+', ' ', query.lower().strip())
        
        # Expand common contractions
        contractions = {
            "what's": "what is",
            "how's": "how is",
            "i'm": "i am",
            "we're": "we are",
            "they're": "they are",
            "can't": "cannot",
            "won't": "will not",
            "n't": " not",
            "'re": " are",
            "'ve": " have",
            "'ll": " will",
            "'d": " would"
        }
        
        for contraction, expansion in contractions.items():
            query = query.replace(contraction, expansion)
        
        return query
    
    def _extract_entities(self, query: str) -> List[Dict]:
        """Extract entities from the query using advanced NLP"""
        entities = []
        
        # Use spaCy for entity extraction if available
        if SPACY_AVAILABLE:
            doc = nlp(query)
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': 0.9  # spaCy doesn't provide confidence scores
                })
        
        # Domain-specific entity extraction
        for entity_type, entity_list in self.domain_entities.items():
            for entity in entity_list:
                if entity in query:
                    # Check if this entity is already captured by spaCy
                    already_captured = any(e['text'] == entity for e in entities)
                    if not already_captured:
                        entities.append({
                            'text': entity,
                            'label': entity_type.upper(),
                            'confidence': 0.8
                        })
        
        # Extract dates using regex patterns
        date_patterns = [
            r'\b(today|yesterday|tomorrow)\b',
            r'\b(last|this|next)\s+(week|month|quarter|year)\b',
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            r'\b(\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{2,4})\b'
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                entities.append({
                    'text': match.group(),
                    'label': 'DATE',
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.95
                })
        
        # Extract quantities
        quantity_pattern = r'\b(\d+(?:\.\d+)?)\s*(kg|tons?|hours?|minutes?|percent|%|\$)\b'
        matches = re.finditer(quantity_pattern, query, re.IGNORECASE)
        for match in matches:
            entities.append({
                'text': match.group(),
                'label': 'QUANTITY',
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.9
            })
        
        # Extract batch IDs (format: B followed by numbers)
        batch_pattern = r'\b([Bb]\d+)\b'
        matches = re.finditer(batch_pattern, query, re.IGNORECASE)
        for match in matches:
            entities.append({
                'text': match.group(),
                'label': 'BATCH_ID',
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.9
            })
        
        return entities
    
    def _classify_intent(self, query: str) -> str:
        """Classify the intent of the query using zero-shot classification"""
        if zero_shot_classifier is not None:
            try:
                result = zero_shot_classifier(query, self.intent_categories)
                return result['labels'][0]  # Return the highest scoring label
            except Exception as e:
                print(f"Zero-shot classification failed: {e}")
        
        # Fallback to keyword-based classification
        query_lower = query.lower()
        
        # Check for specific patterns
        if any(word in query_lower for word in ['why', 'reason', 'cause', 'analyze', 'analysis']):
            if any(word in query_lower for word in self.query_patterns['production_queries']):
                return 'production_inquiry'
            elif any(word in query_lower for word in self.query_patterns['quality_queries']):
                return 'quality_analysis'
            else:
                return 'general_inquiry'
        
        elif any(word in query_lower for word in ['show', 'display', 'what', 'how much', 'status', 'current']):
            if any(word in query_lower for word in ['today', 'daily', 'current']):
                return 'report_generation'
            elif any(word in query_lower for word in self.query_patterns['financial_queries']):
                return 'financial_inquiry'
            else:
                return 'report_generation'
        
        elif any(word in query_lower for word in ['best', 'top', 'highest', 'performing', 'trend']):
            return 'report_generation'
        
        elif any(word in query_lower for word in ['problem', 'issue', 'alert', 'warning', 'maintenance', 'repair', 'service']):
            return 'maintenance_request'
        
        elif any(word in query_lower for word in ['schedule', 'plan', 'when', 'time']):
            return 'scheduling'
        
        elif any(word in query_lower for word in ['compliance', 'license', 'certificate', 'audit', 'regulation']):
            return 'compliance_check'
        
        elif any(word in query_lower for word in ['finance', 'revenue', 'profit', 'cost', 'margin', 'expense', 'income', 'budget', 'roi', 'earnings', 'cash', 'payment']):
            return 'financial_inquiry'
        
        elif any(word in query_lower for word in ['inventory', 'stock', 'storage', 'warehouse', 'paddy', 'rice', 'supply', 'demand', 'availability']):
            return 'inventory_check'
        
        elif any(word in query_lower for word in ['quality', 'grade', 'defect', 'standard', 'test', 'inspection', 'moisture', 'broken', 'chalky', 'foreign matter', 'purity']):
            return 'quality_analysis'
        
        elif any(word in query_lower for word in ['production', 'output', 'manufacturing', 'processing', 'batch', 'mill', 'throughput', 'capacity', 'efficiency', 'yield', 'volume']):
            return 'production_inquiry'
        
        else:
            # Default classification based on most common query patterns
            scores = defaultdict(int)
            for category, keywords in self.query_patterns.items():
                for keyword in keywords:
                    if keyword in query_lower:
                        scores[category] += 1
            
            if scores:
                # Return the category with the highest score
                best_category = max(scores, key=scores.get)
                # Map category to intent
                category_to_intent = {
                    'production_queries': 'production_inquiry',
                    'quality_queries': 'quality_analysis',
                    'financial_queries': 'financial_inquiry',
                    'customer_queries': 'customer_service',
                    'inventory_queries': 'inventory_check',
                    'maintenance_queries': 'maintenance_request',
                    'compliance_queries': 'compliance_check',
                    'reporting_queries': 'report_generation'
                }
                return category_to_intent.get(best_category, 'general_inquiry')
            else:
                return 'general_inquiry'
    
    def _analyze_sentiment(self, query: str) -> Dict:
        """Analyze the sentiment of the query"""
        if sentiment_classifier is not None:
            try:
                result = sentiment_classifier(query)[0]
                return {
                    'label': result['label'],
                    'score': result['score']
                }
            except Exception as e:
                print(f"Sentiment analysis failed: {e}")
        
        # Fallback sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'well', 'perfect', 'amazing', 'wonderful']
        negative_words = ['bad', 'poor', 'terrible', 'awful', 'worst', 'problem', 'issue', 'error']
        
        query_lower = query.lower()
        positive_count = sum(1 for word in positive_words if word in query_lower)
        negative_count = sum(1 for word in negative_words if word in query_lower)
        
        if positive_count > negative_count:
            return {'label': 'POSITIVE', 'score': 0.7}
        elif negative_count > positive_count:
            return {'label': 'NEGATIVE', 'score': 0.7}
        else:
            return {'label': 'NEUTRAL', 'score': 0.5}
    
    def _generate_enhanced_response(self, original_query: str, processed_query: str, 
                                  entities: List[Dict], intent: str, sentiment: Dict, 
                                  user_context: Dict) -> Dict:
        """Generate enhanced response using context and intent"""
        # Generate response based on intent
        if intent == 'production_inquiry':
            return self._generate_production_response(entities, user_context)
        elif intent == 'quality_analysis':
            return self._generate_quality_response(entities, user_context)
        elif intent == 'financial_inquiry':
            return self._generate_financial_response(entities, user_context)
        elif intent == 'inventory_check':
            return self._generate_inventory_response(entities, user_context)
        elif intent == 'maintenance_request':
            return self._generate_maintenance_response(entities, user_context)
        elif intent == 'compliance_check':
            return self._generate_compliance_response(entities, user_context)
        elif intent == 'report_generation':
            return self._generate_report_response(entities, user_context)
        elif intent == 'customer_service':
            return self._generate_customer_response(entities, user_context)
        elif intent == 'scheduling':
            return self._generate_schedule_response(entities, user_context)
        else:
            return self._generate_general_response(original_query, entities, user_context)
    
    def _generate_production_response(self, entities: List[Dict], user_context: Dict) -> Dict:
        """Generate production-specific response"""
        # Extract date entities
        date_entities = [e for e in entities if e['label'] == 'DATE']
        date_text = date_entities[0]['text'] if date_entities else 'today'
        
        # Generate mock production data
        processed_quantity = np.random.randint(2000, 3000)
        efficiency = np.random.randint(85, 95)
        throughput = np.random.randint(150, 250)
        
        response_text = self.response_templates['production_summary'].format(
            processed_quantity=processed_quantity,
            efficiency=efficiency,
            throughput=throughput
        )
        
        return {
            'response': response_text,
            'confidence': 0.85,
            'data': {
                'processed_quantity': processed_quantity,
                'efficiency': efficiency,
                'throughput': throughput,
                'date': date_text
            },
            'actionable_items': [
                f"Monitor throughput to maintain {throughput} kg/hour target",
                f"Address any efficiency issues below {efficiency}%"
            ],
            'suggestions': [
                "Ask about specific production line performance",
                "Inquire about equipment efficiency metrics",
                "Check for production bottlenecks"
            ]
        }
    
    def _generate_quality_response(self, entities: List[Dict], user_context: Dict) -> Dict:
        """Generate quality-specific response"""
        # Extract product entities
        product_entities = [e for e in entities if e['label'] == 'PRODUCT']
        product_text = product_entities[0]['text'] if product_entities else 'rice'
        
        # Generate mock quality data
        batch_id = f"B{datetime.now().strftime('%Y%m%d%H%M')}"
        grade = np.random.choice(['A+', 'A', 'B+', 'B', 'C+'])
        score = np.random.randint(75, 98)
        moisture = round(np.random.uniform(11, 13), 1)
        broken = round(np.random.uniform(1, 4), 1)
        foreign = round(np.random.uniform(0.1, 0.8), 1)
        
        response_text = self.response_templates['quality_report'].format(
            batch_id=batch_id,
            grade=grade,
            score=score,
            moisture=moisture,
            broken=broken,
            foreign=foreign
        )
        
        return {
            'response': response_text,
            'confidence': 0.9,
            'data': {
                'batch_id': batch_id,
                'grade': grade,
                'score': score,
                'moisture_content': moisture,
                'broken_percentage': broken,
                'foreign_matter': foreign
            },
            'actionable_items': [
                f"Review moisture control settings if {moisture}% exceeds target",
                f"Adjust milling parameters if broken percentage {broken}% is high"
            ],
            'suggestions': [
                "Ask for detailed quality analysis by parameter",
                "Inquire about quality trends over time",
                "Check quality by production batch"
            ]
        }
    
    def _generate_financial_response(self, entities: List[Dict], user_context: Dict) -> Dict:
        """Generate financial-specific response"""
        # Extract date entities
        date_entities = [e for e in entities if e['label'] == 'DATE']
        date_text = date_entities[0]['text'] if date_entities else 'current period'
        
        # Generate mock financial data
        revenue = f"${np.random.randint(50000, 80000):,}"
        margin = np.random.randint(15, 25)
        expenses = f"${np.random.randint(30000, 50000):,}"
        profit = f"${np.random.randint(10000, 20000):,}"
        
        response_text = self.response_templates['financial_summary'].format(
            revenue=revenue,
            margin=margin,
            expenses=expenses,
            profit=profit
        )
        
        return {
            'response': response_text,
            'confidence': 0.8,
            'data': {
                'revenue': revenue,
                'profit_margin': margin,
                'expenses': expenses,
                'net_profit': profit,
                'period': date_text
            },
            'actionable_items': [
                f"Review expense categories to maintain {margin}% margin",
                f"Analyze revenue streams for growth opportunities"
            ],
            'suggestions': [
                "Ask about specific expense categories",
                "Inquire about profit trends",
                "Check cash flow status"
            ]
        }
    
    def _generate_inventory_response(self, entities: List[Dict], user_context: Dict) -> Dict:
        """Generate inventory-specific response"""
        # Extract product entities
        product_entities = [e for e in entities if e['label'] == 'PRODUCT']
        product_text = product_entities[0]['text'] if product_entities else 'rice'
        
        # Generate mock inventory data
        paddy_stock = np.random.randint(50, 150)
        rice_stock = np.random.randint(30, 100)
        utilization = np.random.randint(60, 85)
        
        response_text = self.response_templates['inventory_status'].format(
            paddy_stock=paddy_stock,
            rice_stock=rice_stock,
            utilization=utilization
        )
        
        return {
            'response': response_text,
            'confidence': 0.85,
            'data': {
                'paddy_stock': paddy_stock,
                'rice_stock': rice_stock,
                'utilization': utilization
            },
            'actionable_items': [
                f"Reorder paddy if stock {paddy_stock} tons is below threshold",
                f"Plan production to optimize {utilization}% storage utilization"
            ],
            'suggestions': [
                "Ask about specific inventory items",
                "Inquire about storage capacity",
                "Check inventory turnover rates"
            ]
        }
    
    def _generate_maintenance_response(self, entities: List[Dict], user_context: Dict) -> Dict:
        """Generate maintenance-specific response"""
        # Extract equipment entities
        equipment_entities = [e for e in entities if e['label'] == 'EQUIPMENT']
        equipment_text = equipment_entities[0]['text'] if equipment_entities else 'equipment'
        
        # Extract date entities
        date_entities = [e for e in entities if e['label'] == 'DATE']
        date_text = date_entities[0]['text'] if date_entities else 'upcoming'
        
        # Generate mock maintenance data
        date = (datetime.now() + timedelta(days=np.random.randint(1, 7))).strftime('%Y-%m-%d')
        downtime = np.random.randint(2, 8)
        
        response_text = self.response_templates['maintenance_alert'].format(
            equipment=equipment_text.title(),
            date=date,
            downtime=downtime
        )
        
        return {
            'response': response_text,
            'confidence': 0.75,
            'data': {
                'equipment': equipment_text,
                'maintenance_date': date,
                'estimated_downtime': downtime,
                'date_context': date_text
            },
            'actionable_items': [
                f"Schedule maintenance for {equipment_text} on {date}",
                f"Prepare backup equipment to minimize {downtime} hour downtime"
            ],
            'suggestions': [
                "Ask about maintenance history",
                "Inquire about preventive maintenance schedule",
                "Check equipment performance metrics"
            ]
        }
    
    def _generate_compliance_response(self, entities: List[Dict], user_context: Dict) -> Dict:
        """Generate compliance-specific response"""
        # Generate mock compliance data
        audit_date = (datetime.now() + timedelta(days=np.random.randint(30, 90))).strftime('%Y-%m-%d')
        certificates = np.random.randint(8, 15)
        
        response_text = self.response_templates['compliance_status'].format(
            audit_date=audit_date,
            certificates=certificates
        )
        
        return {
            'response': response_text,
            'confidence': 0.9,
            'data': {
                'next_audit_date': audit_date,
                'valid_certificates': certificates
            },
            'actionable_items': [
                f"Prepare for audit scheduled on {audit_date}",
                f"Verify all {certificates} certificates are up to date"
            ],
            'suggestions': [
                "Ask about specific compliance requirements",
                "Inquire about certificate expiration dates",
                "Check regulatory updates"
            ]
        }
    
    def _generate_report_response(self, entities: List[Dict], user_context: Dict) -> Dict:
        """Generate report-specific response"""
        # Extract date entities
        date_entities = [e for e in entities if e['label'] == 'DATE']
        date_text = date_entities[0]['text'] if date_entities else 'current period'
        
        # Generate mock report summary
        report_types = ['production', 'quality', 'financial', 'inventory']
        report_type = np.random.choice(report_types)
        
        response_text = f"I've generated a {report_type} report for {date_text}. The report includes key metrics, trends, and actionable insights. Would you like me to share specific sections or metrics from this report?"
        
        return {
            'response': response_text,
            'confidence': 0.85,
            'data': {
                'report_type': report_type,
                'period': date_text
            },
            'actionable_items': [
                "Review the full report for detailed insights",
                "Share report with relevant stakeholders"
            ],
            'suggestions': [
                f"Ask for detailed {report_type} metrics",
                "Inquire about trends in the report",
                "Request specific sections of the report"
            ]
        }
    
    def _generate_customer_response(self, entities: List[Dict], user_context: Dict) -> Dict:
        """Generate customer service response"""
        # Generate mock customer data
        satisfaction_score = np.random.randint(75, 95)
        pending_orders = np.random.randint(5, 15)
        
        response_text = f"Customer satisfaction score is {satisfaction_score}/100. There are currently {pending_orders} orders pending fulfillment. Our customer service team is addressing all inquiries within 24 hours."
        
        return {
            'response': response_text,
            'confidence': 0.8,
            'data': {
                'satisfaction_score': satisfaction_score,
                'pending_orders': pending_orders
            },
            'actionable_items': [
                f"Monitor satisfaction score to maintain above 90%",
                f"Process {pending_orders} pending orders promptly"
            ],
            'suggestions': [
                "Ask about specific customer feedback",
                "Inquire about order fulfillment status",
                "Check customer retention rates"
            ]
        }
    
    def _generate_schedule_response(self, entities: List[Dict], user_context: Dict) -> Dict:
        """Generate scheduling response"""
        # Extract date entities
        date_entities = [e for e in entities if e['label'] == 'DATE']
        date_text = date_entities[0]['text'] if date_entities else 'upcoming'
        
        # Generate mock schedule data
        activity = np.random.choice(['maintenance', 'production run', 'quality audit', 'delivery'])
        time = f"{np.random.randint(8, 17)}:{np.random.choice(['00', '30']):02d}"
        
        response_text = f"I found a scheduled {activity} for {date_text} at {time}. Would you like to modify this schedule or get more details about this activity?"
        
        return {
            'response': response_text,
            'confidence': 0.85,
            'data': {
                'activity': activity,
                'date': date_text,
                'time': time
            },
            'actionable_items': [
                f"Confirm {activity} schedule for {date_text} at {time}",
                f"Coordinate resources for the scheduled activity"
            ],
            'suggestions': [
                "Ask about other scheduled activities",
                "Inquire about resource availability",
                "Check for schedule conflicts"
            ]
        }
    
    def _generate_general_response(self, query: str, entities: List[Dict], user_context: Dict) -> Dict:
        """Generate general response for unclassified queries"""
        # Extract main topic from entities
        if entities:
            topic = entities[0]['text']
        else:
            # Extract key words from query
            words = query.split()
            topic = words[0] if words else 'your inquiry'
        
        response_text = self.response_templates['general_response'].format(topic=topic)
        
        return {
            'response': response_text,
            'confidence': 0.7,
            'suggestions': [
                "Try asking about today's production status",
                "Ask about quality metrics or issues",
                "Inquire about financial performance",
                "Check inventory levels",
                "Ask about maintenance schedules"
            ]
        }


def main():
    """Test the enhanced NLP processor"""
    print("Testing Enhanced NLP Processor...")
    
    # Create processor
    processor = EnhancedNLPProcessor()
    
    # Test queries
    test_queries = [
        "What is today's production status?",
        "Show me the quality report for batch B12345",
        "How is our financial performance this month?",
        "What is the current inventory level of paddy?",
        "When is the next maintenance scheduled for the huller?",
        "Are we compliant with all regulations?",
        "Generate a report on production trends",
        "How satisfied are our customers?",
        "What is scheduled for tomorrow?"
    ]
    
    user_context = {
        'user_id': 'test_user',
        'user_role': 'manager',
        'timestamp': datetime.now().isoformat()
    }
    
    # Process each query
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = processor.process_query(query, user_context)
        
        if result['success']:
            print(f"Intent: {result['intent']}")
            print(f"Response: {result['response']}")
            if result.get('entities'):
                print(f"Entities: {result['entities']}")
        else:
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()
