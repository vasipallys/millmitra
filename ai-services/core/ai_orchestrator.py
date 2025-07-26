try:
    from langchain.agents import AgentExecutor
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

class SimpleAgent:
    """Enhanced agent for rice mill specific responses"""
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Load domain-specific knowledge for each agent type"""
        knowledge = {
            'operations': {
                'production_status': 'Current production metrics and batch information',
                'quality_metrics': 'Quality test results and standards',
                'machine_status': 'Equipment performance and maintenance alerts',
                'inventory_levels': 'Stock levels and storage optimization'
            },
            'financial': {
                'cash_flow': 'Current cash position and forecasts',
                'profitability': 'Margin analysis and cost optimization',
                'payments': 'Outstanding payments and collection status',
                'pricing': 'Market rates and pricing recommendations'
            },
            'compliance': {
                'gst_status': 'Tax compliance and filing status',
                'quality_standards': 'Food safety and quality certifications',
                'documentation': 'Required permits and licenses',
                'audit_trail': 'Compliance audit and reporting'
            },
            'customer': {
                'satisfaction': 'Customer feedback and satisfaction metrics',
                'orders': 'Order status and delivery tracking',
                'relationships': 'Customer relationship insights',
                'support': 'Customer service and issue resolution'
            }
        }
        return knowledge.get(self.agent_type, {})

    async def process(self, query: str, context: dict):
        """Process query with domain-specific intelligence"""
        query_lower = query.lower()

        # Enhanced response based on agent type and query content
        if self.agent_type == 'operations':
            return self._handle_operations_query(query_lower, context)
        elif self.agent_type == 'financial':
            return self._handle_financial_query(query_lower, context)
        elif self.agent_type == 'compliance':
            return self._handle_compliance_query(query_lower, context)
        elif self.agent_type == 'customer':
            return self._handle_customer_query(query_lower, context)
        else:
            return f"AI {self.agent_type} agent processed: {query}"

    def _handle_operations_query(self, query: str, context: dict):
        """Handle operations-related queries"""
        if 'production' in query or 'batch' in query:
            return {
                'type': 'production_status',
                'data': {
                    'current_batches': context.get('active_batches', 3),
                    'daily_production': '2,500 kg',
                    'efficiency': '87%',
                    'quality_grade': 'A+',
                    'recommendations': ['Optimize moisture control', 'Schedule maintenance for Mill #2']
                }
            }
        elif 'quality' in query:
            return {
                'type': 'quality_metrics',
                'data': {
                    'average_grade': 'A',
                    'defect_rate': '2.1%',
                    'moisture_content': '13.2%',
                    'foreign_matter': '0.8%',
                    'recommendations': ['Improve cleaning process', 'Adjust drying parameters']
                }
            }
        elif 'inventory' in query or 'stock' in query:
            return {
                'type': 'inventory_status',
                'data': {
                    'paddy_stock': '15,000 kg',
                    'finished_goods': '8,500 kg',
                    'storage_utilization': '78%',
                    'reorder_alerts': ['Basmati paddy running low', 'Packaging material needed']
                }
            }
        else:
            return {'type': 'general', 'response': f"Operations insight for: {query}"}

    def _handle_financial_query(self, query: str, context: dict):
        """Handle financial-related queries"""
        if 'profit' in query or 'margin' in query:
            return {
                'type': 'profitability',
                'data': {
                    'gross_margin': '23.5%',
                    'net_profit': '₹2,45,000',
                    'cost_breakdown': {'raw_materials': '65%', 'labor': '15%', 'utilities': '12%', 'other': '8%'},
                    'recommendations': ['Negotiate better paddy prices', 'Optimize energy usage']
                }
            }
        elif 'cash' in query or 'payment' in query:
            return {
                'type': 'cash_flow',
                'data': {
                    'current_balance': '₹8,75,000',
                    'receivables': '₹3,20,000',
                    'payables': '₹1,85,000',
                    'forecast_30_days': '₹12,10,000',
                    'alerts': ['Payment due from ABC Traders', 'Farmer payment scheduled tomorrow']
                }
            }
        else:
            return {'type': 'general', 'response': f"Financial insight for: {query}"}

    def _handle_compliance_query(self, query: str, context: dict):
        """Handle compliance-related queries"""
        if 'gst' in query or 'tax' in query:
            return {
                'type': 'gst_status',
                'data': {
                    'filing_status': 'Up to date',
                    'next_due_date': '20th of next month',
                    'input_credit': '₹45,000',
                    'output_liability': '₹67,000',
                    'recommendations': ['File GSTR-1 by 11th', 'Reconcile purchase invoices']
                }
            }
        elif 'quality' in query or 'standard' in query:
            return {
                'type': 'quality_compliance',
                'data': {
                    'certifications': ['FSSAI', 'ISO 22000'],
                    'audit_status': 'Compliant',
                    'next_audit': '3 months',
                    'action_items': ['Update HACCP documentation', 'Calibrate testing equipment']
                }
            }
        else:
            return {'type': 'general', 'response': f"Compliance insight for: {query}"}

    def _handle_customer_query(self, query: str, context: dict):
        """Handle customer-related queries"""
        if 'satisfaction' in query or 'feedback' in query:
            return {
                'type': 'customer_satisfaction',
                'data': {
                    'average_rating': '4.6/5',
                    'response_rate': '89%',
                    'top_complaints': ['Delivery delays', 'Packaging issues'],
                    'top_compliments': ['Quality consistency', 'Competitive pricing'],
                    'recommendations': ['Improve logistics', 'Upgrade packaging']
                }
            }
        elif 'order' in query:
            return {
                'type': 'order_status',
                'data': {
                    'pending_orders': 12,
                    'processing_orders': 8,
                    'shipped_today': 15,
                    'delivery_performance': '94%',
                    'alerts': ['Rush order from XYZ Corp', 'Delayed shipment to Mumbai']
                }
            }
        else:
            return {'type': 'general', 'response': f"Customer insight for: {query}"}

class RiceMillAIOrchestrator:
    def __init__(self):
        self.agents = {
            'operations': SimpleAgent('operations'),
            'financial': SimpleAgent('financial'),
            'compliance': SimpleAgent('compliance'),
            'customer': SimpleAgent('customer')
        }

        if LANGCHAIN_AVAILABLE:
            self.memory = ConversationBufferMemory()
        else:
            self.memory = None
        
    async def process_query(self, query: str, context: dict):
        try:
            # Route query to appropriate agent
            agent_type = self._classify_query(query)
            agent = self.agents.get(agent_type, self.agents['operations'])

            response = await agent.process(query, context)
            return self._format_response(response)
        except Exception as e:
            return f"AI processing error: {str(e)}"

    def _classify_query(self, query: str) -> str:
        """Classify query to determine which agent should handle it"""
        query_lower = query.lower()

        if any(word in query_lower for word in ['money', 'cost', 'price', 'revenue', 'profit', 'finance']):
            return 'financial'
        elif any(word in query_lower for word in ['customer', 'client', 'buyer', 'order', 'sale']):
            return 'customer'
        elif any(word in query_lower for word in ['compliance', 'regulation', 'standard', 'audit']):
            return 'compliance'
        else:
            return 'operations'

    def _format_response(self, response: str) -> str:
        """Format the agent response"""
        if isinstance(response, dict):
            return {
                'success': True,
                'data': response,
                'timestamp': '2024-01-01T00:00:00Z',
                'source': 'rice_mill_ai',
                'confidence': 0.85
            }
        else:
            return f"🤖 Rice Mill AI: {response}"

    def get_natural_language_response(self, query: str, context: dict = None):
        """Generate natural language responses for common queries"""
        query_lower = query.lower()
        context = context or {}

        # Common natural language patterns
        if 'why is production low' in query_lower:
            return {
                'type': 'analysis',
                'response': "Production is currently at 87% efficiency. Main factors affecting output: 1) Mill #2 needs maintenance (reducing capacity by 15%), 2) Moisture content in current paddy batch is higher than optimal (13.8% vs target 13.2%), 3) Two operators are on leave today. Recommendation: Schedule Mill #2 maintenance tonight and adjust drying parameters.",
                'actionable_items': [
                    'Schedule Mill #2 maintenance',
                    'Adjust paddy drying parameters',
                    'Consider overtime for remaining operators'
                ]
            }

        elif 'show me today' in query_lower or 'today\'s' in query_lower:
            return {
                'type': 'daily_summary',
                'response': "Today's Summary: Production: 2,500kg (87% of target), Quality Grade: A+, Revenue: ₹3,75,000, New Orders: 8, Customer Satisfaction: 4.6/5. Key highlights: Completed large order for ABC Traders, received quality certification renewal.",
                'metrics': {
                    'production': '2,500 kg',
                    'efficiency': '87%',
                    'revenue': '₹3,75,000',
                    'orders': 8,
                    'satisfaction': '4.6/5'
                }
            }

        elif 'best performing' in query_lower:
            return {
                'type': 'performance_analysis',
                'response': "Best performing areas today: 1) Quality Control (99.2% pass rate), 2) Customer Service (4.8/5 rating), 3) Basmati processing line (95% efficiency). Areas for improvement: 1) Sona Masuri line (78% efficiency), 2) Packaging speed (12% below target).",
                'top_performers': ['Quality Control', 'Customer Service', 'Basmati Line'],
                'improvement_areas': ['Sona Masuri Line', 'Packaging Department']
            }

        else:
            return None