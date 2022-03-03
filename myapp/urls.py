from django.urls import path
from . import views
from . import users
from . import query
from . import mark
from . import markdata
from . import count
from . import specialist
from .train_predict_code import forecast


urlpatterns = [
    path('login/', users.login),
    path('reg/', users.reg),

    path('search/', views.get_initial_graph),
    path('querybyinfo/', views.demoproduct),

    path('queryallproducts/', query.queryallproducts),
    path('querymostreason/', query.Querymostreason),
    path('getops/', query.Getops),
    path('queryinfos/', query.Queryinfos),
    path('querybycondition/', query.Querybycondition),
    path('querymainharm/', query.Querymainharm),

    path('countbycondition/', count.Countbycondition),
    path('countproducthurtmost/', count.Countproducthurtmost),
    path('getcountops/', count.Getcountops),
    path('counthurtarea/', count.Counthurtarea),

    path('querymarkinfo/', mark.queryallmarkinfos),
    path('changerulesmark/', mark.changemarkinfos),
    path('insertrulesmark/', mark.insertmarkinfos),
    path('deletemark/', mark.deletemarks),
    path('insertdamagekey/', mark.InsertDamageKey),
    path('deletedamagekey/', mark.DeleteDamageKey),

    path('querymarkdata/', markdata.Queryall),
    path('querymarkinfos/', markdata.QueryInfos),
    path('modifyinfos/', markdata.Modifyinfos),
    path('modifysort/', markdata.Modifysort),
    path('modifysortbyproductname/', markdata.Modifysortbyproductname),
    path('deleteevent/', markdata.Deleteevent),

    path('pre/', forecast.Predict),
    path('createprnode/', forecast.Createpredictnode),

    path('querypreinfo/', specialist.Queryinfos),
    path('changeass/', specialist.Changeass),
    path('deleteass/', specialist.Deleteass),
]
