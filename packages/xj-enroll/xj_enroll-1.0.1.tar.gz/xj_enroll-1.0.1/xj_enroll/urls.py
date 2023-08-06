from django.conf.urls import url
from apps.enroll.apis import EnrollRecordListView


urlpatterns = [
    url(r'^list/?$', EnrollRecordListView.as_view(), name='list'),
]
