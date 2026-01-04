
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
