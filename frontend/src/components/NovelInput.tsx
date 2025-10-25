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
      <div className="title-row">
        <h3 className="panel-title">小说文案</h3>
        <div className="storyboard-switch">
          <label 
            className="switch-label"
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
          >
            <input
              type="checkbox"
              checked={storyboardEnabled}
              onChange={(e) => onStoryboardToggle(e.target.checked)}
            />
            <span className="switch-text">分镜表调整</span>
            {showTooltip && (
              <div className="tooltip">
                <div className="tooltip-content">
                  <div className="tooltip-title">分镜表使用流程：</div>
                  <div className="tooltip-steps">
                    <div className="tooltip-step">1. 提交文本</div>
                    <div className="tooltip-step">2. 模型生成分镜表</div>
                    <div className="tooltip-step">3. 用户修改分镜表</div>
                    <div className="tooltip-step">4. 保存分镜表</div>
                    <div className="tooltip-step">5. 生成视频</div>
                  </div>
                </div>
              </div>
            )}
          </label>
        </div>
      </div>
      
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
      
      <div className="button-container">
        <button className="submit-btn" onClick={handleSubmitText}>
          ✨ 提交文本
        </button>
      </div>

      <div className="prompt-section">
        <div className="prompt-header">
          <h4 className="section-subtitle">提示词管理</h4>
          <button 
            className="save-prompt-btn" 
            onClick={handleSavePrompt}
            disabled={loading}
          >
            {loading ? '保存中...' : '保存提示词'}
          </button>
        </div>
        
        <textarea
          className="prompt-area"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="输入提示词内容..."
          rows={3}
        />
      </div>
    </div>
  );
};

export default NovelInput;
