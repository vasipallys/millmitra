from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import PaddyStock, ProductStock, User
# Temporarily disabled until services are fixed
# from services.inventory_service import InventoryService
# from services.ai_inventory_service import AIInventoryService
from extensions import db
from datetime import datetime
import json

inventory_bp = Blueprint('inventory', __name__)
# Temporarily disabled until services are fixed
# inventory_service = InventoryService()
# ai_inventory = AIInventoryService()

# Simple endpoints for frontend compatibility
@inventory_bp.route('/paddy', methods=['GET'])
@jwt_required()
def get_paddy():
    """Simple paddy stock endpoint for frontend compatibility"""
    paddy_stocks = PaddyStock.query.all()
    return jsonify({
        'stocks': [stock.to_dict() for stock in paddy_stocks],
        'total_quantity': sum(stock.quantity for stock in paddy_stocks),
        'total_value': sum(stock.quantity * stock.purchase_price for stock in paddy_stocks),
        'message': 'Paddy stock data loaded successfully'
    })

@inventory_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    """Simple product stock endpoint for frontend compatibility"""
    product_stocks = ProductStock.query.all()
    return jsonify({
        'stocks': [stock.to_dict() for stock in product_stocks],
        'total_quantity': sum(stock.quantity for stock in product_stocks),
        'total_value': sum(stock.quantity * stock.market_price for stock in product_stocks),
        'message': 'Product stock data loaded successfully'
    })

@inventory_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_inventory_overview():
    """Get inventory overview statistics"""
    try:
        # Get paddy stock totals
        paddy_stocks = PaddyStock.query.all()
        total_paddy_quantity = sum(stock.remaining_quantity or 0 for stock in paddy_stocks)
        total_paddy_value = sum((stock.remaining_quantity or 0) * stock.purchase_price for stock in paddy_stocks)

        # Get product stock totals
        product_stocks = ProductStock.query.all()
        total_product_quantity = sum(stock.quantity for stock in product_stocks)
        total_product_value = sum(stock.quantity * (stock.market_price or 0) for stock in product_stocks)

        # Calculate low stock items (less than 100 units)
        low_stock_paddy = len([s for s in paddy_stocks if (s.remaining_quantity or 0) < 100])
        low_stock_products = len([s for s in product_stocks if s.quantity < 100])

        return jsonify({
            'success': True,
            'overview': {
                'total_paddy_stock': total_paddy_quantity,
                'total_product_stock': total_product_quantity,
                'total_value': total_paddy_value + total_product_value,
                'paddy_value': total_paddy_value,
                'product_value': total_product_value,
                'low_stock_items': low_stock_paddy + low_stock_products,
                'total_items': len(paddy_stocks) + len(product_stocks),
                'recent_movements': 0  # TODO: Implement when movement tracking is added
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching inventory overview: {str(e)}'
        }), 500

@inventory_bp.route('/reorder-alerts', methods=['GET'])
@jwt_required()
def get_reorder_alerts():
    """Get items that need reordering"""
    try:
        alerts = []

        # Check paddy stocks
        paddy_stocks = PaddyStock.query.all()
        for stock in paddy_stocks:
            if (stock.remaining_quantity or 0) < 100:  # Reorder threshold
                alerts.append({
                    'id': f'paddy_{stock.id}',
                    'item_name': f'{stock.variety} Paddy',
                    'item_type': 'paddy',
                    'current_stock': stock.remaining_quantity or 0,
                    'reorder_level': 100,
                    'priority': 'high' if (stock.remaining_quantity or 0) < 50 else 'medium',
                    'location': stock.warehouse_id or 'Unknown'
                })

        # Check product stocks
        product_stocks = ProductStock.query.all()
        for stock in product_stocks:
            if stock.quantity < 100:  # Reorder threshold
                alerts.append({
                    'id': f'product_{stock.id}',
                    'item_name': stock.product_name,
                    'item_type': 'product',
                    'current_stock': stock.quantity,
                    'reorder_level': 100,
                    'priority': 'high' if stock.quantity < 50 else 'medium',
                    'location': stock.warehouse_id or 'Unknown'
                })

        return jsonify({
            'success': True,
            'alerts': alerts,
            'total': len(alerts)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching reorder alerts: {str(e)}'
        }), 500

@inventory_bp.route('/valuation', methods=['GET'])
@jwt_required()
def get_inventory_valuation():
    """Get inventory valuation breakdown"""
    try:
        # Calculate paddy valuation by variety
        paddy_stocks = PaddyStock.query.all()
        paddy_by_variety = {}
        total_paddy_value = 0

        for stock in paddy_stocks:
            variety = stock.variety
            value = (stock.remaining_quantity or 0) * stock.purchase_price
            total_paddy_value += value

            if variety in paddy_by_variety:
                paddy_by_variety[variety] += value
            else:
                paddy_by_variety[variety] = value

        # Calculate product valuation by type
        product_stocks = ProductStock.query.all()
        product_by_type = {}
        total_product_value = 0

        for stock in product_stocks:
            product_type = stock.product_type
            value = stock.quantity * (stock.market_price or 0)
            total_product_value += value

            if product_type in product_by_type:
                product_by_type[product_type] += value
            else:
                product_by_type[product_type] = value

        # Format for frontend
        by_category = []
        for variety, value in paddy_by_variety.items():
            by_category.append({
                'category': f'{variety} (Paddy)',
                'value': value,
                'type': 'paddy'
            })

        for product_type, value in product_by_type.items():
            by_category.append({
                'category': f'{product_type} (Product)',
                'value': value,
                'type': 'product'
            })

        return jsonify({
            'success': True,
            'valuation': {
                'total_value': total_paddy_value + total_product_value,
                'paddy_value': total_paddy_value,
                'product_value': total_product_value,
                'by_category': sorted(by_category, key=lambda x: x['value'], reverse=True)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching inventory valuation: {str(e)}'
        }), 500

@inventory_bp.route('/movements', methods=['GET'])
@jwt_required()
def get_stock_movements():
    """Get stock movements/transactions"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        movement_type = request.args.get('type')  # 'in', 'out', 'transfer'
        item_type = request.args.get('item_type')  # 'paddy', 'product'

        # Mock data for now - in production this would come from a StockMovement model
        movements = [
            {
                'id': 1,
                'date': '2025-07-26T10:00:00',
                'type': 'in',
                'item_type': 'paddy',
                'item_name': 'Basmati Paddy',
                'quantity': 1000,
                'unit': 'kg',
                'reference': 'PUR-001',
                'source': 'Farmer - Siva Kumar',
                'destination': 'Warehouse A',
                'notes': 'Fresh paddy procurement'
            },
            {
                'id': 2,
                'date': '2025-07-26T14:30:00',
                'type': 'out',
                'item_type': 'product',
                'item_name': 'Basmati Rice',
                'quantity': 500,
                'unit': 'kg',
                'reference': 'SAL-001',
                'source': 'Warehouse A',
                'destination': 'Customer - ABC Store',
                'notes': 'Sale to retail customer'
            },
            {
                'id': 3,
                'date': '2025-07-26T16:00:00',
                'type': 'transfer',
                'item_type': 'paddy',
                'item_name': 'Sona Masuri Paddy',
                'quantity': 750,
                'unit': 'kg',
                'reference': 'TRF-001',
                'source': 'Warehouse A',
                'destination': 'Processing Unit',
                'notes': 'Transfer for processing'
            }
        ]

        # Apply filters if provided
        if movement_type:
            movements = [m for m in movements if m['type'] == movement_type]

        if item_type:
            movements = [m for m in movements if m['item_type'] == item_type]

        return jsonify({
            'success': True,
            'movements': movements,
            'total': len(movements),
            'summary': {
                'total_in': sum(m['quantity'] for m in movements if m['type'] == 'in'),
                'total_out': sum(m['quantity'] for m in movements if m['type'] == 'out'),
                'total_transfers': sum(m['quantity'] for m in movements if m['type'] == 'transfer')
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching stock movements: {str(e)}'
        }), 500

@inventory_bp.route('/movements', methods=['POST'])
@jwt_required()
def create_stock_movement():
    """Create a new stock movement/transaction"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        # Validate required fields - handle both frontend formats
        movement_type = data.get('movement_type') or data.get('type')
        quantity = data.get('quantity')

        if not movement_type:
            return jsonify({
                'success': False,
                'message': 'Missing required field: movement_type or type'
            }), 400

        if not quantity:
            return jsonify({
                'success': False,
                'message': 'Missing required field: quantity'
            }), 400

        # Generate movement ID
        movement_id = f"MOV{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Create movement record (for now, just return success)
        # In production, this would save to a StockMovement model
        movement = {
            'id': movement_id,
            'date': datetime.utcnow().isoformat(),
            'type': movement_type,
            'movement_type': movement_type,  # Support both field names
            'item_type': data.get('item_type', 'unknown'),
            'item_name': data.get('item_name') or data.get('stock_name', 'Unknown Item'),
            'quantity': float(quantity),
            'unit': data.get('unit', 'kg'),
            'unit_price': float(data.get('unit_price', 0)),
            'total_value': float(data.get('total_value', 0)),
            'reference': data.get('reference_number') or data.get('reference', ''),
            'source': data.get('location_from') or data.get('source', ''),
            'destination': data.get('location_to') or data.get('destination', ''),
            'supplier_customer': data.get('supplier_customer', ''),
            'reason': data.get('reason', ''),
            'notes': data.get('notes', ''),
            'batch_number': data.get('batch_number', ''),
            'expiry_date': data.get('expiry_date', ''),
            'stock_id': data.get('stock_id', ''),
            'created_by': user_id,
            'created_at': datetime.utcnow().isoformat()
        }

        # TODO: In production, save to database
        # stock_movement = StockMovement(**movement)
        # db.session.add(stock_movement)
        # db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Stock movement created successfully',
            'movement': movement
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating stock movement: {str(e)}'
        }), 500

# Paddy Stock Management
@inventory_bp.route('/paddy-stock', methods=['GET'])
@jwt_required()
def get_paddy_stock():
    variety = request.args.get('variety', '')
    location = request.args.get('location', '')
    
    # Query paddy stocks directly from database
    query = PaddyStock.query
    if variety:
        query = query.filter(PaddyStock.variety.ilike(f'%{variety}%'))
    if location:
        query = query.filter(PaddyStock.location.ilike(f'%{location}%'))

    stocks = query.all()

    return jsonify({
        'success': True,
        'stocks': [s.to_dict() for s in stocks],
        'total': len(stocks),
        'message': 'Paddy stock data loaded successfully'
    })

@inventory_bp.route('/paddy-stock', methods=['POST'])
@jwt_required()
def add_paddy_stock():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        data = request.get_json()

        # Validate required fields
        required_fields = ['variety', 'quantity', 'quality_grade']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400

        # Generate stock ID
        stock_count = PaddyStock.query.count() + 1
        stock_id = f"PS{stock_count:06d}"

        # Calculate total amount
        quantity = float(data['quantity'])
        purchase_price = float(data.get('purchase_price', 0))
        total_amount = quantity * purchase_price

        # Create new paddy stock entry
        stock = PaddyStock(
            stock_id=stock_id,
            farmer_id=data.get('farmer_id', 1),  # Default to farmer ID 1 if not provided
            variety=data['variety'],
            quantity=quantity,
            purchase_price=purchase_price,
            total_amount=total_amount,
            quality_grade=data['quality_grade'],
            moisture_content=float(data.get('moisture_content', 0)),
            warehouse_id=data.get('location', 'WH001'),
            purchase_date=datetime.utcnow(),
            created_by=user_id
        )

        db.session.add(stock)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Paddy stock added successfully',
            'stock': stock.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error adding paddy stock: {str(e)}'
        }), 500, 201

@inventory_bp.route('/paddy-stock/<int:stock_id>', methods=['PUT'])
@jwt_required()
def update_paddy_stock(stock_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    stock = inventory_service.update_paddy_stock(stock_id, user, data)
    
    return jsonify({
        'success': True,
        'stock': stock.to_dict()
    })

# Product Stock Management
@inventory_bp.route('/product-stock', methods=['GET'])
@jwt_required()
def get_product_stock():
    product_type = request.args.get('product_type', '')
    grade = request.args.get('grade', '')

    # Query product stocks directly from database
    query = ProductStock.query
    if product_type:
        query = query.filter(ProductStock.product_type.ilike(f'%{product_type}%'))
    if grade:
        query = query.filter(ProductStock.quality_grade.ilike(f'%{grade}%'))

    stocks = query.all()

    return jsonify({
        'success': True,
        'stocks': [s.to_dict() for s in stocks],
        'total': len(stocks),
        'message': 'Product stock data loaded successfully'
    })

@inventory_bp.route('/product-stock', methods=['POST'])
@jwt_required()
def add_product_stock():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        data = request.get_json()

        # Validate required fields
        required_fields = ['product_type', 'quantity', 'quality_grade']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400

        # Generate product ID
        product_count = ProductStock.query.count() + 1
        product_id = f"PR{product_count:06d}"

        # Create new product stock entry
        stock = ProductStock(
            product_id=product_id,
            product_name=data.get('product_name', data['product_type']),
            product_type=data['product_type'],
            variety=data.get('variety', ''),
            grade=data['quality_grade'],
            quantity=float(data['quantity']),
            unit_cost=float(data.get('production_cost', 0)),
            market_price=float(data.get('market_price', 0)),
            warehouse_id=data.get('location', 'WH001'),
            production_date=datetime.utcnow(),
            created_by=user_id
        )

        db.session.add(stock)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Product stock added successfully',
            'stock': stock.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error adding product stock: {str(e)}'
        }), 500

# Stock Movements - Temporarily disabled
# @inventory_bp.route('/transactions', methods=['GET'])
# @jwt_required()
# def get_transactions():
#     page = request.args.get('page', 1, type=int)
#     per_page = request.args.get('per_page', 20, type=int)
#     transaction_type = request.args.get('type', '')
#
#     transactions = inventory_service.get_transactions(page, per_page, transaction_type)
#
#     # AI transaction pattern analysis
#     pattern_analysis = ai_inventory.analyze_transaction_patterns([t.to_dict() for t in transactions['items']])
#
#     return jsonify({
#         'transactions': [t.to_dict() for t in transactions['items']],
#         'pagination': transactions['pagination'],
#         'pattern_analysis': pattern_analysis
#     })

@inventory_bp.route('/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI transaction validation
    validation_result = ai_inventory.validate_transaction(data)
    
    if not validation_result['valid']:
        return jsonify({
            'success': False,
            'errors': validation_result['errors']
        }), 400
    
    # AI impact analysis
    impact_analysis = ai_inventory.analyze_transaction_impact(data)
    
    # AI fraud detection
    fraud_check = ai_inventory.detect_transaction_fraud(data)
    
    if fraud_check['is_suspicious']:
        return jsonify({
            'success': False,
            'message': 'Transaction flagged for review',
            'fraud_indicators': fraud_check['indicators']
        }), 400
    
    transaction = inventory_service.create_transaction(user, data)
    
    # AI post-transaction recommendations
    recommendations = ai_inventory.get_post_transaction_recommendations(transaction.id)
    
    return jsonify({
        'success': True,
        'transaction': transaction.to_dict(),
        'impact_analysis': impact_analysis,
        'recommendations': recommendations
    }), 201

# Inventory Analytics - Temporarily disabled
# @inventory_bp.route('/analytics/overview', methods=['GET'])
# @jwt_required()
# def get_inventory_analytics_overview():
#     overview = inventory_service.get_inventory_overview()
#
#     # AI-enhanced analytics
#     ai_analytics = ai_inventory.enhance_inventory_analytics(overview)
#
#     return jsonify({
#         'overview': overview,
#         'ai_analytics': ai_analytics
#     })

@inventory_bp.route('/analytics/turnover', methods=['GET'])
@jwt_required()
def get_inventory_turnover():
    days = request.args.get('days', 30, type=int)
    turnover = inventory_service.calculate_inventory_turnover(days)
    
    return jsonify(turnover)

@inventory_bp.route('/analytics/valuation', methods=['GET'])
@jwt_required()
def get_inventory_analytics_valuation():
    method = request.args.get('method', 'fifo')
    
    valuation = inventory_service.calculate_inventory_valuation(method)
    
    # AI valuation optimization
    optimization = ai_inventory.optimize_inventory_valuation(valuation)
    
    # AI market price analysis
    market_analysis = ai_inventory.analyze_market_prices()
    
    return jsonify({
        'valuation': valuation,
        'optimization': optimization,
        'market_analysis': market_analysis
    })

# Reorder Management
@inventory_bp.route('/reorder-rules', methods=['GET'])
@jwt_required()
def get_reorder_rules():
    rules = inventory_service.get_reorder_rules()
    
    # AI rule effectiveness analysis
    effectiveness_analysis = ai_inventory.analyze_rule_effectiveness([rule.to_dict() for rule in rules])
    
    return jsonify({
        'rules': [rule.to_dict() for rule in rules],
        'effectiveness_analysis': effectiveness_analysis
    })

@inventory_bp.route('/reorder-rules', methods=['POST'])
@jwt_required()
def create_reorder_rule():
    user_id = get_jwt_identity()
    
    data = request.get_json()
    
    # AI optimization of reorder parameters
    optimized_rule = ai_inventory.optimize_reorder_rule(data)
    
    rule = inventory_service.create_reorder_rule(optimized_rule)
    
    return jsonify({
        'success': True,
        'rule': rule.to_dict(),
        'optimization_notes': optimized_rule.get('optimization_notes', [])
    }), 201

@inventory_bp.route('/reorder-alerts-advanced', methods=['GET'])
@jwt_required()
def get_reorder_alerts_advanced():
    alerts = inventory_service.check_reorder_alerts()
    
    # AI prioritization of alerts
    prioritized_alerts = ai_inventory.prioritize_reorder_alerts(alerts)
    
    return jsonify({
        'alerts': prioritized_alerts
    })

# Supplier Management
@inventory_bp.route('/suppliers', methods=['GET'])
@jwt_required()
def get_suppliers():
    suppliers = inventory_service.get_suppliers()
    
    # AI supplier performance analysis
    performance_analysis = ai_inventory.analyze_supplier_performance(suppliers)
    
    return jsonify({
        'suppliers': suppliers,
        'performance_analysis': performance_analysis
    })

@inventory_bp.route('/suppliers', methods=['POST'])
@jwt_required()
def create_supplier():
    data = request.get_json()
    supplier = inventory_service.create_supplier(data)
    
    return jsonify({
        'success': True,
        'supplier': supplier.to_dict()
    }), 201

# AI-Powered Features
@inventory_bp.route('/ai/demand-forecast', methods=['POST'])
@jwt_required()
def get_ai_demand_forecast():
    data = request.get_json()
    forecast = ai_inventory.generate_demand_forecast(data)
    
    return jsonify(forecast)

@inventory_bp.route('/ai/optimize-stock-levels', methods=['POST'])
@jwt_required()
def optimize_stock_levels():
    data = request.get_json()
    optimization = ai_inventory.optimize_stock_levels(data)
    
    return jsonify(optimization)

@inventory_bp.route('/ai/price-recommendations', methods=['POST'])
@jwt_required()
def get_price_recommendations():
    data = request.get_json()
    recommendations = ai_inventory.get_pricing_recommendations(data)
    
    return jsonify(recommendations)

# Inventory Reports
@inventory_bp.route('/reports/stock-aging', methods=['GET'])
@jwt_required()
def get_stock_aging_report():
    report = inventory_service.generate_stock_aging_report()
    
    return jsonify(report)

@inventory_bp.route('/reports/movement-summary', methods=['GET'])
@jwt_required()
def get_movement_summary():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    summary = inventory_service.generate_movement_summary(start_date, end_date)
    
    return jsonify(summary)

@inventory_bp.route('/reports/low-stock', methods=['GET'])
@jwt_required()
def get_low_stock_report():
    report = inventory_service.generate_low_stock_report()
    
    # AI recommendations for low stock items
    ai_recommendations = ai_inventory.get_low_stock_recommendations(report)
    
    return jsonify({
        'report': report,
        'ai_recommendations': ai_recommendations
    })

@inventory_bp.route('/waste-tracking', methods=['GET'])
@jwt_required()
def get_waste_tracking():
    period = request.args.get('period', 'monthly')
    
    waste_data = inventory_service.get_waste_tracking(period)
    
    # AI waste analysis
    waste_analysis = ai_inventory.analyze_waste_patterns(waste_data)
    
    # AI waste reduction recommendations
    reduction_recommendations = ai_inventory.recommend_waste_reduction(waste_data)
    
    return jsonify({
        'waste_data': waste_data,
        'analysis': waste_analysis,
        'reduction_recommendations': reduction_recommendations
    })

@inventory_bp.route('/optimization', methods=['POST'])
@jwt_required()
def optimize_inventory():
    data = request.get_json()
    optimization_type = data.get('type', 'cost')
    
    # AI inventory optimization
    optimization_result = ai_inventory.optimize_inventory_levels(data, optimization_type)
    
    return jsonify(optimization_result)

@inventory_bp.route('/aging-analysis', methods=['GET'])
@jwt_required()
def get_aging_analysis():
    stock_type = request.args.get('stock_type', 'all')
    
    aging_data = inventory_service.get_aging_analysis(stock_type)
    
    # AI aging insights
    aging_insights = ai_inventory.analyze_stock_aging(aging_data)
    
    # AI disposal recommendations
    disposal_recommendations = ai_inventory.recommend_stock_disposal(aging_data)
    
    return jsonify({
        'aging_data': aging_data,
        'insights': aging_insights,
        'disposal_recommendations': disposal_recommendations
    })

@inventory_bp.route('/turnover-analysis', methods=['GET'])
@jwt_required()
def get_turnover_analysis():
    period_days = request.args.get('days', 90, type=int)
    
    turnover_data = inventory_service.calculate_turnover_rates(period_days)
    
    # AI turnover optimization
    turnover_optimization = ai_inventory.optimize_turnover_rates(turnover_data)
    
    return jsonify({
        'turnover_data': turnover_data,
        'optimization': turnover_optimization
    })

@inventory_bp.route('/quality-tracking', methods=['GET'])
@jwt_required()
def get_quality_tracking():
    stock_type = request.args.get('type', 'all')  # paddy, product, all
    
    quality_data = inventory_service.get_quality_tracking(stock_type)
    
    # AI quality trend analysis
    quality_analysis = ai_inventory.analyze_quality_trends(quality_data)
    
    return jsonify({
        'quality_data': quality_data,
        'ai_analysis': quality_analysis
    })

@inventory_bp.route('/storage-optimization', methods=['GET'])
@jwt_required()
def get_storage_optimization():
    # AI storage space optimization
    optimization = ai_inventory.optimize_storage_utilization()
    
    return jsonify(optimization)

@inventory_bp.route('/predictive-maintenance', methods=['GET'])
@jwt_required()
def get_predictive_maintenance():
    # AI predictive maintenance for storage equipment
    maintenance_predictions = ai_inventory.predict_equipment_maintenance()
    
    return jsonify({'maintenance_predictions': maintenance_predictions})

@inventory_bp.route('/cost-analysis', methods=['GET'])
@jwt_required()
def get_cost_analysis():
    period_days = request.args.get('days', 30, type=int)
    
    cost_data = inventory_service.get_inventory_costs(period_days)
    
    # AI cost optimization
    cost_optimization = ai_inventory.optimize_inventory_costs(cost_data)
    
    return jsonify({
        'cost_data': cost_data,
        'optimization': cost_optimization
    })

@inventory_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_inventory_dashboard():
    user_id = get_jwt_identity()
    
    dashboard_data = inventory_service.get_dashboard_data()
    
    # AI-enhanced dashboard insights
    ai_insights = ai_inventory.generate_dashboard_insights(dashboard_data)
    
    # AI stock level optimization
    optimization_suggestions = ai_inventory.get_stock_optimization_suggestions()
    
    return jsonify({
        'dashboard': dashboard_data,
        'ai_insights': ai_insights,
        'optimization_suggestions': optimization_suggestions
    })

@inventory_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_stock_alerts():
    alert_type = request.args.get('type', '')
    priority = request.args.get('priority', '')
    
    alerts = inventory_service.get_stock_alerts(alert_type, priority)
    
    # AI alert prioritization
    prioritized_alerts = ai_inventory.prioritize_alerts([a.to_dict() for a in alerts])
    
    # AI resolution suggestions
    resolution_suggestions = ai_inventory.suggest_alert_resolutions(prioritized_alerts)
    
    return jsonify({
        'alerts': prioritized_alerts,
        'resolution_suggestions': resolution_suggestions
    })

@inventory_bp.route('/reorder-points', methods=['GET'])
@jwt_required()
def get_reorder_points():
    # AI-calculated reorder points
    reorder_points = ai_inventory.calculate_optimal_reorder_points()
    
    return jsonify({'reorder_points': reorder_points})

@inventory_bp.route('/reorder-points', methods=['POST'])
@jwt_required()
def update_reorder_points():
    data = request.get_json()
    
    # AI validation of reorder points
    validation = ai_inventory.validate_reorder_points(data)
    
    if validation['valid']:
        result = inventory_service.update_reorder_points(data['reorder_points'])
        return jsonify({'success': True, 'updated': result})
    else:
        return jsonify({
            'success': False,
            'errors': validation['errors']
        }), 400

@inventory_bp.route('/demand-forecast', methods=['GET'])
@jwt_required()
def get_demand_forecast():
    product_type = request.args.get('product_type', '')
    days = request.args.get('days', 30, type=int)
    
    # AI demand forecasting
    forecast = ai_inventory.forecast_demand(product_type, days)
    
    # AI seasonal analysis
    seasonal_analysis = ai_inventory.analyze_seasonal_patterns(product_type)
    
    return jsonify({
        'forecast': forecast,
        'seasonal_analysis': seasonal_analysis
    })

@inventory_bp.route('/cycle-count', methods=['POST'])
@jwt_required()
def initiate_cycle_count():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI cycle count optimization
    optimized_plan = ai_inventory.optimize_cycle_count_plan(data)
    
    cycle_count = inventory_service.initiate_cycle_count(user, optimized_plan)
    
    return jsonify({
        'success': True,
        'cycle_count': cycle_count.to_dict(),
        'optimized_plan': optimized_plan
    }), 201

@inventory_bp.route('/supplier-performance', methods=['GET'])
@jwt_required()
def get_supplier_performance():
    supplier_id = request.args.get('supplier_id', type=int)
    
    performance_data = inventory_service.get_supplier_performance(supplier_id)
    
    # AI supplier analysis
    supplier_analysis = ai_inventory.analyze_supplier_performance(performance_data)
    
    # AI supplier recommendations
    supplier_recommendations = ai_inventory.recommend_supplier_actions(performance_data)
    
    return jsonify({
        'performance_data': performance_data,
        'analysis': supplier_analysis,
        'recommendations': supplier_recommendations
    })

@inventory_bp.route('/quality-trends', methods=['GET'])
@jwt_required()
def get_quality_trends():
    product_type = request.args.get('product_type', '')
    period = request.args.get('period', 'quarterly')
    
    quality_data = inventory_service.get_quality_trends(product_type, period)
    
    # AI quality analysis
    quality_analysis = ai_inventory.analyze_quality_trends(quality_data)
    
    # AI quality improvement recommendations
    improvement_recommendations = ai_inventory.recommend_quality_improvements(quality_data)
    
    return jsonify({
        'quality_data': quality_data,
        'analysis': quality_analysis,
        'improvement_recommendations': improvement_recommendations
    })

@inventory_bp.route('/smart-alerts', methods=['GET'])
@jwt_required()
def get_smart_alerts():
    # AI-generated smart alerts
    smart_alerts = ai_inventory.generate_smart_alerts()
    
    return jsonify({'smart_alerts': smart_alerts})

@inventory_bp.route('/batch-tracking', methods=['GET'])
@jwt_required()
def get_batch_tracking():
    batch_id = request.args.get('batch_id', '')
    
    tracking_data = inventory_service.get_batch_tracking(batch_id)
    
    # AI batch analysis
    batch_analysis = ai_inventory.analyze_batch_performance(tracking_data)
    
    return jsonify({
        'tracking_data': tracking_data,
        'analysis': batch_analysis
    })

