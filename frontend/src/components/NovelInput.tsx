import React, { useState } from 'react';
import './NovelInput.css';

interface NovelInputProps {
  onTextChange: (text: string) => void;
  onSubmit: (text: string, useStoryboard: boolean) => void;
  onPromptChange: (prompt: string) => void;
  prompt: string;
}

const NovelInput: React.FC<NovelInputProps> = ({
  onTextChange,
  onSubmit,
  onPromptChange,
  prompt,
}) => {
  const [text, setText] = useState('');
  const [useStoryboard, setUseStoryboard] = useState(false);

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
    onSubmit(text, useStoryboard);
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
          📁 上传TXT文件
        </label>
        <input
          id="file-input"
          type="file"
          accept=".txt"
          onChange={handleFileUpload}
          className="file-input"
        />
      </div>

      <div className="storyboard-option">
        <label className="checkbox-label" title="启用分镜表功能可以对每个镜头进行详细编辑">
          <input
            type="checkbox"
            checked={useStoryboard}
            onChange={(e) => setUseStoryboard(e.target.checked)}
          />
          <span>启用分镜表功能</span>
        </label>
      </div>
      
      <div className="button-container">
        <button className="submit-btn" onClick={handleSubmitText}>
          ✨ 提交文本
        </button>
      </div>

      <div className="prompt-section">
        <h4 className="section-subtitle">模型提示词</h4>
        <textarea
          className="prompt-area"
          value={prompt}
          onChange={(e) => onPromptChange(e.target.value)}
          placeholder="配置参数后会自动生成提示词"
          rows={5}
        />
        <div className="button-container">
          <button className="save-btn" onClick={handleSavePrompt}>
            💾 保存
          </button>
        </div>
      </div>
    </div>
  );
};

export default NovelInput;
