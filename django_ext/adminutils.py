import csv


# Python 3 version works natively with unicode!!!
def download_csv(modeladmin, request, queryset, filename='export.csv'):
    from django.http import HttpResponse
    from django.core.exceptions import PermissionDenied

    if not request.user.is_staff:
        raise PermissionDenied
    opts = queryset.model._meta
    response = HttpResponse(content_type='text/csv')
    # force download.
    response['Content-Disposition'] = 'attachment;filename=%s' % filename
    # the csv writer
    writer = csv.writer(response, dialect=csv.excel)
    field_names = [field.name for field in opts.fields]
    # Write a first row with header information
    writer.writerow(field_names)
    # Write data rows
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response
download_csv.short_description = "Download selected as csv"
