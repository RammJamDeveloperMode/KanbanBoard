declare module 'react-dnd' {
  import { RefObject } from 'react';

  export interface DragSourceMonitor {
    isDragging(): boolean;
  }

  export interface DropTargetMonitor {
    isOver(): boolean;
  }

  export function useDrag<T, P, R>(spec: {
    type: string;
    item: T;
    collect?: (monitor: DragSourceMonitor) => R;
  }): [R, RefObject<HTMLElement>];

  export function useDrop<T, P, R>(spec: {
    accept: string;
    drop?: (item: T) => void;
    collect?: (monitor: DropTargetMonitor) => R;
  }): [R, RefObject<HTMLElement>];
} 