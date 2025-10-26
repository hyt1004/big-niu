import React, { useState, useEffect } from 'react';
import { StoryboardTable, StoryboardCell } from '../types';
import './StoryboardInfoBar.css';

interface StoryboardInfoBarProps {
  storyboard: StoryboardTable | null;
  loading: boolean;
  onExpand: () => void;
  onSubmit: () => void;
  onCellUpdate?: (cells: StoryboardCell[]) => void;
}

const StoryboardInfoBar: React.FC<StoryboardInfoBarProps> = ({
  storyboard,
  loading,
  onExpand,
  onSubmit,
  onCellUpdate,
}) => {
  const [editedCells, setEditedCells] = useState<StoryboardCell[]>([]);

  useEffect(() => {
    if (storyboard?.cells) {
      setEditedCells([...storyboard.cells]);
    }
  }, [storyboard]);

  const handleCellChange = (index: number, field: keyof StoryboardCell, value: string | number) => {
    const newCells = [...editedCells];
    newCells[index] = {
      ...newCells[index],
      [field]: value,
    };
    setEditedCells(newCells);
    if (onCellUpdate) {
      onCellUpdate(newCells);
    }
  };

  if (loading) {
    return (
      <div className="storyboard-info-bar">
        <div className="storyboard-loading">
          <div className="spinner"></div>
          <span>正在生成分镜表...</span>
        </div>
      </div>
    );
  }

  if (!storyboard) {
    return (
      <div className="storyboard-info-bar">
        <div className="storyboard-header">
          <h3>分镜表预览</h3>
          <div className="storyboard-stats">
            <span>0 行</span>
            <span>·</span>
            <span>0 个镜头</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="storyboard-info-bar">
      <div className="storyboard-header">
        <h3>分镜表预览</h3>
        <div className="storyboard-stats">
          <span>{storyboard?.rows || 0} 行</span>
          <span>·</span>
          <span>{storyboard?.cells.length || 0} 个镜头</span>
        </div>
      </div>

      <div className="storyboard-preview-table">
        <table>
          <thead>
            <tr>
              <th>镜头号</th>
              <th>镜头画面</th>
              <th>画面描述</th>
              <th>台词</th>
              <th>主要角色</th>
              <th>拍摄距离</th>
              <th>动态强度</th>
              <th>画面氛围</th>
            </tr>
          </thead>
          <tbody>
            {editedCells.slice(0, 3).map((cell, index) => (
              <tr key={index}>
                <td>{cell.shot_number}</td>
                <td className="image-cell">
                  {cell.scene_image ? (
                    <img src={cell.scene_image} alt={`Scene ${cell.shot_number}`} className="preview-thumbnail" />
                  ) : (
                    <div className="no-image-preview">暂无</div>
                  )}
                </td>
                <td className="description-cell">
                  <textarea
                    value={cell.scene_description}
                    onChange={(e) => handleCellChange(index, 'scene_description', e.target.value)}
                    className="preview-textarea"
                    rows={2}
                  />
                </td>
                <td className="dialogue-cell">
                  <textarea
                    value={cell.dialogue}
                    onChange={(e) => handleCellChange(index, 'dialogue', e.target.value)}
                    className="preview-textarea"
                    rows={2}
                  />
                </td>
                <td>
                  <textarea
                    value={cell.main_character}
                    onChange={(e) => handleCellChange(index, 'main_character', e.target.value)}
                    className="preview-textarea preview-textarea-short"
                    rows={2}
                  />
                </td>
                <td>
                  <div className="preview-number-control">
                    <button
                      type="button"
                      className="preview-number-btn preview-number-btn-minus"
                      onClick={() => {
                        const newValue = Math.max(0, cell.shooting_distance - 0.1);
                        handleCellChange(index, 'shooting_distance', parseFloat(newValue.toFixed(1)));
                      }}
                    >
                      −
                    </button>
                    <input
                      type="number"
                      min="0"
                      max="1"
                      step="0.1"
                      value={cell.shooting_distance}
                      onChange={(e) => {
                        const val = parseFloat(e.target.value);
                        if (!isNaN(val) && val >= 0 && val <= 1) {
                          handleCellChange(index, 'shooting_distance', val);
                        }
                      }}
                      onBlur={(e) => {
                        const val = parseFloat(e.target.value);
                        if (isNaN(val) || val < 0) {
                          handleCellChange(index, 'shooting_distance', 0);
                        } else if (val > 1) {
                          handleCellChange(index, 'shooting_distance', 1);
                        }
                      }}
                      className="preview-input preview-input-number"
                    />
                    <button
                      type="button"
                      className="preview-number-btn preview-number-btn-plus"
                      onClick={() => {
                        const newValue = Math.min(1, cell.shooting_distance + 0.1);
                        handleCellChange(index, 'shooting_distance', parseFloat(newValue.toFixed(1)));
                      }}
                    >
                      +
                    </button>
                  </div>
                </td>
                <td>
                  <div className="preview-number-control">
                    <button
                      type="button"
                      className="preview-number-btn preview-number-btn-minus"
                      onClick={() => {
                        const newValue = Math.max(0, cell.dynamic_intensity - 0.1);
                        handleCellChange(index, 'dynamic_intensity', parseFloat(newValue.toFixed(1)));
                      }}
                    >
                      −
                    </button>
                    <input
                      type="number"
                      min="0"
                      max="1"
                      step="0.1"
                      value={cell.dynamic_intensity}
                      onChange={(e) => {
                        const val = parseFloat(e.target.value);
                        if (!isNaN(val) && val >= 0 && val <= 1) {
                          handleCellChange(index, 'dynamic_intensity', val);
                        }
                      }}
                      onBlur={(e) => {
                        const val = parseFloat(e.target.value);
                        if (isNaN(val) || val < 0) {
                          handleCellChange(index, 'dynamic_intensity', 0);
                        } else if (val > 1) {
                          handleCellChange(index, 'dynamic_intensity', 1);
                        }
                      }}
                      className="preview-input preview-input-number"
                    />
                    <button
                      type="button"
                      className="preview-number-btn preview-number-btn-plus"
                      onClick={() => {
                        const newValue = Math.min(1, cell.dynamic_intensity + 0.1);
                        handleCellChange(index, 'dynamic_intensity', parseFloat(newValue.toFixed(1)));
                      }}
                    >
                      +
                    </button>
                  </div>
                </td>
                <td>
                  <div className="preview-number-control">
                    <button
                      type="button"
                      className="preview-number-btn preview-number-btn-minus"
                      onClick={() => {
                        const newValue = Math.max(0, cell.scene_atmosphere - 0.1);
                        handleCellChange(index, 'scene_atmosphere', parseFloat(newValue.toFixed(1)));
                      }}
                    >
                      −
                    </button>
                    <input
                      type="number"
                      min="0"
                      max="1"
                      step="0.1"
                      value={cell.scene_atmosphere}
                      onChange={(e) => {
                        const val = parseFloat(e.target.value);
                        if (!isNaN(val) && val >= 0 && val <= 1) {
                          handleCellChange(index, 'scene_atmosphere', val);
                        }
                      }}
                      onBlur={(e) => {
                        const val = parseFloat(e.target.value);
                        if (isNaN(val) || val < 0) {
                          handleCellChange(index, 'scene_atmosphere', 0);
                        } else if (val > 1) {
                          handleCellChange(index, 'scene_atmosphere', 1);
                        }
                      }}
                      className="preview-input preview-input-number"
                    />
                    <button
                      type="button"
                      className="preview-number-btn preview-number-btn-plus"
                      onClick={() => {
                        const newValue = Math.min(1, cell.scene_atmosphere + 0.1);
                        handleCellChange(index, 'scene_atmosphere', parseFloat(newValue.toFixed(1)));
                      }}
                    >
                      +
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {(storyboard?.cells.length || 0) > 3 && (
              <tr className="more-rows">
                <td colSpan={8}>还有 {(storyboard?.cells.length || 0) - 3} 个镜头...</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="storyboard-actions">
        <button className="btn-expand" onClick={onExpand}>
          <span className="icon">✏️</span>
          放大编辑
        </button>
        <button className="btn-submit" onClick={onSubmit}>
          <span className="icon">✓</span>
          提交分镜表
        </button>
      </div>
    </div>
  );
};

export default StoryboardInfoBar;
