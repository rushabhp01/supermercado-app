from django.db import models

from django.contrib.auth.models import User




class Prediccion(models.Model):
    supermarket = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    name = models.CharField(max_length=100, primary_key=True)
    prediction_date = models.CharField(max_length=100)
    prediction = models.FloatField()


    class Meta:
        db_table = 'tabla_predicciones' 

    def __str__(self):
        return f"{self.name} - {self.prediction}"

    

