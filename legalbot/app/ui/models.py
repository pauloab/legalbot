from django.db import models

class Configuracion(models.Model):
    clave = models.CharField(max_length=100)
    valor = models.CharField(max_length=100)

    def __str__(self):
        return self.clave