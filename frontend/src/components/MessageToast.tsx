import React, { useEffect } from 'react';
import './MessageToast.css';

interface MessageToastProps {
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
  onClose: () => void;
}

const MessageToast: React.FC<MessageToastProps> = ({ 
  message, 
  type, 
  duration = 3000, 
  onClose 
}) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <div className={`message-toast message-toast-${type}`}>
      <div className="message-content">
        <span className="message-text">{message}</span>
      </div>
    </div>
  );
};

export default MessageToast;
