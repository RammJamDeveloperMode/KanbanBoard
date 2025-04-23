"""
URL configuration for kanban_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import logging
import json
from .schema import schema

logger = logging.getLogger(__name__)

class LoggingGraphQLView(GraphQLView):
    def dispatch(self, request, *args, **kwargs):
        logger.info(f"=== Iniciando solicitud GraphQL ===")
        logger.info(f"Método: {request.method}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Origin: {request.headers.get('Origin', 'No Origin')}")
        
        try:
            body = request.body.decode('utf-8') if request.body else 'No body'
            logger.info(f"Body: {body}")
            
            if body and body != 'No body':
                try:
                    body_json = json.loads(body)
                    logger.info(f"Body JSON: {json.dumps(body_json, indent=2)}")
                except json.JSONDecodeError:
                    logger.error("Error al decodificar el body como JSON")
            
            response = super().dispatch(request, *args, **kwargs)
            logger.info(f"Respuesta: {response.status_code}")
            logger.info(f"Contenido de la respuesta: {response.content.decode('utf-8')}")
            return response
        except Exception as e:
            logger.error(f"Error en solicitud GraphQL: {str(e)}")
            logger.error(f"Tipo de error: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'errors': [{'message': str(e)}]
            }, status=400)

@require_http_methods(["GET", "POST"])
def graphql_view(request):
    try:
        logger.info("=== Iniciando vista GraphQL ===")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Body: {request.body.decode('utf-8') if request.body else 'No body'}")
        
        response = LoggingGraphQLView.as_view(graphiql=True)(request)
        logger.info(f"=== Respuesta exitosa ===")
        return response
    except Exception as e:
        logger.error("=== Error en la vista GraphQL ===")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Tipo de error: {type(e)}")
        import traceback
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        return JsonResponse({
            'errors': [{'message': str(e)}]
        }, status=500)

def redirect_to_graphql(request):
    return redirect('/graphql/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql', csrf_exempt(LoggingGraphQLView.as_view(graphiql=True, schema=schema))),
    path('graphql/', csrf_exempt(LoggingGraphQLView.as_view(graphiql=True, schema=schema))),
]
