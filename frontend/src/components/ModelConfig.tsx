import React from 'react';
import { ModelConfig as ModelConfigType } from '../types';
import './ModelConfig.css';

interface ModelConfigProps {
  config: ModelConfigType;
  onChange: (config: ModelConfigType) => void;
}

const ModelConfig: React.FC<ModelConfigProps> = ({ config, onChange }) => {
  const handleChange = (field: keyof ModelConfigType, value: any) => {
    onChange({ ...config, [field]: value });
  };

  const handleCharacterChange = (index: number, value: string) => {
    const newCharacters = [...config.characters];
    newCharacters[index] = value;
    onChange({ ...config, characters: newCharacters });
  };

  return (
    <div className="model-config">
      <h3>模型配置</h3>
      
      <div className="config-section">
        <label>动漫模式</label>
        <div className="anime-mode-group">
          <button
            className={`mode-button ${config.anime_mode === 'blackwhite' ? 'active' : ''}`}
            onClick={() => handleChange('anime_mode', 'blackwhite')}
          >
            黑白
          </button>
          <button
            className={`mode-button ${config.anime_mode === 'color' ? 'active' : ''}`}
            onClick={() => handleChange('anime_mode', 'color')}
          >
            彩色
          </button>
          <button
            className={`mode-button ${config.anime_mode === 'illustration' ? 'active' : ''}`}
            onClick={() => handleChange('anime_mode', 'illustration')}
          >
            插画
          </button>
        </div>
      </div>

      <div className="config-section">
        <label>时代背景</label>
        <select
          value={config.era}
          onChange={(e) => handleChange('era', e.target.value)}
        >
          <option value="medieval">中世纪</option>
          <option value="renaissance">文艺复兴</option>
          <option value="cold_war">冷战</option>
          <option value="modern">现代</option>
          <option value="digital">数字时代</option>
          <option value="warring_states">中华战国</option>
          <option value="tang">中华唐代</option>
          <option value="song">中华宋代</option>
        </select>
      </div>

      <div className="config-section">
        <label>随机选项</label>
        <div className="checkbox-group">
          <label>
            <input
              type="checkbox"
              checked={config.random_fine_tune}
              onChange={(e) => handleChange('random_fine_tune', e.target.checked)}
            />
            随机微调
          </label>
          <label>
            <input
              type="checkbox"
              checked={config.random_composition}
              onChange={(e) => handleChange('random_composition', e.target.checked)}
            />
            随机构图
          </label>
          <label>
            <input
              type="checkbox"
              checked={config.random_shot}
              onChange={(e) => handleChange('random_shot', e.target.checked)}
            />
            随机镜头
          </label>
        </div>
      </div>

      <div className="config-section">
        <label>参数调节</label>
        <div className="params-grid">
          <div className="param-item">
            <label>画面气氛 ({config.atmosphere.toFixed(2)})</label>
            <div className="param-range">
              <span className="range-label">阴暗恐怖</span>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={config.atmosphere}
                onChange={(e) => handleChange('atmosphere', parseFloat(e.target.value))}
              />
              <span className="range-label">明亮欢快</span>
            </div>
          </div>

          <div className="param-item">
            <label>拍摄距离 ({config.distance.toFixed(2)})</label>
            <div className="param-range">
              <span className="range-label">怼脸拍摄</span>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={config.distance}
                onChange={(e) => handleChange('distance', parseFloat(e.target.value))}
              />
              <span className="range-label">全身远景</span>
            </div>
          </div>

          <div className="param-item">
            <label>写实程度 ({config.realism.toFixed(2)})</label>
            <div className="param-range">
              <span className="range-label">卡通</span>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={config.realism}
                onChange={(e) => handleChange('realism', parseFloat(e.target.value))}
              />
              <span className="range-label">写实</span>
            </div>
          </div>

          <div className="param-item">
            <label>动态强度 ({config.dynamic.toFixed(2)})</label>
            <div className="param-range">
              <span className="range-label">静态</span>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={config.dynamic}
                onChange={(e) => handleChange('dynamic', parseFloat(e.target.value))}
              />
              <span className="range-label">强动感</span>
            </div>
          </div>
        </div>
      </div>

      <div className="config-section">
        <label>主角描述</label>
        {[0, 1, 2, 3, 4].map((index) => (
          <input
            key={index}
            type="text"
            placeholder={`角色 ${index + 1}`}
            value={config.characters[index] || ''}
            onChange={(e) => handleCharacterChange(index, e.target.value)}
            className="character-input"
          />
        ))}
      </div>
    </div>
  );
};

export default ModelConfig;
