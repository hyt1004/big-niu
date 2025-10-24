import React, { useState } from 'react';
import './NovelInput.css';

interface NovelInputProps {
  onTextChange: (text: string) => void;
  onGenerate: () => void;
}

const NovelInput: React.FC<NovelInputProps> = ({ onTextChange }) => {
  const [text, setText] = useState('');
  const [prompt, setPrompt] = useState('');

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

  const handleSubmitText = () => {
    if (!text.trim()) {
      alert('请输入小说文本');
      return;
    }
    console.log('提交文本:', text);
  };

  const handleSavePrompt = () => {
    console.log('保存提示词:', prompt);
    alert('提示词已保存');
  };

  return (
    <div className="novel-input">
      <h3 className="panel-title">小说文案</h3>
      
      <div className="textarea-container">
        <textarea
          className="text-area"
          value={text}
          onChange={handleTextChange}
          placeholder="请输入小说内容..."
          rows={8}
        />
        <label htmlFor="file-input" className="file-upload-btn">
          上传TXT文件
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
        <button className="submit-btn" onClick={handleSubmitText}>
          提交文本
        </button>
      </div>

      <div className="prompt-section">
        <h4 className="section-subtitle">模型提示词</h4>
        <textarea
          className="prompt-area"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="配置参数后点击'生成提示词'按钮"
          rows={5}
          readOnly
        />
        <div className="button-container">
          <button className="save-btn" onClick={handleSavePrompt}>
            保存
          </button>
        </div>
      </div>
    </div>
  );
};

export default NovelInput;
