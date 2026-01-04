from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import PriceRule
from .serializers import PriceRuleSerializer, PriceCalculationSerializer
from .services.pricing_engine import PricingEngine
from .services.report_service import PriceReportService
from products.models import Product
from partners.models import BusinessPartner

class PriceRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Price Rules
    """
    queryset = PriceRule.objects.all()
    serializer_class = PriceRuleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'customer', 'is_active', 'city']
    search_fields = ['rule_name', 'product__name', 'product__code', 'customer__name']
    ordering_fields = ['priority', 'valid_from', 'price']
    ordering = ['-priority']

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Simulate price calculation"""
        serializer = PriceCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        try:
            product = Product.objects.get(id=data['product_id'])
            customer = None
            if data.get('customer_id'):
                customer = BusinessPartner.objects.get(id=data['customer_id'])
            
            result = PricingEngine.calculate_price(
                product=product,
                customer=customer,
                quantity=data.get('quantity', 1),
                date=data.get('date')
            )
            return Response(result)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        except BusinessPartner.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        """Import rules from Excel/CSV file"""
        import pandas as pd
        from datetime import datetime
        
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        file_ext = file.name.split('.')[-1].lower()
        
        if file_ext not in ['csv', 'xlsx', 'xls']:
            return Response({'error': 'Invalid file format. Please upload CSV or Excel file.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Read file based on extension
            if file_ext == 'csv':
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Validate required columns
            required_columns = ['product_code', 'rule_name', 'priority', 'valid_from', 'price']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({
                    'error': f'Missing required columns: {", ".join(missing_columns)}',
                    'required_columns': required_columns,
                    'optional_columns': ['customer_code', 'customer_category', 'city', 'valid_to', 
                                       'min_quantity', 'max_quantity', 'discount_percentage', 'is_active']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process rows
            created_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Get product
                    product = Product.objects.get(code=row['product_code'])
                    
                    # Get customer if specified
                    customer = None
                    if 'customer_code' in row and pd.notna(row['customer_code']):
                        try:
                            customer = BusinessPartner.objects.get(code=row['customer_code'])
                        except BusinessPartner.DoesNotExist:
                            errors.append(f"Row {index + 2}: Customer '{row['customer_code']}' not found")
                            continue
                    
                    # Parse dates
                    valid_from = pd.to_datetime(row['valid_from']).date()
                    valid_to = None
                    if 'valid_to' in row and pd.notna(row['valid_to']):
                        valid_to = pd.to_datetime(row['valid_to']).date()
                    
                    # Create price rule
                    PriceRule.objects.create(
                        product=product,
                        rule_name=row['rule_name'],
                        priority=int(row.get('priority', 10)),
                        valid_from=valid_from,
                        valid_to=valid_to,
                        customer=customer,
                        customer_category=row.get('customer_category') if pd.notna(row.get('customer_category')) else None,
                        city=row.get('city') if pd.notna(row.get('city')) else None,
                        min_quantity=float(row.get('min_quantity', 0)),
                        max_quantity=float(row.get('max_quantity')) if pd.notna(row.get('max_quantity')) else None,
                        price=float(row['price']) if pd.notna(row.get('price')) else None,
                        discount_percentage=float(row.get('discount_percentage', 0)),
                        is_active=bool(row.get('is_active', True))
                    )
                    created_count += 1
                    
                except Product.DoesNotExist:
                    errors.append(f"Row {index + 2}: Product '{row['product_code']}' not found")
                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")
            
            return Response({
                'success': True,
                'created_count': created_count,
                'total_rows': len(df),
                'errors': errors if errors else None
            }, status=status.HTTP_201_CREATED if created_count > 0 else status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': f'File processing error: {str(e)}'}, 
                          status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def export_template(self, request):
        """Download Excel template for bulk import"""
        import pandas as pd
        from django.http import HttpResponse
        import io
        
        # Create template DataFrame
        template_data = {
            'product_code': ['PROD001', 'PROD002'],
            'rule_name': ['Example Rule 1', 'Example Rule 2'],
            'priority': [10, 20],
            'valid_from': ['2025-01-01', '2025-01-01'],
            'valid_to': ['2025-12-31', ''],
            'customer_code': ['', 'CUST001'],
            'customer_category': ['', 'VIP'],
            'city': ['', 'Lahore'],
            'min_quantity': [0, 10],
            'max_quantity': ['', 100],
            'price': [95.00, 85.00],
            'discount_percentage': [0, 0],
            'is_active': [True, True]
        }
        
        df = pd.DataFrame(template_data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Price Rules')
        
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=price_rules_template.xlsx'
        return response

    # ===== REPORT ENDPOINTS =====
    
    @action(detail=False, methods=['get'])
    def report_by_product(self, request):
        """Price List Report by Product"""
        product_id = request.query_params.get('product_id')
        date = request.query_params.get('date')
        active_only = request.query_params.get('active_only', 'true').lower() == 'true'
        
        report_data = PriceReportService.price_list_by_product(
            product_id=product_id,
            date=date,
            active_only=active_only
        )
        
        return Response({
            'report_type': 'price_list_by_product',
            'generated_at': timezone.now(),
            'filters': {
                'product_id': product_id,
                'date': date,
                'active_only': active_only
            },
            'data': report_data,
            'count': len(report_data)
        })

    @action(detail=False, methods=['get'])
    def report_by_customer(self, request):
        """Price List Report by Customer"""
        customer_id = request.query_params.get('customer_id')
        date = request.query_params.get('date')
        active_only = request.query_params.get('active_only', 'true').lower() == 'true'
        
        report_data = PriceReportService.price_list_by_customer(
            customer_id=customer_id,
            date=date,
            active_only=active_only
        )
        
        return Response({
            'report_type': 'price_list_by_customer',
            'generated_at': timezone.now(),
            'filters': {
                'customer_id': customer_id,
                'date': date,
                'active_only': active_only
            },
            'data': report_data,
            'count': len(report_data)
        })

    @action(detail=False, methods=['get'])
    def report_price_history(self, request):
        """Price History Report"""
        product_id = request.query_params.get('product_id')
        customer_id = request.query_params.get('customer_id')
        days = int(request.query_params.get('days', 90))
        
        report_data = PriceReportService.price_history_report(
            product_id=product_id,
            customer_id=customer_id,
            days=days
        )
        
        return Response({
            'report_type': 'price_history',
            'generated_at': timezone.now(),
            'filters': {
                'product_id': product_id,
                'customer_id': customer_id,
                'days': days
            },
            'data': report_data,
            'count': len(report_data)
        })

    @action(detail=False, methods=['get'])
    def report_price_variance(self, request):
        """Price Variance Report"""
        date = request.query_params.get('date')
        
        report_data = PriceReportService.price_variance_report(date=date)
        
        # Calculate summary statistics
        if report_data:
            total_rules = len(report_data)
            avg_variance = sum(r['variance_percentage'] for r in report_data) / total_rules
            max_discount = min(r['variance_percentage'] for r in report_data)
            max_premium = max(r['variance_percentage'] for r in report_data)
        else:
            total_rules = avg_variance = max_discount = max_premium = 0
        
        return Response({
            'report_type': 'price_variance',
            'generated_at': timezone.now(),
            'filters': {
                'date': date
            },
            'summary': {
                'total_rules': total_rules,
                'average_variance_pct': round(avg_variance, 2),
                'max_discount_pct': round(max_discount, 2),
                'max_premium_pct': round(max_premium, 2)
            },
            'data': report_data,
            'count': len(report_data)
        })
