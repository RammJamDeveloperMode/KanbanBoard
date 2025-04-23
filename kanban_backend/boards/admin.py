from django.contrib import admin
from .models import Board, Column, Card

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('id', 'board_id', 'name', 'order', 'created_at', 'updated_at')
    search_fields = ('name', 'board_id')

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'column_id', 'title', 'order', 'created_at', 'updated_at')
    search_fields = ('title', 'column_id') 