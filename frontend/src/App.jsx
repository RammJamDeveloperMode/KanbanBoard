import React from 'react';
import { DragDropContext } from '@hello-pangea/dnd';
import Board from './components/Board';
import './App.css';

const App = () => {
  return (
    <DragDropContext>
      <div className="min-h-screen bg-gray-100">
        <Board />
      </div>
    </DragDropContext>
  );
};

export default App;
