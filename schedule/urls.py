from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('createSchedule/', views.CreateSchedule.as_view(), name='createSchedule'),
    path('updateSchedule/', views.UpdateSchedule.as_view(), name='updateSchedule'),
    path('scheduleLog/', views.ScheduleLog.as_view()),
    path('scheduleGroupDetail/', views.ScheduleGroupDetail.as_view()),
    path('scheduleDetail/', views.ScheduleDetail.as_view()),
]