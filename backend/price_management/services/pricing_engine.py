from decimal import Decimal
from django.utils import timezone
from django.db.models import Q
from ..models import PriceRule
from products.models import Product

class PricingEngine:
    @staticmethod
    def calculate_price(product, customer=None, quantity=1, date=None):
        """
        Calculate best price for a product based on rules.
        Highest priority rule wins.
        Priority:
        1. Explicit PriceRule (highest priority)
        2. Base Product Price
        """
        if date is None:
            date = timezone.now().date()
        
        quantity = Decimal(str(quantity))
        base_price = product.selling_price
        final_price = base_price
        applied_rule = None
        
        # 1. Fetch active rules for product valid on date
        rules = PriceRule.objects.filter(
            product=product,
            is_active=True,
            valid_from__lte=date
        ).filter(
            Q(valid_to__isnull=True) | Q(valid_to__gte=date)
        )
        
        # 2. Filter by Quantity limits
        rules = rules.filter(
            min_quantity__lte=quantity
        ).filter(
            Q(max_quantity__isnull=True) | Q(max_quantity__gte=quantity)
        )
        
        
        # 3. Filter by Customer / City
        applicable_rules = []
        for rule in rules:
            is_match = True
            
            # Customer check
            if rule.customer:
                if not customer or rule.customer_id != customer.id:
                    is_match = False
            
            # City check
            if rule.city:
                if not customer or not customer.city or rule.city.lower() != customer.city.lower():
                    is_match = False
            
            # Category check (if rule specifies category)
            if rule.customer_category:
                # Since we don't have category in BusinessPartner, we treat this rule as NOT MATCHING if set
                is_match = False

            if is_match:
                applicable_rules.append(rule)

        # 4. Sort by Priority (Highest wins)
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        
        if applicable_rules:
            best_rule = applicable_rules[0]
            
            # Apply Pricing Logic
            # If price is set and > 0, it overrides base price
            if best_rule.price is not None and best_rule.price > 0:
                final_price = best_rule.price
                applied_rule = best_rule
            
            # If discount_percentage > 0, it applies to base price
            # Only apply positive discounts (data integrity check)
            elif best_rule.discount_percentage > 0:
                discount_amount = base_price * (best_rule.discount_percentage / 100)
                final_price = base_price - discount_amount
                applied_rule = best_rule

        return {
            'product_id': product.id,
            'product_name': product.name,
            'original_price': base_price,
            'final_price': final_price,
            'applied_rule': applied_rule.rule_name if applied_rule else None,
            'rule_id': applied_rule.id if applied_rule else None,
            'quantity': quantity,
            'currency': 'PKR' # Simplified
        }

    @staticmethod
    def bulk_update_prices(product_ids, percentage_change):
        """
        Update base selling_price for list of products
        """
        products = Product.objects.filter(id__in=product_ids)
        updated_count = 0
        factor = 1 + (Decimal(str(percentage_change)) / 100)
        
        for product in products:
            product.selling_price = product.selling_price * factor
            product.save()
            updated_count += 1
            
        return updated_count
