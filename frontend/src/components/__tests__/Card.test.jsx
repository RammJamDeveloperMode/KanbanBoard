import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { Card } from '../Card';
import { DELETE_CARD } from '../../graphql/queries';

const mockCard = {
    id: '1',
    title: 'Test Card',
    description: 'Test Description',
    order: 1,
};

const mocks = [
    {
        request: {
            query: DELETE_CARD,
            variables: { id: '1' },
        },
        result: {
            data: {
                deleteCard: {
                    success: true,
                    __typename: 'DeleteCardPayload',
                },
            },
        },
    },
];

describe('Card Component', () => {
    it('renders card title and description', () => {
        render(
            <MockedProvider mocks={mocks} addTypename={false}>
                <Card card={mockCard} />
            </MockedProvider>
        );

        expect(screen.getByText('Test Card')).toBeInTheDocument();
        expect(screen.getByText('Test Description')).toBeInTheDocument();
    });

    it('shows edit form when edit button is clicked', () => {
        render(
            <MockedProvider mocks={mocks} addTypename={false}>
                <Card card={mockCard} />
            </MockedProvider>
        );

        const editButton = screen.getByRole('button', { name: /edit/i });
        fireEvent.click(editButton);

        expect(screen.getByDisplayValue('Test Card')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Test Description')).toBeInTheDocument();
    });

    it('shows delete confirmation modal when delete button is clicked', () => {
        render(
            <MockedProvider mocks={mocks} addTypename={false}>
                <Card card={mockCard} />
            </MockedProvider>
        );

        const deleteButton = screen.getByRole('button', { name: /delete/i });
        fireEvent.click(deleteButton);

        expect(screen.getByText('¿Estás seguro de que quieres eliminar esta tarjeta?')).toBeInTheDocument();
    });
}); 