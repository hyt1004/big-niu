import React, { useState } from 'react';
import { StoryboardTable, StoryboardCell } from '../types';
import apiService from '../services/api';
import './NovelInput.css';

interface NovelInputProps {
  onTextChange: (text: string) => void;
  onGenerate: () => void;
  storyboardEnabled: boolean;
  onStoryboardToggle: (enabled: boolean) => void;
  storyboardData: StoryboardTable | null;
  storyboardLoading: boolean;
  onStoryboardCellUpdate: (shotNumber: number, field: keyof StoryboardCell, value: any) => void;
  onSaveStoryboard: () => void;
  onShowMessage: (message: string, type?: 'success' | 'error' | 'info' | 'warning') => void;
}

const NovelInput: React.FC<NovelInputProps> = ({
  onTextChange,
  onGenerate,
  storyboardEnabled,
  onStoryboardToggle,
  onShowMessage,
}) => {
  const [text, setText] = useState('');
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

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
      onShowMessage('请输入小说文本', 'warning');
      return;
    }
    onGenerate();
  };

  const handleSavePrompt = async () => {
    if (!prompt.trim()) {
      onShowMessage('请输入提示词内容', 'warning');
      return;
    }

    setLoading(true);
    try {
      const response = await apiService.saveModelConfig({
        anime_mode: 'color',
        era: 'modern',
        random_fine_tune: false,
        random_composition: false,
        random_shot: false,
        shot_direction: 'horizontal',
        atmosphere: 0.5,
        distance: 0.5,
        realism: 0.5,
        dynamic: 0.5,
        characters: ['', ''],
      });

      if (response) {
        setPrompt('');
        onShowMessage('提示词已保存', 'success');
      } else {
        onShowMessage('保存提示词失败', 'error');
      }
    } catch (err) {
      onShowMessage('保存提示词失败', 'error');
      console.error('Save prompt error:', err);
    } finally {
      setLoading(false);
    }
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
        <label 
          className="checkbox-label"
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
        >
          <input
            type="checkbox"
            checked={storyboardEnabled}
            onChange={(e) => onStoryboardToggle(e.target.checked)}
          />
          <span>启用分镜表功能</span>
          {showTooltip && (
            <div className="tooltip">
              启用分镜表功能可以对每个镜头进行详细编辑
            </div>
          )}
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
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="配置参数后会自动生成提示词"
          rows={5}
        />
        <div className="button-container">
          <button 
            className="save-btn" 
            onClick={handleSavePrompt}
            disabled={loading}
          >
            💾 {loading ? '保存中...' : '保存'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default NovelInput;
