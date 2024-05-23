from django.shortcuts import render

from .models import Prediccion

from django.http import HttpResponseRedirect
import json
from django.conf import settings
from pathlib import Path

from django.shortcuts import render
from .models import Prediccion
from django.conf import settings
from pathlib import Path
import json
from django.utils.timezone import make_aware
from datetime import datetime
from django.db.models import Min, Max
import re

def listar_predicciones(request):
    predicciones = Prediccion.objects.all()  # Obtener todas las predicciones de la base de datos
    return render(request, 'predicciones/lista_predicciones.html', {'predicciones': predicciones})





def buscar_producto(request):
    productos_encontrados = []
    mapeo_path = Path(settings.BASE_DIR) / 'diccionario2'
    with open(mapeo_path, 'r') as file:
        producto_mapeo = json.load(file)

    producto_keys = list(producto_mapeo.keys())
    productos_finales = [] 

    if request.method == 'POST':
        selected_products = request.POST.getlist('products')
        fecha = request.POST.get('prediction_date')

        for producto_usuario in selected_products:
            nombres_productos = producto_mapeo.get(producto_usuario, [])
            productos_por_nombre = []
            for nombre_producto in nombres_productos:
                


                productos = Prediccion.objects.filter(name=nombre_producto, prediction_date=fecha).order_by('prediction')

                
                if not productos.exists():
                    closest_before = Prediccion.objects.filter(
                        name=nombre_producto, prediction_date__lt=fecha
                    ).aggregate(Max('prediction_date'))['prediction_date__max']

                    if closest_before:
                        productos = Prediccion.objects.filter(name=nombre_producto, prediction_date=closest_before).order_by('prediction')
                
                productos_por_nombre.extend(productos)

            # Si hay productos encontrados, agregar el más barato a la lista final
            if productos_por_nombre:
                producto_mas_barato = min(productos_por_nombre, key=lambda x: x.prediction)
                productos_finales.append(producto_mas_barato)


    if producto_keys:
        prediction_dates = list(Prediccion.objects.values_list('prediction_date', flat=True).distinct().order_by('prediction_date'))
        #print(prediction_dates)

        cleaned_dates = [re.sub(r'\s\+\d{2}', '', date) for date in prediction_dates]
        #print(cleaned_dates)
        #prediction_dates = [date.strftime('%Y-%m-%d') for date in prediction_dates]
           

        
                    
    return render(request, 'buscar_producto.html', {'productos': productos_finales,  'product_keys': producto_keys,'prediction_dates': json.dumps(cleaned_dates)})





#############################################################################################









from django.shortcuts import render
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


file_path = '/Users/rushabhpatel/Desktop/TFG/Notebook/productos-supermercado2.csv'  
data = pd.read_csv(file_path)


data = data.dropna(subset=['name', 'insert_date'])
data['price'] = data['price'].str.replace(',', '.').astype(float)
data['reference_price'] = data['reference_price'].str.replace(',', '.').astype(float)

def price_distribution(request):
    supermarkets = data['supermarket'].unique()
    graphs = []

    for supermarket in supermarkets:
        supermarket_data = data[(data['supermarket'] == supermarket) & (data['price'] <= 20)]
        fig = px.box(supermarket_data, x='price', y='category', title=f'Distribución de precios por categoría en {supermarket} (0-20 euros)')
        graph = pio.to_html(fig, full_html=False)
        graphs.append(graph)

    return render(request, 'price_distribution.html', {'graphs': graphs})




def price_histogram(request):
    graphs = []
    supermarkets = data['supermarket'].unique()

    for supermarket in supermarkets:
        supermarket_data = data[data['supermarket'] == supermarket]
        category_counts = supermarket_data['category'].value_counts().nlargest(10).reset_index()
        category_counts.columns = ['category', 'count']
        fig = px.bar(category_counts, x='count', y='category', orientation='h', title=f'Productos más comunes en {supermarket}')
        graph = pio.to_html(fig, full_html=False)
        graphs.append(graph)

    return render(request, 'price_histogram.html', {'graphs': graphs})




def products_per_category(request):
    category_counts = data['category'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']
    fig = px.bar(category_counts, x='category', y='count', title='Cantidad de Productos por Categoría')
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    graph = pio.to_html(fig, full_html=False)
    return render(request, 'products_per_category.html', {'graph': graph})

def index(request):
    return render(request, 'index.html')



