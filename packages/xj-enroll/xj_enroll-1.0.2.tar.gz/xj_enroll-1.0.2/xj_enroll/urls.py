from django.conf.urls import url
from .apis import EnrollRecordListView


urlpatterns = [
    url(r'^list/?$', EnrollRecordListView.as_view(), name='list'),
]
