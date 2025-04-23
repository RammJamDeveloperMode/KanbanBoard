import React, { useState } from 'react';
import { Draggable } from '@hello-pangea/dnd';
import { useMutation } from '@apollo/client';
import { GET_BOARD, UPDATE_CARD } from '../graphql/queries';

const Card = ({ id, title, description, index, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(title);
  const [editedDescription, setEditedDescription] = useState(description);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const [updateCard] = useMutation(UPDATE_CARD, {
    refetchQueries: [{ query: GET_BOARD }],
    onCompleted: () => {
      setIsEditing(false);
    }
  });

  const handleDelete = async () => {
    try {
      await onDelete(String(id));
      setShowDeleteConfirm(false);
    } catch (error) {
      console.error('Error al eliminar tarjeta:', error);
    }
  };

  const handleUpdate = async () => {
    try {
      await updateCard({
        variables: {
          id,
          title: editedTitle,
          description: editedDescription
        }
      });
    } catch (error) {
      console.error('Error al actualizar la tarjeta:', error);
    }
  };

  if (!id) {
    console.error('Card rendered without id');
    return null;
  }

  return (
    <>
      <Draggable draggableId={id} index={index}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.draggableProps}
            {...provided.dragHandleProps}
            className={`bg-white rounded-lg shadow-md p-4 mb-2 ${
              snapshot.isDragging ? 'shadow-lg' : ''
            }`}
          >
            {isEditing ? (
              <div className="space-y-2">
                <input
                  type="text"
                  value={editedTitle}
                  onChange={(e) => setEditedTitle(e.target.value)}
                  className="w-full p-2 border rounded"
                  placeholder="Título"
                />
                <textarea
                  value={editedDescription}
                  onChange={(e) => setEditedDescription(e.target.value)}
                  className="w-full p-2 border rounded"
                  placeholder="Descripción"
                />
                <div className="flex justify-end space-x-2">
                  <button
                    onClick={() => {
                      setIsEditing(false);
                      setEditedTitle(title);
                      setEditedDescription(description);
                    }}
                    className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleUpdate}
                    className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    Guardar
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <div className="flex justify-between items-start">
                  <h3 className="font-medium">{title}</h3>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setIsEditing(true)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onClick={() => setShowDeleteConfirm(true)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
                {description && <p className="text-sm text-gray-600 mt-2">{description}</p>}
              </div>
            )}
          </div>
        )}
      </Draggable>
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-4 rounded-lg shadow-lg max-w-sm w-full mx-4">
            <p className="mb-4">¿Estás seguro de que quieres eliminar esta tarjeta?</p>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
              >
                Cancelar
              </button>
              <button
                onClick={handleDelete}
                className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

Card.displayName = 'Card';

export default Card; 