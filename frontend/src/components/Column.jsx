import React, { useState, useMemo } from 'react';
import { Draggable, Droppable } from '@hello-pangea/dnd';
import Card from './Card';
import AddCardForm from './AddCardForm';
import { useMutation } from '@apollo/client';
import { UPDATE_COLUMN } from '../graphql/queries';

const Column = React.memo(({ 
  id = '', 
  title = '', 
  cards = [], 
  order = 0,
  onDeleteColumn,
  onDeleteCard,
  onAddCard
}) => {
  const [showAddCardForm, setShowAddCardForm] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(title);

  const [updateColumn] = useMutation(UPDATE_COLUMN);

  const renderedCards = useMemo(() => {
    if (!cards) return [];
    
    return cards.map((card, index) => (
      <Card
        key={card.id}
        id={String(card.id)}
        title={card.title}
        description={card.description}
        index={index}
        onDelete={onDeleteCard}
      />
    ));
  }, [cards, onDeleteCard]);

  if (!id) {
    console.error('Error: Column debe tener un id');
    return null;
  }

  const columnId = String(id);

  const handleDelete = () => {
    onDeleteColumn(columnId);
    setShowDeleteModal(false);
  };

  const handleEditTitle = async () => {
    if (!editedTitle.trim()) return;
    
    try {
      await updateColumn({
        variables: {
          columnId,
          title: editedTitle.trim(),
          order
        }
      });
      setIsEditing(false);
    } catch (error) {
      console.error('Error al actualizar el nombre de la columna:', error);
    }
  };

  return (
    <>
      <Draggable draggableId={columnId} index={order} type="column">
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.draggableProps}
            className={`w-80 flex-shrink-0 ${
              snapshot.isDragging ? 'shadow-lg' : ''
            }`}
          >
            <div
              {...provided.dragHandleProps}
              className={`p-4 rounded-t-lg ${
                snapshot.isDragging ? 'bg-blue-100' : 'bg-gray-100'
              }`}
            >
              <div className="flex justify-between items-center">
                {isEditing ? (
                  <div className="flex items-center space-x-2 flex-grow">
                    <input
                      type="text"
                      value={editedTitle}
                      onChange={(e) => setEditedTitle(e.target.value)}
                      className="font-medium border rounded px-2 flex-grow"
                      onKeyPress={(e) => e.key === 'Enter' && handleEditTitle()}
                    />
                    <button
                      onClick={handleEditTitle}
                      className="px-2 py-1 bg-green-500 text-white rounded hover:bg-green-600 text-sm"
                    >
                      Guardar
                    </button>
                    <button
                      onClick={() => {
                        setIsEditing(false);
                        setEditedTitle(title);
                      }}
                      className="px-2 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm"
                    >
                      Cancelar
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center justify-between flex-grow">
                    <h3 className="font-semibold">{title}</h3>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => {
                          setIsEditing(true);
                          setEditedTitle(title);
                        }}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => setShowDeleteModal(true)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
            <Droppable droppableId={columnId} type="card">
              {(provided, snapshot) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className={`p-4 rounded-b-lg min-h-[100px] ${
                    snapshot.isDraggingOver ? 'bg-blue-50' : 'bg-white'
                  }`}
                >
                  {renderedCards}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>

            {showAddCardForm ? (
              <AddCardForm 
                columnId={columnId} 
                onClose={() => setShowAddCardForm(false)}
                onAddCard={onAddCard}
              />
            ) : (
              <button
                onClick={() => setShowAddCardForm(true)}
                className="mt-4 w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                + Añadir tarjeta
              </button>
            )}
          </div>
        )}
      </Draggable>

      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">¿Estás seguro de eliminar esta columna?</h3>
            <p className="text-gray-600 mb-6">
              Esta acción eliminará la columna "{title}" y todas sus tarjetas. Esta acción no se puede deshacer.
            </p>
            <div className="flex justify-end space-x-4">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancelar
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
});

export default Column;
