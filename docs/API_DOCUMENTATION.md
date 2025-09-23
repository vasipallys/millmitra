# Rice Mill ERP API Documentation

**Version:** 1.0.0  
**Generated:** 2025-08-18T20:23:54.504539  
**Base URL:** http://localhost:5000

## Authentication

This API uses JWT (JSON Web Token) authentication.

**Login Endpoint:** `POST /api/auth/login`

**Request:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

**Using the Token:**
Include the token in the Authorization header:
```
Authorization: Bearer <your_token_here>
```

## API Endpoints


### Authentication

**Base Path:** `/api/auth`

#### `POST` /api/auth/suggest-username

**Function:** `suggest_username`

**Description:** AI-powered username suggestions

---

#### `POST` /api/auth/login

**Function:** `login`

**Description:** Endpoint for login

**Sample Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Sample Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

---

#### `GET` /api/auth/me

**Function:** `get_current_user`

**Description:** Get current user information

---

#### `POST` /api/auth/verify-otp

**Function:** `verify_otp`

**Description:** Endpoint for verify_otp

---

#### `POST` /api/auth/logout

**Function:** `logout`

**Description:** Logout user and invalidate session

---

#### `POST` /api/auth/voice-login

**Function:** `voice_login`

**Description:** Endpoint for voice_login

**Sample Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Sample Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

---


### Dashboard

**Base Path:** `/api/dashboard`

#### `GET` /api/dashboard/overview

**Function:** `get_dashboard_overview`

**Description:** Endpoint for get_dashboard_overview

---

#### `GET` /api/dashboard/widgets

**Function:** `get_smart_widgets`

**Description:** Endpoint for get_smart_widgets

---

#### `GET` /api/dashboard/insights

**Function:** `get_ai_insights`

**Description:** Endpoint for get_ai_insights

---

#### `GET` /api/dashboard/alerts

**Function:** `get_smart_alerts`

**Description:** Endpoint for get_smart_alerts

---

#### `GET` /api/dashboard/metrics/production

**Function:** `get_production_metrics`

**Description:** Endpoint for get_production_metrics

---

#### `GET` /api/dashboard/metrics/quality

**Function:** `get_quality_metrics`

**Description:** Endpoint for get_quality_metrics

---

#### `GET` /api/dashboard/metrics/inventory

**Function:** `get_inventory_metrics`

**Description:** Endpoint for get_inventory_metrics

---

#### `GET` /api/dashboard/metrics/financial

**Function:** `get_financial_metrics`

**Description:** Endpoint for get_financial_metrics

---

#### `GET` /api/dashboard/predictions

**Function:** `get_predictions`

**Description:** Endpoint for get_predictions

---

#### `POST` /api/dashboard/customize

**Function:** `customize_dashboard`

**Description:** Endpoint for customize_dashboard

---


### Farmer Management

**Base Path:** `/api/farmer`

#### `POST` /api/farmer/register

**Function:** `register_farmer`

**Description:** Endpoint for register_farmer

---

#### `GET` /api/farmer/list

**Function:** `get_farmers`

**Description:** Endpoint for get_farmers

---

#### `GET` /api/farmer/<int:farmer_id>

**Function:** `get_farmer_details`

**Description:** Endpoint for get_farmer_details

---

#### `PUT` /api/farmer/<int:farmer_id>

**Function:** `update_farmer`

**Description:** Submit farmer information update for verification

---

#### `GET` /api/farmer/edit-requests

**Function:** `get_edit_requests`

**Description:** Get farmer edit requests

---

#### `POST` /api/farmer/edit-requests/<int:request_id>/approve

**Function:** `approve_edit_request`

**Description:** Approve farmer edit request

---

#### `POST` /api/farmer/edit-requests/<int:request_id>/reject

**Function:** `reject_edit_request`

**Description:** Reject farmer edit request

---

#### `POST` /api/farmer/edit-requests/create-sample

**Function:** `create_sample_edit_requests`

**Description:** Create sample edit requests for testing

---

#### `GET` /api/farmer/contracts

**Function:** `get_contracts`

**Description:** Get farmer contracts with optional filtering

---

#### `PUT` /api/farmer/contracts/<int:contract_id>

**Function:** `update_contract`

**Description:** Update contract information

---

#### `POST` /api/farmer/contracts

**Function:** `create_contract`

**Description:** Endpoint for create_contract

---

#### `GET` /api/farmer/procurements

**Function:** `get_procurements`

**Description:** Get procurement records with optional filtering

---

#### `POST` /api/farmer/procurements

**Function:** `record_procurement`

**Description:** Endpoint for record_procurement

---

#### `POST` /api/farmer/payments

**Function:** `process_payment`

**Description:** Endpoint for process_payment

---

#### `GET` /api/farmer/analytics/overview

**Function:** `get_farmer_analytics`

**Description:** Get comprehensive farmer analytics overview

---

#### `GET` /api/farmer/analytics/test

**Function:** `test_analytics`

**Description:** Simple test endpoint for analytics

---

#### `POST` /api/farmer/seasonal-planning

**Function:** `create_seasonal_plan`

**Description:** Endpoint for create_seasonal_plan

---

#### `GET` /api/farmer/quality-trends

**Function:** `get_quality_trends`

**Description:** Endpoint for get_quality_trends

---


### Inventory Management

**Base Path:** `/api/inventory`

#### `GET` /api/inventory/paddy

**Function:** `get_paddy`

**Description:** Simple paddy stock endpoint for frontend compatibility

---

#### `POST` /api/inventory/paddy

**Function:** `add_paddy`

**Description:** Add new paddy stock

---

#### `GET` /api/inventory/products

**Function:** `get_products`

**Description:** Simple product stock endpoint for frontend compatibility

---

#### `GET` /api/inventory/movements

**Function:** `get_movements`

**Description:** Get stock movements

---

#### `GET` /api/inventory/paddy-stock

**Function:** `get_paddy_stock`

**Description:** Endpoint for get_paddy_stock

---

#### `POST` /api/inventory/paddy-stock

**Function:** `add_paddy_stock`

**Description:** Endpoint for add_paddy_stock

---

#### `PUT` /api/inventory/paddy-stock/<int:stock_id>

**Function:** `update_paddy_stock`

**Description:** Endpoint for update_paddy_stock

---

#### `GET` /api/inventory/product-stock

**Function:** `get_product_stock`

**Description:** Endpoint for get_product_stock

---

#### `POST` /api/inventory/product-stock

**Function:** `add_product_stock`

**Description:** Endpoint for add_product_stock

---

#### `GET` /api/inventory/transactions

**Function:** `get_transactions`

**Description:** Endpoint for get_transactions

---

#### `POST` /api/inventory/transactions

**Function:** `create_transaction`

**Description:** Endpoint for create_transaction

---

#### `GET` /api/inventory/analytics/overview

**Function:** `get_inventory_overview`

**Description:** Endpoint for get_inventory_overview

---

#### `GET` /api/inventory/analytics/turnover

**Function:** `get_inventory_turnover`

**Description:** Endpoint for get_inventory_turnover

---

#### `GET` /api/inventory/analytics/valuation

**Function:** `get_inventory_valuation`

**Description:** Endpoint for get_inventory_valuation

---

#### `GET` /api/inventory/reorder-rules

**Function:** `get_reorder_rules`

**Description:** Endpoint for get_reorder_rules

---

#### `POST` /api/inventory/reorder-rules

**Function:** `create_reorder_rule`

**Description:** Endpoint for create_reorder_rule

---

#### `GET` /api/inventory/reorder-alerts

**Function:** `get_reorder_alerts`

**Description:** Endpoint for get_reorder_alerts

---

#### `GET` /api/inventory/suppliers

**Function:** `get_suppliers`

**Description:** Endpoint for get_suppliers

---

#### `POST` /api/inventory/suppliers

**Function:** `create_supplier`

**Description:** Endpoint for create_supplier

---

#### `POST` /api/inventory/ai/demand-forecast

**Function:** `get_ai_demand_forecast`

**Description:** Endpoint for get_ai_demand_forecast

---

#### `POST` /api/inventory/ai/optimize-stock-levels

**Function:** `optimize_stock_levels`

**Description:** Endpoint for optimize_stock_levels

---

#### `POST` /api/inventory/ai/price-recommendations

**Function:** `get_price_recommendations`

**Description:** Endpoint for get_price_recommendations

---

#### `GET` /api/inventory/reports/stock-aging

**Function:** `get_stock_aging_report`

**Description:** Endpoint for get_stock_aging_report

---

#### `GET` /api/inventory/reports/movement-summary

**Function:** `get_movement_summary`

**Description:** Endpoint for get_movement_summary

---

#### `GET` /api/inventory/reports/low-stock

**Function:** `get_low_stock_report`

**Description:** Endpoint for get_low_stock_report

---

#### `GET` /api/inventory/waste-tracking

**Function:** `get_waste_tracking`

**Description:** Endpoint for get_waste_tracking

---

#### `POST` /api/inventory/optimization

**Function:** `optimize_inventory`

**Description:** Endpoint for optimize_inventory

---

#### `GET` /api/inventory/aging-analysis

**Function:** `get_aging_analysis`

**Description:** Endpoint for get_aging_analysis

---

#### `GET` /api/inventory/turnover-analysis

**Function:** `get_turnover_analysis`

**Description:** Endpoint for get_turnover_analysis

---

#### `GET` /api/inventory/quality-tracking

**Function:** `get_quality_tracking`

**Description:** Endpoint for get_quality_tracking

---

#### `GET` /api/inventory/storage-optimization

**Function:** `get_storage_optimization`

**Description:** Endpoint for get_storage_optimization

---

#### `GET` /api/inventory/predictive-maintenance

**Function:** `get_predictive_maintenance`

**Description:** Endpoint for get_predictive_maintenance

---

#### `GET` /api/inventory/cost-analysis

**Function:** `get_cost_analysis`

**Description:** Endpoint for get_cost_analysis

---

#### `GET` /api/inventory/dashboard

**Function:** `get_inventory_dashboard`

**Description:** Endpoint for get_inventory_dashboard

---

#### `GET` /api/inventory/alerts

**Function:** `get_stock_alerts`

**Description:** Endpoint for get_stock_alerts

---

#### `GET` /api/inventory/reorder-points

**Function:** `get_reorder_points`

**Description:** Endpoint for get_reorder_points

---

#### `POST` /api/inventory/reorder-points

**Function:** `update_reorder_points`

**Description:** Endpoint for update_reorder_points

---

#### `GET` /api/inventory/demand-forecast

**Function:** `get_demand_forecast`

**Description:** Endpoint for get_demand_forecast

---

#### `POST` /api/inventory/cycle-count

**Function:** `initiate_cycle_count`

**Description:** Endpoint for initiate_cycle_count

---

#### `GET` /api/inventory/supplier-performance

**Function:** `get_supplier_performance`

**Description:** Endpoint for get_supplier_performance

---

#### `GET` /api/inventory/quality-trends

**Function:** `get_quality_trends`

**Description:** Endpoint for get_quality_trends

---

#### `GET` /api/inventory/smart-alerts

**Function:** `get_smart_alerts`

**Description:** Endpoint for get_smart_alerts

---

#### `GET` /api/inventory/batch-tracking

**Function:** `get_batch_tracking`

**Description:** Endpoint for get_batch_tracking

---


### Production Management

**Base Path:** `/api/production`

#### `GET` /api/production/batches

**Function:** `get_batches`

**Description:** Endpoint for get_batches

---

#### `POST` /api/production/batches

**Function:** `create_batch`

**Description:** Endpoint for create_batch

---

#### `GET` /api/production/batches/<int:batch_id>

**Function:** `get_batch_details`

**Description:** Endpoint for get_batch_details

---

#### `POST` /api/production/batches/<int:batch_id>/start

**Function:** `start_batch`

**Description:** Endpoint for start_batch

---

#### `POST` /api/production/batches/<int:batch_id>/complete

**Function:** `complete_batch`

**Description:** Endpoint for complete_batch

---

#### `POST` /api/production/batches/<int:batch_id>/steps

**Function:** `add_production_step`

**Description:** Endpoint for add_production_step

---

#### `POST` /api/production/quality-tests

**Function:** `create_quality_test`

**Description:** Endpoint for create_quality_test

---

#### `GET` /api/production/quality-tests

**Function:** `get_quality_tests`

**Description:** Endpoint for get_quality_tests

---

#### `GET` /api/production/current-status

**Function:** `get_current_status`

**Description:** Endpoint for get_current_status

---

#### `GET` /api/production/schedules

**Function:** `get_production_schedules`

**Description:** Endpoint for get_production_schedules

---

#### `POST` /api/production/schedules

**Function:** `create_production_schedule`

**Description:** Endpoint for create_production_schedule

---

#### `POST` /api/production/optimize

**Function:** `optimize_production`

**Description:** Endpoint for optimize_production

---

#### `GET` /api/production/analytics

**Function:** `get_production_analytics`

**Description:** Endpoint for get_production_analytics

---

#### `GET` /api/production/recommendations

**Function:** `get_ai_recommendations`

**Description:** Endpoint for get_ai_recommendations

---

#### `GET` /api/production/maintenance

**Function:** `get_maintenance_logs`

**Description:** Endpoint for get_maintenance_logs

---

#### `POST` /api/production/maintenance

**Function:** `log_maintenance`

**Description:** Endpoint for log_maintenance

---

#### `GET` /api/production/maintenance/predictions

**Function:** `get_maintenance_predictions`

**Description:** Endpoint for get_maintenance_predictions

---

#### `GET` /api/production/efficiency/analysis

**Function:** `get_efficiency_analysis`

**Description:** Endpoint for get_efficiency_analysis

---

#### `POST` /api/production/batches/<int:batch_id>/pause

**Function:** `pause_batch`

**Description:** Endpoint for pause_batch

---

#### `POST` /api/production/batches/<int:batch_id>/resume

**Function:** `resume_batch`

**Description:** Endpoint for resume_batch

---

#### `GET` /api/production/dashboard

**Function:** `get_production_dashboard`

**Description:** Endpoint for get_production_dashboard

---


### Sales Management

**Base Path:** `/api/sales`

#### `GET` /api/sales/analytics

**Function:** `get_sales_analytics`

**Description:** General sales analytics endpoint for frontend compatibility

---

#### `GET` /api/sales/dashboard

**Function:** `get_sales_dashboard`

**Description:** Endpoint for get_sales_dashboard

---

#### `GET` /api/sales/customers

**Function:** `get_customers`

**Description:** Endpoint for get_customers

---

#### `POST` /api/sales/customers

**Function:** `create_customer`

**Description:** Endpoint for create_customer

---

#### `GET` /api/sales/customers/<int:customer_id>

**Function:** `get_customer_details`

**Description:** Endpoint for get_customer_details

---

#### `GET` /api/sales/orders

**Function:** `get_sales_orders`

**Description:** Endpoint for get_sales_orders

---

#### `POST` /api/sales/orders

**Function:** `create_sales_order`

**Description:** Endpoint for create_sales_order

---

#### `PUT` /api/sales/orders/<int:order_id>/status

**Function:** `update_order_status`

**Description:** Endpoint for update_order_status

---

#### `GET` /api/sales/quotations

**Function:** `get_quotations`

**Description:** Endpoint for get_quotations

---

#### `POST` /api/sales/quotations

**Function:** `create_quotation`

**Description:** Endpoint for create_quotation

---

#### `POST` /api/sales/quotations/<int:quotation_id>/convert

**Function:** `convert_quotation_to_order`

**Description:** Endpoint for convert_quotation_to_order

---

#### `GET` /api/sales/leads

**Function:** `get_sales_leads`

**Description:** Endpoint for get_sales_leads

---

#### `POST` /api/sales/leads

**Function:** `create_sales_lead`

**Description:** Endpoint for create_sales_lead

---

#### `PUT` /api/sales/leads/<int:lead_id>/status

**Function:** `update_lead_status`

**Description:** Endpoint for update_lead_status

---

#### `GET` /api/sales/analytics/revenue

**Function:** `get_revenue_analytics`

**Description:** Endpoint for get_revenue_analytics

---

#### `GET` /api/sales/analytics/forecast

**Function:** `get_sales_forecast`

**Description:** Endpoint for get_sales_forecast

---

#### `POST` /api/sales/lead-scoring

**Function:** `score_sales_lead`

**Description:** Endpoint for score_sales_lead

---


### Finance Management

**Base Path:** `/api/finance`

#### `GET` /api/finance/invoices

**Function:** `get_invoices`

**Description:** Get invoices list for frontend compatibility

---

#### `GET` /api/finance/cash-flow

**Function:** `get_cash_flow`

**Description:** Get cash flow data for frontend compatibility

---

#### `GET` /api/finance/accounts-receivable

**Function:** `get_accounts_receivable`

**Description:** Get accounts receivable for frontend compatibility

---

#### `GET` /api/finance/financial-summary

**Function:** `get_financial_summary`

**Description:** Get financial summary for frontend compatibility

---

#### `POST` /api/finance/accounts

**Function:** `create_account`

**Description:** Endpoint for create_account

---

#### `POST` /api/finance/journal-entries

**Function:** `create_journal_entry`

**Description:** Endpoint for create_journal_entry

---

#### `POST` /api/finance/invoices

**Function:** `create_invoice`

**Description:** Endpoint for create_invoice

---

#### `POST` /api/finance/payments

**Function:** `record_payment`

**Description:** Endpoint for record_payment

---

#### `GET` /api/finance/summary

**Function:** `get_summary`

**Description:** Endpoint for get_summary

---

#### `GET` /api/finance/aging-report

**Function:** `get_aging_report`

**Description:** Endpoint for get_aging_report

---


### Customer Management

**Base Path:** `/api/customers`

#### `GET` /api/customers/analytics/overview

**Function:** `get_analytics_overview`

**Description:** Customer analytics overview for frontend compatibility

---

#### `GET` /api/customers/analytics/segments

**Function:** `get_analytics_segments`

**Description:** Customer segments for frontend compatibility

---

#### `GET` /api/customers/

**Function:** `get_customers`

**Description:** Endpoint for get_customers

---

#### `POST` /api/customers/

**Function:** `create_customer`

**Description:** Endpoint for create_customer

---

#### `GET` /api/customers/<int:customer_id>

**Function:** `get_customer`

**Description:** Endpoint for get_customer

---

#### `PUT` /api/customers/<int:customer_id>

**Function:** `update_customer`

**Description:** Endpoint for update_customer

---

#### `GET` /api/customers/<int:customer_id>/interactions

**Function:** `get_customer_interactions`

**Description:** Endpoint for get_customer_interactions

---

#### `POST` /api/customers/<int:customer_id>/interactions

**Function:** `create_customer_interaction`

**Description:** Endpoint for create_customer_interaction

---

#### `GET` /api/customers/segments

**Function:** `get_customer_segments`

**Description:** Endpoint for get_customer_segments

---

#### `POST` /api/customers/segments

**Function:** `create_customer_segment`

**Description:** Endpoint for create_customer_segment

---

#### `GET` /api/customers/<int:customer_id>/contracts

**Function:** `get_customer_contracts`

**Description:** Endpoint for get_customer_contracts

---

#### `POST` /api/customers/<int:customer_id>/contracts

**Function:** `create_customer_contract`

**Description:** Endpoint for create_customer_contract

---

#### `GET` /api/customers/analytics/satisfaction

**Function:** `get_satisfaction_analytics`

**Description:** Endpoint for get_satisfaction_analytics

---

#### `GET` /api/customers/analytics/lifetime-value

**Function:** `get_lifetime_value_analytics`

**Description:** Endpoint for get_lifetime_value_analytics

---

#### `GET` /api/customers/analytics/churn-prediction

**Function:** `get_churn_prediction`

**Description:** Endpoint for get_churn_prediction

---

#### `GET` /api/customers/communication/campaigns

**Function:** `get_communication_campaigns`

**Description:** Endpoint for get_communication_campaigns

---

#### `POST` /api/customers/communication/campaigns

**Function:** `create_communication_campaign`

**Description:** Endpoint for create_communication_campaign

---

#### `GET` /api/customers/feedback/surveys

**Function:** `get_customer_surveys`

**Description:** Endpoint for get_customer_surveys

---

#### `POST` /api/customers/feedback/surveys

**Function:** `create_customer_survey`

**Description:** Endpoint for create_customer_survey

---

#### `GET` /api/customers/loyalty/programs

**Function:** `get_loyalty_programs`

**Description:** Endpoint for get_loyalty_programs

---

#### `POST` /api/customers/loyalty/programs

**Function:** `create_loyalty_program`

**Description:** Endpoint for create_loyalty_program

---

#### `GET` /api/customers/<int:customer_id>/recommendations

**Function:** `get_customer_recommendations`

**Description:** Endpoint for get_customer_recommendations

---

#### `GET` /api/customers/analytics/journey-mapping

**Function:** `get_customer_journey_mapping`

**Description:** Endpoint for get_customer_journey_mapping

---

#### `GET` /api/customers/support/tickets

**Function:** `get_support_tickets`

**Description:** Endpoint for get_support_tickets

---

#### `POST` /api/customers/support/tickets

**Function:** `create_support_ticket`

**Description:** Endpoint for create_support_ticket

---

#### `GET` /api/customers/analytics/voice-of-customer

**Function:** `get_voice_of_customer`

**Description:** Endpoint for get_voice_of_customer

---

#### `GET` /api/customers/predictive/behavior

**Function:** `get_predictive_behavior`

**Description:** Endpoint for get_predictive_behavior

---

#### `POST` /api/customers/<int:customer_id>/feedback

**Function:** `analyze_feedback`

**Description:** Endpoint for analyze_feedback

---

#### `GET` /api/customers/ai-recommendations

**Function:** `get_ai_recommendations`

**Description:** Endpoint for get_ai_recommendations

---


### Quality Control

**Base Path:** `/api/quality`

#### `GET` /api/quality/standards

**Function:** `get_quality_standards`

**Description:** Get all quality standards

---

#### `POST` /api/quality/standards

**Function:** `create_quality_standard`

**Description:** Create new quality standard

---

#### `GET` /api/quality/templates

**Function:** `get_test_templates`

**Description:** Get all test templates

---

#### `POST` /api/quality/templates

**Function:** `create_test_template`

**Description:** Create new test template

---

#### `GET` /api/quality/inspections

**Function:** `get_inspections`

**Description:** Get quality inspections with filters

---

#### `POST` /api/quality/inspections

**Function:** `create_inspection`

**Description:** Create new quality inspection

---

#### `GET` /api/quality/inspections/<int:inspection_id>

**Function:** `get_inspection`

**Description:** Get specific inspection details

---

#### `POST` /api/quality/inspections/<int:inspection_id>/approve

**Function:** `approve_inspection`

**Description:** Approve quality inspection

---

#### `GET` /api/quality/alerts

**Function:** `get_quality_alerts`

**Description:** Get quality alerts

---

#### `POST` /api/quality/alerts/<int:alert_id>/resolve

**Function:** `resolve_quality_alert`

**Description:** Resolve quality alert

---

#### `GET` /api/quality/trends

**Function:** `get_quality_trends`

**Description:** Get quality trends analysis

---

#### `GET` /api/quality/dashboard

**Function:** `get_quality_dashboard`

**Description:** Get quality dashboard data

---

#### `GET` /api/quality/equipment-health

**Function:** `check_equipment_health`

**Description:** Check equipment health based on quality patterns

---

#### `POST` /api/quality/batch-analysis

**Function:** `analyze_batch_quality`

**Description:** Analyze quality for a specific batch

---

#### `GET` /api/quality/compliance-report

**Function:** `generate_compliance_report`

**Description:** Generate compliance report

---

#### `POST` /api/quality/predict-quality

**Function:** `predict_quality`

**Description:** Predict quality based on input parameters

---

#### `GET` /api/quality/recommendations

**Function:** `get_quality_recommendations`

**Description:** Get AI-powered quality recommendations

---


### Analytics

**Base Path:** `/api/analytics`

#### `POST` /api/analytics/dashboards

**Function:** `create_dashboard`

**Description:** Endpoint for create_dashboard

---

#### `GET` /api/analytics/dashboards/executive

**Function:** `get_executive_dashboard`

**Description:** Endpoint for get_executive_dashboard

---

#### `GET` /api/analytics/dashboards/operational

**Function:** `get_operational_dashboard`

**Description:** Endpoint for get_operational_dashboard

---

#### `POST` /api/analytics/kpis

**Function:** `create_kpi`

**Description:** Endpoint for create_kpi

---

#### `GET` /api/analytics/kpis/dashboard

**Function:** `get_kpi_dashboard`

**Description:** Endpoint for get_kpi_dashboard

---

#### `GET` /api/analytics/reports/financial

**Function:** `generate_financial_report`

**Description:** Endpoint for generate_financial_report

---

#### `GET` /api/analytics/reports/production

**Function:** `generate_production_report`

**Description:** Endpoint for generate_production_report

---

#### `GET` /api/analytics/trends/revenue

**Function:** `get_revenue_trends`

**Description:** Endpoint for get_revenue_trends

---

#### `GET` /api/analytics/insights/business

**Function:** `get_business_insights`

**Description:** Endpoint for get_business_insights

---

#### `POST` /api/analytics/alerts/data

**Function:** `create_data_alert`

**Description:** Endpoint for create_data_alert

---

#### `GET` /api/analytics/performance/summary

**Function:** `get_performance_summary`

**Description:** Endpoint for get_performance_summary

---


### Compliance

**Base Path:** `/api/compliance`

#### `POST` /api/compliance/assessments

**Function:** `create_assessment`

**Description:** Endpoint for create_assessment

---

#### `PUT` /api/compliance/assessments/<int:assessment_id>/results

**Function:** `update_assessment_results`

**Description:** Endpoint for update_assessment_results

---

#### `POST` /api/compliance/documents

**Function:** `create_document`

**Description:** Endpoint for create_document

---

#### `PUT` /api/compliance/action-items/<int:action_item_id>/progress

**Function:** `update_action_progress`

**Description:** Endpoint for update_action_progress

---

#### `GET` /api/compliance/dashboard

**Function:** `get_compliance_dashboard`

**Description:** Endpoint for get_compliance_dashboard

---

#### `GET` /api/compliance/reports/compliance

**Function:** `generate_compliance_report`

**Description:** Endpoint for generate_compliance_report

---

#### `GET` /api/compliance/alerts/check-expiring

**Function:** `check_expiring_documents`

**Description:** Endpoint for check_expiring_documents

---


### Supply Chain

**Base Path:** `/api/supply-chain`

#### `POST` /api/supply-chain/suppliers

**Function:** `create_supplier`

**Description:** Endpoint for create_supplier

---

#### `POST` /api/supply-chain/purchase-orders

**Function:** `create_purchase_order`

**Description:** Endpoint for create_purchase_order

---

#### `POST` /api/supply-chain/purchase-orders/<int:po_id>/receive

**Function:** `receive_purchase_order`

**Description:** Endpoint for receive_purchase_order

---

#### `POST` /api/supply-chain/procurement-requests

**Function:** `create_procurement_request`

**Description:** Endpoint for create_procurement_request

---

#### `GET` /api/supply-chain/suppliers/<int:supplier_id>/performance

**Function:** `get_supplier_performance`

**Description:** Endpoint for get_supplier_performance

---

#### `POST` /api/supply-chain/optimize-inventory

**Function:** `optimize_inventory`

**Description:** Endpoint for optimize_inventory

---

#### `POST` /api/supply-chain/predict-delivery

**Function:** `predict_delivery`

**Description:** Endpoint for predict_delivery

---


### Logistics

**Base Path:** `/api/logistics`

#### `POST` /api/logistics/shipments

**Function:** `create_shipment`

**Description:** Endpoint for create_shipment

---

#### `POST` /api/logistics/shipments/<int:shipment_id>/assign

**Function:** `assign_shipment`

**Description:** Endpoint for assign_shipment

---

#### `POST` /api/logistics/shipments/<int:shipment_id>/start

**Function:** `start_shipment`

**Description:** Endpoint for start_shipment

---

#### `POST` /api/logistics/shipments/<int:shipment_id>/complete

**Function:** `complete_delivery`

**Description:** Endpoint for complete_delivery

---

#### `GET` /api/logistics/track/<shipment_number>

**Function:** `track_shipment`

**Description:** Endpoint for track_shipment

---

#### `GET` /api/logistics/fleet/status

**Function:** `get_fleet_status`

**Description:** Endpoint for get_fleet_status

---

#### `GET` /api/logistics/vehicles

**Function:** `get_vehicles`

**Description:** Endpoint for get_vehicles

---

#### `GET` /api/logistics/drivers

**Function:** `get_drivers`

**Description:** Endpoint for get_drivers

---


### Notifications

**Base Path:** `/api`

#### `GET` /api/notifications

**Function:** `get_notifications`

**Description:** Get all notifications

---

#### `POST` /api/notifications/<int:notification_id>/read

**Function:** `mark_notification_read`

**Description:** Mark a notification as read

---

#### `POST` /api/notifications/mark-all-read

**Function:** `mark_all_notifications_read`

**Description:** Mark all notifications as read

---

#### `DELETE` /api/notifications/<int:notification_id>

**Function:** `delete_notification`

**Description:** Delete a notification

---

#### `POST` /api/notifications

**Function:** `create_notification`

**Description:** Create a new notification

---

#### `GET` /api/notifications/categories

**Function:** `get_notification_categories`

**Description:** Get notification categories

---

#### `GET` /api/notifications/stats

**Function:** `get_notification_stats`

**Description:** Get notification statistics

---


### AI Services

**Base Path:** `/api/ai`

#### `POST` /api/ai/voice/recognize

**Function:** `recognize_voice`

**Description:** Process voice command

---

#### `POST` /api/ai/quality/assess

**Function:** `assess_quality`

**Description:** Analyze rice quality from image

---

#### `POST` /api/ai/insights/generate

**Function:** `generate_insights`

**Description:** Generate AI insights from data

---

#### `POST` /api/ai/demand/predict

**Function:** `predict_demand`

**Description:** Predict demand using AI

---

#### `POST` /api/ai/production/optimize

**Function:** `optimize_production`

**Description:** Optimize production schedule

---

#### `POST` /api/ai/anomalies/detect

**Function:** `detect_anomalies`

**Description:** Detect anomalies in data

---

#### `GET` /api/ai/capabilities

**Function:** `get_ai_capabilities`

**Description:** Get AI service capabilities

---

#### `GET` /api/ai/models/status

**Function:** `get_model_status`

**Description:** Get AI model status

---

#### `POST` /api/ai/train/model

**Function:** `train_model`

**Description:** Train or retrain AI models

---

#### `POST` /api/ai/feedback

**Function:** `submit_feedback`

**Description:** Submit feedback for AI predictions

---

#### `GET` /api/ai/health

**Function:** `ai_health_check`

**Description:** Health check for AI services

---


### Biometric

**Base Path:** `/api/biometric`

#### `POST` /api/biometric/register/face

**Function:** `register_face`

**Description:** Register user's face for biometric authentication

---

#### `POST` /api/biometric/verify/face

**Function:** `verify_face`

**Description:** Verify user's face for authentication

---

#### `POST` /api/biometric/register/fingerprint

**Function:** `register_fingerprint`

**Description:** Register user's fingerprint

---

#### `POST` /api/biometric/verify/fingerprint

**Function:** `verify_fingerprint`

**Description:** Verify user's fingerprint

---

#### `POST` /api/biometric/login/voice

**Function:** `voice_login`

**Description:** Voice-based login with speech recognition and voice verification

---

#### `POST` /api/biometric/capture/voice

**Function:** `capture_voice`

**Description:** Capture voice sample for registration

---

#### `GET` /api/biometric/status/<int:user_id>

**Function:** `get_biometric_status`

**Description:** Get user's biometric registration status

---

#### `POST` /api/biometric/register/voice

**Function:** `register_voice`

**Description:** Register user's voice biometric

---

#### `POST` /api/biometric/verify/voice

**Function:** `verify_voice`

**Description:** Verify user's voice biometric

---

#### `POST` /api/biometric/ai/process

**Function:** `process_ai_command`

**Description:** Process AI voice commands

---


### Quality Vision

**Base Path:** `/api/quality-vision`

#### `POST` /api/quality-vision/analyze/image

**Function:** `analyze_quality_image`

**Description:** Analyze rice quality from image using AI computer vision

---

#### `GET` /api/quality-vision/dashboard

**Function:** `get_vision_dashboard`

**Description:** Get AI vision quality dashboard data

---

#### `GET` /api/quality-vision/recommendations/<test_id>

**Function:** `get_ai_recommendations`

**Description:** Get AI-generated quality improvement recommendations

---

#### `GET` /api/quality-vision/standards/<variety>

**Function:** `get_variety_standards`

**Description:** Get quality standards for rice variety

---

#### `POST` /api/quality-vision/batch/<batch_id>/analyze

**Function:** `analyze_batch_samples`

**Description:** Analyze multiple samples from a production batch

---

#### `POST` /api/quality-vision/calibrate

**Function:** `calibrate_vision_system`

**Description:** Calibrate the AI vision system with reference samples

---

#### `GET` /api/quality-vision/export/analysis/<test_id>

**Function:** `export_analysis_report`

**Description:** Export detailed AI analysis report

---


### Financial Intelligence

**Base Path:** `/api/financial-intelligence`

#### `POST` /api/financial-intelligence/cash-flow/analyze

**Function:** `analyze_cash_flow`

**Description:** Comprehensive cash flow analysis with AI predictions

---

#### `POST` /api/financial-intelligence/payment/schedule

**Function:** `smart_payment_scheduling`

**Description:** AI-powered optimal payment scheduling

---

#### `GET` /api/financial-intelligence/forecast

**Function:** `financial_forecasting`

**Description:** Advanced financial forecasting using AI

---

#### `GET` /api/financial-intelligence/payment/optimize

**Function:** `payment_optimization`

**Description:** Optimize payment processes using AI

---

#### `GET` /api/financial-intelligence/health-score

**Function:** `financial_health_score`

**Description:** Calculate comprehensive financial health score

---

#### `POST` /api/financial-intelligence/invoice/process

**Function:** `automated_invoice_processing`

**Description:** AI-powered automated invoice processing

---

#### `GET` /api/financial-intelligence/dashboard

**Function:** `financial_dashboard`

**Description:** Get comprehensive financial intelligence dashboard

---

#### `GET` /api/financial-intelligence/insights

**Function:** `financial_insights`

**Description:** Get AI-generated financial insights and recommendations

---

#### `GET` /api/financial-intelligence/reports/cash-flow

**Function:** `cash_flow_report`

**Description:** Generate detailed cash flow report

---

#### `GET` /api/financial-intelligence/reports/financial-health

**Function:** `financial_health_report`

**Description:** Generate detailed financial health report

---

#### `GET` /api/financial-intelligence/alerts

**Function:** `financial_alerts`

**Description:** Get financial alerts and warnings

---


### GST Compliance

**Base Path:** `/api/compliance`

#### `POST` /api/compliance/gst/calculate

**Function:** `calculate_gst`

**Description:** Calculate GST for a transaction

---

#### `POST` /api/compliance/invoice/generate

**Function:** `generate_gst_invoice`

**Description:** Generate GST-compliant invoice

---

#### `GET` /api/compliance/gstr1/<int:month>/<int:year>

**Function:** `generate_gstr1_report`

**Description:** Generate GSTR-1 report

---

#### `GET` /api/compliance/gstr3b/<int:month>/<int:year>

**Function:** `generate_gstr3b_report`

**Description:** Generate GSTR-3B report

---

#### `GET` /api/compliance/compliance/status

**Function:** `check_compliance_status`

**Description:** Check overall compliance status

---

#### `POST` /api/compliance/gstin/validate

**Function:** `validate_gstin`

**Description:** Validate GSTIN format and checksum

---

#### `POST` /api/compliance/pan/validate

**Function:** `validate_pan`

**Description:** Validate PAN format

---

#### `POST` /api/compliance/reports/generate

**Function:** `generate_compliance_report`

**Description:** Generate comprehensive compliance report

---

#### `GET` /api/compliance/dashboard

**Function:** `compliance_dashboard`

**Description:** Get compliance dashboard data

---

#### `GET` /api/compliance/calendar/<int:year>

**Function:** `compliance_calendar`

**Description:** Get compliance calendar with due dates

---

#### `POST` /api/compliance/tds/calculate

**Function:** `calculate_tds`

**Description:** Calculate TDS for payment

---

#### `POST` /api/compliance/tds/certificate

**Function:** `generate_tds_certificate`

**Description:** Generate TDS certificate

---

#### `POST` /api/compliance/export/gst

**Function:** `export_gst_data`

**Description:** Export GST data in various formats

---

#### `POST` /api/compliance/reconcile/gst

**Function:** `reconcile_gst_data`

**Description:** Reconcile GST data between books and returns

---

#### `POST` /api/compliance/tax/summary

**Function:** `tax_summary`

**Description:** Get comprehensive tax summary

---

#### `GET` /api/compliance/reminders

**Function:** `compliance_reminders`

**Description:** Get compliance reminders

---

#### `POST` /api/compliance/check/automated

**Function:** `automated_compliance_check`

**Description:** Run automated compliance checks

---

#### `GET` /api/compliance/invoice/<invoice_id>/gst-details

**Function:** `get_invoice_gst_details`

**Description:** Get GST details for a specific invoice

---

#### `GET` /api/compliance/hsn/codes

**Function:** `get_hsn_codes`

**Description:** Get HSN codes for rice products

---

#### `GET` /api/compliance/gst/rates

**Function:** `get_gst_rates`

**Description:** Get current GST rates for different products

---

#### `GET` /api/compliance/compliance/requirements

**Function:** `get_compliance_requirements`

**Description:** Get compliance requirements for rice mill

---


### Analytics Reporting

**Base Path:** `/api/analytics`

#### `POST` /api/analytics/reports/generate

**Function:** `generate_natural_language_report`

**Description:** Generate natural language report with AI insights

---

#### `POST` /api/analytics/predictive/analyze

**Function:** `predictive_analytics`

**Description:** Advanced predictive analytics with machine learning

---

#### `POST` /api/analytics/insights/generate

**Function:** `generate_intelligent_insights`

**Description:** Generate intelligent insights from multiple data sources

---

#### `POST` /api/analytics/dashboard/custom

**Function:** `generate_custom_dashboard`

**Description:** Generate custom dashboard analytics

---

#### `POST` /api/analytics/compare/analyze

**Function:** `comparative_analysis`

**Description:** Perform comparative analysis

---

#### `POST` /api/analytics/anomaly/detect

**Function:** `detect_anomalies`

**Description:** Detect anomalies in data streams

---

#### `POST` /api/analytics/benchmark/analyze

**Function:** `performance_benchmarking`

**Description:** Benchmark performance against standards

---

#### `GET` /api/analytics/realtime/<metric_type>

**Function:** `real_time_analytics`

**Description:** Generate real-time analytics

---

#### `GET` /api/analytics/dashboard/overview

**Function:** `analytics_dashboard_overview`

**Description:** Get comprehensive analytics dashboard overview

---

#### `GET` /api/analytics/reports/templates

**Function:** `get_report_templates`

**Description:** Get available report templates

---

#### `POST` /api/analytics/export/report

**Function:** `export_report`

**Description:** Export report in various formats

---

#### `POST` /api/analytics/kpi/calculate

**Function:** `calculate_kpis`

**Description:** Calculate Key Performance Indicators

---

#### `POST` /api/analytics/trends/analyze

**Function:** `analyze_trends`

**Description:** Analyze trends in various metrics

---

#### `GET` /api/analytics/alerts/smart

**Function:** `get_smart_alerts`

**Description:** Get AI-generated smart alerts

---


## Error Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request |
| 401  | Unauthorized |
| 403  | Forbidden |
| 404  | Not Found |
| 422  | Validation Error |
| 500  | Internal Server Error |

## Rate Limiting

- **Default:** 1000 requests per hour
- **Login attempts:** 5 per minute
- **API calls:** 100 per minute

## Support

For API support, contact: admin@ricemill.com
