from pyspark.ml.feature import VectorAssembler
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, split, date_add, year, month, dayofweek, dayofmonth, concat_ws, to_json, struct, \
    to_date
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, DateType, FloatType
from pyspark.ml import PipelineModel
from pyspark.sql import DataFrameWriter
import datetime
import os
import pandas as pd
import psycopg2






# Crear una SparkSession

spark = SparkSession.builder \
    .appName("KafkaSparkStreaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.jars.repositories", "https://repo1.maven.org/maven2") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
    .config("spark.driver.extraClassPath", "/Users/rushabhpatel/Desktop/TFG/postgresql-42.7.3.jar") \
    .enableHiveSupport() \
    .getOrCreate()


# configuracion para conectar con el servidor Kafka
kafka_topic_name = "PruebaStream"
kafka_bootstrap_servers = 'localhost:9092'

kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic_name) \
    .option("startingOffsets", "earliest") \
    .load()


columns = ["supermarket", "category", "name", "description", "price", "reference_price", "reference_unit", "insert_date"]

# Decodificar y dividir el mensaje de Kafka
data_df = kafka_df.selectExpr("CAST(value AS STRING) as value") \
    .withColumn("csv", split(col("value"), ",")) \
    .select(*[col("csv")[i].alias(columns[i]) for i in range(len(columns))])

# Corregir tipos de datos
data_df = data_df.select(
    col("supermarket"),
    col("category"),
    col("name"),
    col("description"),
    col("price").cast("float"),
    col("reference_price").cast("float"),
    col("reference_unit"),
    col("insert_date").cast(DateType())
)

# Preparar las columnas para el modelo
data_df = data_df.withColumn("prediction_date", date_add(col("insert_date"), 1))
data_df = data_df.withColumn("year", year(col("prediction_date")))
data_df = data_df.withColumn("month", month(col("prediction_date")))
data_df = data_df.withColumn("dayofweek", dayofweek(col("prediction_date")))
data_df = data_df.withColumn("day", dayofmonth(col("prediction_date")))

columnas_especificas = ["supermarket", "name", "price","insert_date",'category']
df_sin_nulos = data_df.dropna(subset=columnas_especificas)
data_df = df_sin_nulos


# Cargar el modelo preentrenado
model = PipelineModel.load("/Users/rushabhpatel/Desktop/TFG/Notebook/modeloPreciosSuper")




'''def process_streaming_data(batch_df, batch_id):
    # Asegurarse de que la columna de fecha está en el formato correcto
    batch_df = batch_df.withColumn("insert_date", to_date("insert_date"))
    batch_df = batch_df.withColumn("year", year("insert_date"))
    batch_df = batch_df.withColumn("month", month("insert_date"))
    batch_df = batch_df.withColumn("day", dayofmonth("insert_date"))
    batch_df = batch_df.withColumn("dayofweek", dayofweek("insert_date"))

    batch_df = batch_df.withColumn("price", batch_df.price.cast(FloatType()))
    batch_df = batch_df.withColumn("reference_price", col("reference_price").cast("float"))
    batch_df = batch_df.withColumn("name", col("name").cast("string"))
    batch_df = batch_df.withColumn("category", col("name").cast("string"))
    batch_df = batch_df.withColumn("description", col("name").cast("string"))


    # Aplicar el modelo para hacer predicciones
    predictions = model.transform(batch_df)


    # Seleccionar las columnas de interés para guardar
    predictions = predictions.select("supermarket", "category", "name", "prediction_date", "prediction")


    # Definir la ruta para guardar los archivos JSON
    path = f"/Users/rushabhpatel/Desktop/Predicciones"

    # Guardar las predicciones en formato JSON
    predictions.write.mode('append').json(path)


# Configurar la consulta de streaming para usar la función de procesamiento
query = data_df.writeStream \
    .outputMode("append") \
    .foreachBatch(process_streaming_data) \
    .start()

query.awaitTermination() '''


def process_streaming_data(batch_df, batch_id):

    batch_df = batch_df.withColumn("insert_date", to_date("insert_date"))
    batch_df = batch_df.withColumn("year", year("insert_date"))
    batch_df = batch_df.withColumn("month", month("insert_date"))
    batch_df = batch_df.withColumn("day", dayofmonth("insert_date"))
    batch_df = batch_df.withColumn("dayofweek", dayofweek("insert_date"))


    batch_df = batch_df.withColumn("price", batch_df.price.cast(FloatType()))
    batch_df = batch_df.withColumn("reference_price", col("reference_price").cast("float"))
    batch_df = batch_df.withColumn("name", col("name").cast("string"))
    batch_df = batch_df.withColumn("category", col("category").cast("string"))
    batch_df = batch_df.withColumn("description", col("description").cast("string"))

    # Aplicar el modelo para hacer predicciones
    predictions = model.transform(batch_df)


    predictions = predictions.select("supermarket", "category", "name", "prediction_date", "prediction")

    # Conexion a bbdd
    url = "jdbc:postgresql://localhost:5432/productos_supermercado"
    properties = {
        "user": "postgres",
        "password": "rushabh",
        "driver": "org.postgresql.Driver"
    }

    # Guardar las predicciones en bbdd
    predictions.write.jdbc(url=url, table="tabla_predicciones", mode="append", properties=properties)



query = data_df.writeStream \
    .outputMode("append") \
    .foreachBatch(process_streaming_data) \
    .start()

query.awaitTermination()



