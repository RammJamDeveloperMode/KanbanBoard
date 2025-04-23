from django.db import models

# Esta clase es solo para mantener la compatibilidad con Django
# ya que estamos usando DynamoDB como base de datos
class Board(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False  # No queremos que Django cree la tabla

    def __str__(self):
        return self.name

class Column(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    board_id = models.CharField(max_length=36)
    name = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False  # No queremos que Django cree la tabla

    def __str__(self):
        return f"{self.board_id} - {self.name}"

class Card(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    column_id = models.CharField(max_length=36)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False  # No queremos que Django cree la tabla

    def __str__(self):
        return self.title 