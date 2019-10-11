from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Min, Max
from django.db.models.functions import Trunc
from django.db.models import DateTimeField

from .models import EventParam, LogEvent, Client


class MyAdminSite(admin.AdminSite):

    index_template = "admin/custom_index.html"

    def index(self, request, extra_context=None):
        if extra_context == None:
            extra_context = {}


        extra_context["sessions_summary"] = LogEvent.sessions()
        return super().index(request, extra_context)

my_admin = MyAdminSite()
# my_admin = admin.site

class EventAdminBasic(admin.ModelAdmin):
    pass

class ClientAdminBasic(admin.ModelAdmin):
    pass

# Register your models here.

class ParamsInline(admin.TabularInline):
    model = EventParam


class ParamNameFilter(SimpleListFilter):
    title = "Parameter filter"
    parameter_name = "param_name"

    def lookups(self, request, model_admin):
        params = [p for p in EventParam.objects.values('param_name').distinct()]
        return [(p["param_name"], p["param_name"]) for p in params]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(params__param_name=self.value())


class EventAdmin(admin.ModelAdmin):

    def get_params(self, obj):
        return ", ".join(["{}: {}".format(p.param_name, p.param_value) for p in obj.params.all()])

    inlines = [
        ParamsInline,
    ]

    ordering = ['-event_time']

    readonly_fields = ('client',)
    search_fields = ['client__client_hash', 'event_name', 'params__param_name', 'params__param_value',
                     'client__client_platform']

    list_filter = [
        'event_time',
        'event_name',
        'client__client_platform',
        'client__client_version',
        'client__client_hash',
        ParamNameFilter,
    ]

    list_display = [
        'event_name',
        'event_time',
        'client',
        'get_params',
    ]

    change_list_template = "admin/events_summary_change_list.html"

    def changelist_view(self, request, extra_context=None):

        response = super().changelist_view(request, extra_context=extra_context)

        try:

            qs = response.context_data['cl'].queryset

            summary = qs \
                .annotate(period=Trunc('event_time', 'day', output_field=DateTimeField())) \
                .values('period') \
                .annotate(total=Count('id')) \
                .order_by('period')
            summary_range = summary.aggregate(low=Min('total'), high=Max('total'))
            high = summary_range.get('high', 0)
            low = summary_range.get('low', 0)
            total = qs.count()

            response.context_data["summary_over_time"] = [{
                'period': x['period'],
                'total': x['total'] or 0,
                'pct': \
                    ((x['total'] or 0) / total * 100 if high >= low else 0),
            } for x in summary]
        except (AttributeError, KeyError):
            pass

        return response


class ClientAdmin(admin.ModelAdmin):
    list_filter = [
        'client_platform',
        'client_version',
    ]
    list_display = [
        "client_hash",
        "client_platform",
        "client_version",
    ]


my_admin.register(Client, ClientAdmin)
my_admin.register(LogEvent, EventAdmin)

#my_admin.register(Client, ClientAdminBasic)
#my_admin.register(LogEvent, EventAdminBasic)