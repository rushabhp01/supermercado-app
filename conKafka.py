import pandas as pd
from kafka import KafkaProducer
import time

# Inicializar el productor Kafka
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: x.encode('utf-8'))

# Cargar datos del CSV
data = pd.read_csv('/Users/rushabhpatel/Desktop/TFG/Notebook/productos-supermercado2.csv', dtype={
    'supermarket': str,
    'category': str,
    'name': str,
    'description': str,
    'price': str,
    'reference_price': str,
    'reference_unit': str,
    'insert_date': str
}, low_memory=False)



data['price'] = pd.to_numeric(data['price'], errors='coerce')  # Convertir a float, errores a NaN
data['reference_price'] = pd.to_numeric(data['reference_price'], errors='coerce')  # Convertir a float, errores a NaN
data['insert_date'] = pd.to_datetime(data['insert_date'])  # Convertir a timestamp



data.sort_values('insert_date', inplace=True)

batch_size = 50000
#interval = 1800  # Enviar un lote cada 60 segundos
interval = 30
num_batches = len(data) // batch_size

# Simulación del envío de datos en tiempo real
"""
last_time = none
for index, row in data.iterrows():
    message = f"{row['supermarket']},{row['category']},{row['name']},{row['description']},{row['price']},{row['reference_price']},{row['reference_unit']},{row['insert_date']}"
    if last_time is not none:
        sleep_time = (row['insert_date'] - last_time).total_seconds()
        time.sleep(sleep_time)  # pausa basada en la diferencia de tiempo
    last_time = row['insert_date']
    producer.send('pruebastream', value=message)  # enviar mensaje al tópico de kafka
    producer.flush()  

print("All messages sent successfully")

"""

for i in range(num_batches + 1):
    start_index = i * batch_size
    end_index = start_index + batch_size
    batch = data.iloc[start_index:end_index]

    for index, row in batch.iterrows():
        message = f"{row['supermarket']},{row['category']},{row['name']},{row['description']},{row['price']},{row['reference_price']},{row['reference_unit']},{row['insert_date']}"
        producer.send('PruebaStream', value=message)
        producer.flush()

    if i < num_batches:
        time.sleep(interval)  # Pausa entre lotes

print("Se han enviado todos los mensajes correctamente")
