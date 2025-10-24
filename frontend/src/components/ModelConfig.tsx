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
        <select
          value={config.anime_mode}
          onChange={(e) => handleChange('anime_mode', e.target.value)}
        >
          <option value="blackwhite">黑白</option>
          <option value="color">彩色</option>
          <option value="illustration">插画</option>
        </select>
      </div>

      <div className="config-section">
        <label>时代背景</label>
        <select
          value={config.era}
          onChange={(e) => handleChange('era', e.target.value)}
        >
          <option value="ancient">古代</option>
          <option value="medieval">中世纪</option>
          <option value="renaissance">文艺复兴</option>
          <option value="industrial">工业时代</option>
          <option value="modern">现代</option>
          <option value="future">未来</option>
          <option value="cyberpunk">赛博朋克</option>
          <option value="fantasy">奇幻</option>
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
            微调
          </label>
          <label>
            <input
              type="checkbox"
              checked={config.random_composition}
              onChange={(e) => handleChange('random_composition', e.target.checked)}
            />
            构图
          </label>
          <label>
            <input
              type="checkbox"
              checked={config.random_shot}
              onChange={(e) => handleChange('random_shot', e.target.checked)}
            />
            镜头
          </label>
        </div>
      </div>

      <div className="config-section">
        <label>气氛: {config.atmosphere}</label>
        <input
          type="range"
          min="0"
          max="100"
          value={config.atmosphere}
          onChange={(e) => handleChange('atmosphere', parseInt(e.target.value))}
        />
      </div>

      <div className="config-section">
        <label>距离: {config.distance}</label>
        <input
          type="range"
          min="0"
          max="100"
          value={config.distance}
          onChange={(e) => handleChange('distance', parseInt(e.target.value))}
        />
      </div>

      <div className="config-section">
        <label>写实: {config.realism}</label>
        <input
          type="range"
          min="0"
          max="100"
          value={config.realism}
          onChange={(e) => handleChange('realism', parseInt(e.target.value))}
        />
      </div>

      <div className="config-section">
        <label>动态: {config.dynamic}</label>
        <input
          type="range"
          min="0"
          max="100"
          value={config.dynamic}
          onChange={(e) => handleChange('dynamic', parseInt(e.target.value))}
        />
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
