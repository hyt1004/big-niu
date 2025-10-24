import React, { useState } from 'react';
import './NovelInput.css';

interface NovelInputProps {
  onTextChange: (text: string) => void;
  onGenerate: () => void;
}

const NovelInput: React.FC<NovelInputProps> = ({ onTextChange, onGenerate }) => {
  const [text, setText] = useState('');

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value;
    setText(newText);
    onTextChange(newText);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'text/plain') {
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result as string;
        setText(content);
        onTextChange(content);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="novel-input">
      <h3>小说文案输入</h3>
      <textarea
        className="text-area"
        value={text}
        onChange={handleTextChange}
        placeholder="请输入小说文本..."
        rows={10}
      />
      <div className="file-upload">
        <label htmlFor="file-input" className="file-label">
          上传 TXT 文件
        </label>
        <input
          id="file-input"
          type="file"
          accept=".txt"
          onChange={handleFileUpload}
          className="file-input"
        />
      </div>
      <div className="button-container">
        <button className="generate-btn" onClick={onGenerate}>
          生成模型提示词
        </button>
      </div>
    </div>
  );
};

export default NovelInput;
