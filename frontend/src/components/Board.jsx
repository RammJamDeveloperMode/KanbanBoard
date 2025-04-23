import React, { useCallback, useMemo, useState } from 'react';
import { DragDropContext, Droppable } from '@hello-pangea/dnd';
import Column from './Column';
import { useQuery, useMutation } from '@apollo/client';
import { GET_BOARD, MOVE_CARD, ADD_COLUMN, DELETE_COLUMN, UPDATE_BOARD, CREATE_BOARD, DELETE_CARD, CREATE_CARD } from '../graphql/queries';

const Board = () => {
  const [createBoard] = useMutation(CREATE_BOARD);
  const [newColumnName, setNewColumnName] = useState('');
  const [showAddColumnForm, setShowAddColumnForm] = useState(false);
  const [localBoard, setLocalBoard] = useState(null);
  const [isEditingBoardName, setIsEditingBoardName] = useState(false);
  const [editedBoardName, setEditedBoardName] = useState('');

  const { loading, error, refetch } = useQuery(GET_BOARD, {
    fetchPolicy: 'network-only',
    onCompleted: async (data) => {
      if (data?.boards?.[0]) {
        setLocalBoard(JSON.parse(JSON.stringify(data.boards[0])));
      } else {
        try {
          await createBoard({
            variables: {
              name: 'Mi Tablero Kanban',
              type: 'board'
            }
          });
          await refetch();
        } catch (error) {
          console.error('Error al crear el tablero:', error);
        }
      }
    }
  });

  const [moveCard] = useMutation(MOVE_CARD, {
    onCompleted: (data) => {
      if (data?.moveCard?.success) {
        refetch();
      }
    }
  });

  const [addColumn] = useMutation(ADD_COLUMN, {
    onCompleted: () => {
      setNewColumnName('');
      setShowAddColumnForm(false);
      refetch();
    }
  });

  const [deleteColumn] = useMutation(DELETE_COLUMN, {
    onCompleted: (data) => {
      if (data?.deleteColumn?.success) {
        // Actualizar el estado local solo si la mutación fue exitosa
        setLocalBoard(prevBoard => {
          if (!prevBoard) return null;
          const newBoard = JSON.parse(JSON.stringify(prevBoard));
          newBoard.columns = newBoard.columns.filter(col => col.id !== data.deleteColumn.columnId);
          return newBoard;
        });
      }
    }
  });

  const [updateBoard] = useMutation(UPDATE_BOARD, {
    onCompleted: () => {
      refetch();
    }
  });

  const [deleteCard] = useMutation(DELETE_CARD, {
    onCompleted: () => {
      refetch();
    }
  });

  const [createCard] = useMutation(CREATE_CARD, {
    onCompleted: (data) => {
      if (data?.createCard?.card) {
        // Actualizar el estado local inmediatamente
        setLocalBoard(prevBoard => {
          if (!prevBoard) return null;
          const newBoard = JSON.parse(JSON.stringify(prevBoard));
          const column = newBoard.columns.find(col => col.id === data.createCard.card.columnId);
          if (column) {
            column.cards = column.cards || [];
            column.cards.push(data.createCard.card);
            // Reordenar las tarjetas
            column.cards.sort((a, b) => (a.order || 0) - (b.order || 0));
          }
          return newBoard;
        });
      }
    }
  });

  const board = useMemo(() => {
    if (!localBoard) return null;
    
    if (localBoard.type !== 'board') {
      console.error('El item no es un tablero:', localBoard);
      return null;
    }
    
    return {
      ...localBoard,
      columns: (localBoard.columns || [])
        .filter(column => column && column.type === 'column')
        .sort((a, b) => (a.order || 0) - (b.order || 0))
        .map(column => ({
          ...column,
          cards: (column.cards || [])
            .filter(card => card && card.type === 'card')
            .sort((a, b) => (a.order || 0) - (b.order || 0))
        }))
    };
  }, [localBoard]);

  const handleAddColumn = useCallback(async () => {
    if (!newColumnName.trim() || !board?.id) return;
    
    try {
      await addColumn({
        variables: {
          boardId: String(board.id),
          name: newColumnName.trim(),
          order: board.columns.length
        }
      });
    } catch (error) {
      console.error('Error al agregar columna:', error);
    }
  }, [addColumn, board, newColumnName]);

  const handleDeleteColumn = useCallback(async (columnId) => {
    try {
      const { data } = await deleteColumn({
        variables: { columnId }
      });

      if (data.deleteColumn.success) {
        setLocalBoard(prevBoard => ({
          ...prevBoard,
          columns: prevBoard.columns.filter(col => col.id !== columnId)
        }));
      } else {
        console.error('Error al eliminar la columna:', data.deleteColumn.error);
      }
    } catch (error) {
      console.error('Error al eliminar la columna:', error);
    }
  }, [deleteColumn, setLocalBoard]);

  const handleDeleteCard = useCallback(async (cardId) => {
    if (!cardId) return;

    try {
      // Actualizar el estado local inmediatamente
      setLocalBoard(prevBoard => {
        if (!prevBoard) return null;
        const newBoard = JSON.parse(JSON.stringify(prevBoard));
        newBoard.columns = newBoard.columns.map(column => ({
          ...column,
          cards: column.cards.filter(card => card.id !== cardId)
        }));
        return newBoard;
      });

      await deleteCard({
        variables: { id: String(cardId) }
      });
    } catch (error) {
      console.error('Error al eliminar tarjeta:', error);
      // Revertir el cambio local si hay un error
      refetch();
    }
  }, [deleteCard, refetch]);

  const handleAddCard = useCallback(async (columnId, title, description) => {
    if (!columnId || !title.trim()) return;
    
    try {
      // Actualizar el estado local inmediatamente
      setLocalBoard(prevBoard => {
        if (!prevBoard) return null;
        const newBoard = JSON.parse(JSON.stringify(prevBoard));
        const column = newBoard.columns.find(col => col.id === columnId);
        if (column) {
          const newCard = {
            id: 'temp-' + Date.now(), // ID temporal
            type: 'card',
            title: title.trim(),
            description: description.trim(),
            order: column.cards ? column.cards.length : 0,
            columnId: columnId
          };
          column.cards = column.cards || [];
          column.cards.push(newCard);
        }
        return newBoard;
      });

      await createCard({
        variables: {
          columnId: String(columnId),
          title: title.trim(),
          description: description.trim(),
          order: 0
        }
      });
    } catch (error) {
      console.error('Error al agregar tarjeta:', error);
      // Revertir el cambio local si hay un error
      refetch();
    }
  }, [createCard, refetch]);

  const handleDragEnd = useCallback((result) => {
    if (!result.destination) return;

    const { draggableId, source, destination } = result;
    const cardId = draggableId;
    const sourceColumnId = source.droppableId;
    const destinationColumnId = destination.droppableId;
    const newOrder = destination.index;

    // Actualizar el estado local inmediatamente
    setLocalBoard(prevBoard => {
      if (!prevBoard) return null;
      
      const newBoard = JSON.parse(JSON.stringify(prevBoard));
      const sourceColumn = newBoard.columns.find(col => col.id === sourceColumnId);
      const destColumn = newBoard.columns.find(col => col.id === destinationColumnId);
      const card = sourceColumn.cards.find(card => card.id === cardId);
      
      if (sourceColumn && destColumn && card) {
        // Remover la tarjeta de la columna origen
        sourceColumn.cards = sourceColumn.cards.filter(c => c.id !== cardId);
        
        // Actualizar el order de la tarjeta
        card.order = newOrder;
        card.columnId = destinationColumnId;
        
        // Insertar la tarjeta en la nueva posición
        destColumn.cards.splice(newOrder, 0, card);
        
        // Reordenar las tarjetas en ambas columnas
        sourceColumn.cards.sort((a, b) => a.order - b.order);
        destColumn.cards.sort((a, b) => a.order - b.order);
      }
      
      return newBoard;
    });

    // Llamar a la mutación
    moveCard({
      variables: {
        cardId,
        columnId: destinationColumnId,
        cardOrder: newOrder
      }
    });
  }, [moveCard]);

  const handleEditBoardName = useCallback(async () => {
    if (!editedBoardName.trim() || !board?.id) return;
    
    try {
      await updateBoard({
        variables: {
          id: board.id,
          name: editedBoardName.trim()
        }
      });
      setIsEditingBoardName(false);
    } catch (error) {
      console.error('Error al actualizar el nombre del tablero:', error);
    }
  }, [board?.id, editedBoardName, updateBoard]);

  const renderColumns = useMemo(() => {
    if (!board?.columns) return null;
    
    return board.columns.map((column, index) => (
      <Column
        key={column.id}
        id={column.id}
        title={column.name}
        cards={column.cards}
        order={index}
        onDeleteColumn={handleDeleteColumn}
        onDeleteCard={handleDeleteCard}
        onAddCard={handleAddCard}
      />
    ));
  }, [board?.columns, handleDeleteColumn, handleDeleteCard, handleAddCard]);

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!board) return <div>No se encontró el tablero</div>;

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <div className="flex items-center justify-between p-4 bg-white shadow">
        {isEditingBoardName ? (
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={editedBoardName}
              onChange={(e) => setEditedBoardName(e.target.value)}
              className="border rounded px-2"
            />
            <button
              onClick={handleEditBoardName}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Guardar
            </button>
            <button
              onClick={() => {
                setIsEditingBoardName(false);
                setEditedBoardName(board.name);
              }}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Cancelar
            </button>
          </div>
        ) : (
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold">{board.name}</h1>
            <button
              onClick={() => {
                setIsEditingBoardName(true);
                setEditedBoardName(board.name);
              }}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
          </div>
        )}
      </div>

      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="board" type="column" direction="horizontal">
          {(provided) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className="flex overflow-x-auto p-4 space-x-4 h-full"
            >
              {renderColumns}
              {provided.placeholder}
              
              <div className="flex-shrink-0 w-80">
                {showAddColumnForm ? (
                  <div className="p-4 bg-white rounded shadow">
                    <input
                      type="text"
                      value={newColumnName}
                      onChange={(e) => setNewColumnName(e.target.value)}
                      placeholder="Nombre de la columna"
                      className="w-full border rounded px-2 py-1 mb-2"
                    />
                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={() => setShowAddColumnForm(false)}
                        className="px-4 py-2 text-gray-600 hover:text-gray-800"
                      >
                        Cancelar
                      </button>
                      <button
                        onClick={handleAddColumn}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                      >
                        Añadir
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => setShowAddColumnForm(true)}
                    className="w-full p-4 bg-gray-100 rounded hover:bg-gray-200 text-gray-600"
                  >
                    + Añadir columna
                  </button>
                )}
              </div>
            </div>
          )}
        </Droppable>
      </DragDropContext>
    </div>
  );
};

export default Board; 