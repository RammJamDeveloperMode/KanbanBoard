import { gql } from '@apollo/client';

export const GET_BOARD = gql`
  query GetBoard {
    boards {
      id
      type
      name
      columns {
        id
        type
        name
        order
        cards {
          id
          type
          title
          description
          order
          columnId
        }
      }
    }
  }
`;

export const CREATE_BOARD = gql`
  mutation CreateBoard($name: String!, $type: String!) {
    createBoard(name: $name, type: $type) {
      board {
        id
        type
        name
      }
    }
  }
`;

export const MOVE_CARD = gql`
  mutation MoveCard($cardId: String!, $columnId: String!, $cardOrder: Int!) {
    moveCard(cardId: $cardId, columnId: $columnId, cardOrder: $cardOrder) {
      success
      message
      __typename
    }
  }
`;

export const MOVE_COLUMN = gql`
  mutation MoveColumn($columnId: ID!, $order: Int!) {
    moveColumn(columnId: $columnId, order: $order) {
      success
      error
      __typename
    }
  }
`;

export const ADD_COLUMN = gql`
  mutation AddColumn($boardId: ID!, $name: String!, $order: Int) {
    createColumn(boardId: $boardId, name: $name, order: $order) {
      column {
        id
        type
        name
        order
      }
      error
    }
  }
`;

export const DELETE_COLUMN = gql`
  mutation DeleteColumn($columnId: String!) {
    deleteColumn(columnId: $columnId) {
      success
      error
      columnId
      __typename
    }
  }
`;

export const DELETE_CARD = gql`
  mutation DeleteCard($id: ID!) {
    deleteCard(id: $id) {
      success
      __typename
    }
  }
`;

export const UPDATE_BOARD = gql`
  mutation UpdateBoard($id: ID!, $name: String!) {
    updateBoard(id: $id, name: $name) {
      board {
        id
        name
      }
    }
  }
`;

export const UPDATE_COLUMN = gql`
  mutation UpdateColumn($id: ID!, $name: String!, $order: Int) {
    updateColumn(id: $id, name: $name, order: $order) {
      column {
        id
        name
        order
      }
      error
    }
  }
`;

export const CREATE_CARD = gql`
  mutation CreateCard($columnId: ID!, $title: String!, $description: String, $order: Int) {
    createCard(columnId: $columnId, title: $title, description: $description, order: $order) {
      card {
        id
        type
        title
        description
        order
        columnId
      }
    }
  }
`;

export const UPDATE_CARD = gql`
  mutation UpdateCard($id: ID!, $title: String!, $description: String) {
    updateCard(id: $id, title: $title, description: $description) {
      card {
        id
        type
        title
        description
        order
        columnId
      }
    }
  }
`;

export const FIX_CARD_ORDERS = gql`
  mutation FixCardOrders {
    fixCardOrders {
      success
      error
      __typename
    }
  }
`; 