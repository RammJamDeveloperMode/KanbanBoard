import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';

// Configuración global para las pruebas
configure({ testIdAttribute: 'data-testid' }); 