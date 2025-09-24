import { useEffect, useRef } from 'react';
import { Socket, io } from 'socket.io-client';

export const useWebSocket = () => {
  const socket = useRef<Socket | null>(null);

  useEffect(() => {
    // Initialize socket connection
    socket.current = io(process.env.VITE_API_URL || 'http://localhost:3000', {
      withCredentials: true,
    });

    // Handle connection events
    socket.current.on('connect', () => {
      console.log('WebSocket connected');
    });

    socket.current.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    socket.current.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    // Cleanup on unmount
    return () => {
      if (socket.current) {
        socket.current.disconnect();
      }
    };
  }, []);

  return { socket: socket.current };
};

export default useWebSocket;
