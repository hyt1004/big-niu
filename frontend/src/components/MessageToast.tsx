import React, { useEffect } from 'react';
import { Message } from '../types';
import './MessageToast.css';

interface MessageToastProps {
  message: Message;
  onClose: (id: string) => void;
}

const MessageToast: React.FC<MessageToastProps> = ({ message, onClose }) => {
  useEffect(() => {
    const duration = message.duration || 3000;
    const timer = setTimeout(() => {
      onClose(message.id);
    }, duration);

    return () => clearTimeout(timer);
  }, [message, onClose]);

  const getIcon = () => {
    switch (message.type) {
      case 'success':
        return '✓';
      case 'error':
        return '✕';
      case 'warning':
        return '⚠';
      case 'info':
      default:
        return 'ℹ';
    }
  };

  return (
    <div className={`message-toast message-toast-${message.type}`}>
      <div className="message-icon">{getIcon()}</div>
      <div className="message-content">{message.content}</div>
      <button className="message-close" onClick={() => onClose(message.id)}>
        ×
      </button>
    </div>
  );
};

export default MessageToast;
