from django.contrib import admin

# Register your models here.
from .models import RecycleBin


class RecycleBinManager(admin.ModelAdmin):
    fields = (
        'id', 'user_id', 'user_name', 'summary', 'from_table', 'primary_key', 'target_id', 'target_data', 'keys_map',
        'relationship_no')
    list_display = ('from_table', 'primary_key', 'target_id')
    search_fields = ('from_table', 'primary_key', 'target_id')


admin.site.register(RecycleBin, RecycleBinManager)
admin.site.site_header = 'msa一体化管理后台'
admin.site.site_title = 'msa一体化管理后台'