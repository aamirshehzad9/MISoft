"""
Price Reports Service
Provides reporting functionality for pricing data
"""
from decimal import Decimal
from django.db.models import Q, Min, Max, Avg, Count
from django.utils import timezone
from datetime import timedelta
from ..models import PriceRule
from products.models import Product
from partners.models import BusinessPartner


class PriceReportService:
    """Service for generating pricing reports"""
    
    @staticmethod
    def price_list_by_product(product_id=None, date=None, active_only=True):
        """
        Generate price list report grouped by product
        Shows all applicable pricing rules for products
        """
        if date is None:
            date = timezone.now().date()
        
        # Base queryset
        rules = PriceRule.objects.select_related('product', 'customer')
        
        # Filter by product if specified
        if product_id:
            rules = rules.filter(product_id=product_id)
        
        # Filter by active status
        if active_only:
            rules = rules.filter(is_active=True)
        
        # Filter by date validity
        rules = rules.filter(
            valid_from__lte=date
        ).filter(
            Q(valid_to__isnull=True) | Q(valid_to__gte=date)
        )
        
        # Order by product, then priority
        rules = rules.order_by('product__code', '-priority')
        
        # Format results
        report_data = []
        for rule in rules:
            report_data.append({
                'product_code': rule.product.code,
                'product_name': rule.product.name,
                'rule_name': rule.rule_name,
                'priority': rule.priority,
                'customer': rule.customer.name if rule.customer else 'All Customers',
                'city': rule.city or 'All Cities',
                'min_quantity': rule.min_quantity,
                'max_quantity': rule.max_quantity,
                'price': rule.price,
                'discount_percentage': rule.discount_percentage,
                'valid_from': rule.valid_from,
                'valid_to': rule.valid_to,
                'base_price': rule.product.selling_price
            })
        
        return report_data
    
    @staticmethod
    def price_list_by_customer(customer_id=None, date=None, active_only=True):
        """
        Generate price list report grouped by customer
        Shows customer-specific pricing rules
        """
        if date is None:
            date = timezone.now().date()
        
        # Base queryset
        rules = PriceRule.objects.select_related('product', 'customer')
        
        # Filter by customer if specified
        if customer_id:
            rules = rules.filter(
                Q(customer_id=customer_id) | Q(customer__isnull=True)
            )
        
        # Filter by active status
        if active_only:
            rules = rules.filter(is_active=True)
        
        # Filter by date validity
        rules = rules.filter(
            valid_from__lte=date
        ).filter(
            Q(valid_to__isnull=True) | Q(valid_to__gte=date)
        )
        
        # Order by customer, then product
        rules = rules.order_by('customer__name', 'product__code', '-priority')
        
        # Format results
        report_data = []
        for rule in rules:
            report_data.append({
                'customer_name': rule.customer.name if rule.customer else 'General Pricing',
                'product_code': rule.product.code,
                'product_name': rule.product.name,
                'rule_name': rule.rule_name,
                'priority': rule.priority,
                'city': rule.city or 'All Cities',
                'min_quantity': rule.min_quantity,
                'max_quantity': rule.max_quantity,
                'price': rule.price,
                'discount_percentage': rule.discount_percentage,
                'valid_from': rule.valid_from,
                'valid_to': rule.valid_to,
                'base_price': rule.product.selling_price
            })
        
        return report_data
    
    @staticmethod
    def price_history_report(product_id=None, customer_id=None, days=90):
        """
        Generate price history report
        Shows how prices have changed over time
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Base queryset
        rules = PriceRule.objects.select_related('product', 'customer')
        
        # Filter by product
        if product_id:
            rules = rules.filter(product_id=product_id)
        
        # Filter by customer
        if customer_id:
            rules = rules.filter(
                Q(customer_id=customer_id) | Q(customer__isnull=True)
            )
        
        # Filter by date range (rules that were valid during this period)
        rules = rules.filter(
            Q(valid_from__lte=end_date) &
            (Q(valid_to__isnull=True) | Q(valid_to__gte=start_date))
        )
        
        # Order by product, valid_from
        rules = rules.order_by('product__code', '-valid_from', '-priority')
        
        # Format results
        report_data = []
        for rule in rules:
            # Calculate effective period
            effective_from = max(rule.valid_from, start_date)
            effective_to = min(rule.valid_to or end_date, end_date)
            
            report_data.append({
                'product_code': rule.product.code,
                'product_name': rule.product.name,
                'customer': rule.customer.name if rule.customer else 'All Customers',
                'rule_name': rule.rule_name,
                'priority': rule.priority,
                'price': rule.price,
                'discount_percentage': rule.discount_percentage,
                'valid_from': rule.valid_from,
                'valid_to': rule.valid_to,
                'effective_from': effective_from,
                'effective_to': effective_to,
                'days_active': (effective_to - effective_from).days + 1,
                'base_price': rule.product.selling_price,
                'is_active': rule.is_active
            })
        
        return report_data
    
    @staticmethod
    def price_variance_report(date=None):
        """
        Generate price variance report
        Shows variance between base price and rule prices
        """
        if date is None:
            date = timezone.now().date()
        
        # Get active rules
        rules = PriceRule.objects.select_related('product', 'customer').filter(
            is_active=True,
            valid_from__lte=date
        ).filter(
            Q(valid_to__isnull=True) | Q(valid_to__gte=date)
        )
        
        # Format results with variance calculations
        report_data = []
        for rule in rules:
            base_price = rule.product.selling_price
            
            # Calculate effective price
            if rule.price and rule.price > 0:
                effective_price = rule.price
            elif rule.discount_percentage > 0:
                effective_price = base_price * (1 - rule.discount_percentage / 100)
            else:
                effective_price = base_price
            
            # Calculate variance
            variance_amount = effective_price - base_price
            variance_percentage = (variance_amount / base_price * 100) if base_price > 0 else 0
            
            report_data.append({
                'product_code': rule.product.code,
                'product_name': rule.product.name,
                'rule_name': rule.rule_name,
                'customer': rule.customer.name if rule.customer else 'All Customers',
                'city': rule.city or 'All Cities',
                'priority': rule.priority,
                'base_price': base_price,
                'effective_price': effective_price,
                'variance_amount': variance_amount,
                'variance_percentage': round(variance_percentage, 2),
                'min_quantity': rule.min_quantity,
                'max_quantity': rule.max_quantity,
                'valid_from': rule.valid_from,
                'valid_to': rule.valid_to
            })
        
        # Sort by variance percentage (highest discount first)
        report_data.sort(key=lambda x: x['variance_percentage'])
        
        return report_data
