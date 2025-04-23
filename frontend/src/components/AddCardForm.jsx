import React, { useState } from 'react';

const AddCardForm = ({ columnId, onClose, onAddCard }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    try {
      setLoading(true);
      await onAddCard(columnId, title, description);
      setTitle('');
      setDescription('');
      onClose();
    } catch (error) {
      console.error('Error al agregar tarjeta:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-4 space-y-3">
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Título de la tarjeta"
        className="w-full p-2 border rounded-lg"
        required
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Descripción (opcional)"
        className="w-full p-2 border rounded-lg"
        rows="3"
      />
      <div className="flex space-x-2">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? 'Agregando...' : 'Agregar tarjeta'}
        </button>
        <button
          type="button"
          onClick={onClose}
          className="flex-1 bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600"
        >
          Cancelar
        </button>
      </div>
    </form>
  );
};

export default AddCardForm; 