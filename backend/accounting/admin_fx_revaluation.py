        ('Audit Trail', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(FXRevaluationLog)
class FXRevaluationLogAdmin(admin.ModelAdmin):
    list_display = ['revaluation_id', 'entity', 'revaluation_date', 'net_fx_gain_loss', 'status', 'voucher', 'created_at']
    list_filter = ['status', 'execution_method', 'auto_posted', 'reversal_created', 'revaluation_date', 'entity']
    search_fields = ['revaluation_id', 'entity__entity_code', 'entity__entity_name', 'voucher__voucher_number']
    ordering = ['-revaluation_date', '-created_at']
    readonly_fields = ['revaluation_id', 'created_at', 'is_successful', 'has_fx_impact']
    
    fieldsets = (
        ('Revaluation Information', {
            'fields': ('revaluation_id', 'entity', 'revaluation_date', 'functional_currency')
        }),
        ('Results', {
            'fields': ('accounts_revalued', 'total_gain', 'total_loss', 'net_fx_gain_loss', 'is_successful', 'has_fx_impact')
        }),
        ('Vouchers', {
            'fields': ('voucher', 'reversal_voucher')
        }),
        ('Execution Details', {
            'fields': ('status', 'execution_method', 'auto_posted', 'reversal_created')
        }),
        ('Detailed Results', {
            'fields': ('revaluation_details',),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Audit Trail', {
            'fields': ('created_by', 'created_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
