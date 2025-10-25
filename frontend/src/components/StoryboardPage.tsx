import React, { useState, useEffect } from 'react';
import { StoryboardTable, StoryboardCell } from '../types';
import './StoryboardPage.css';

interface StoryboardPageProps {
  storyboard: StoryboardTable;
  onClose: () => void;
  onSave: (storyboard: StoryboardTable) => void;
}

const StoryboardPage: React.FC<StoryboardPageProps> = ({
  storyboard,
  onClose,
  onSave,
}) => {
  const [editedCells, setEditedCells] = useState<StoryboardCell[]>([]);

  useEffect(() => {
    setEditedCells([...storyboard.cells]);
  }, [storyboard]);

  const handleCellChange = (index: number, field: keyof StoryboardCell, value: string | number) => {
    const newCells = [...editedCells];
    newCells[index] = {
      ...newCells[index],
      [field]: value,
    };
    setEditedCells(newCells);
  };

  const handleSave = () => {
    const updatedStoryboard: StoryboardTable = {
      ...storyboard,
      cells: editedCells,
    };
    onSave(updatedStoryboard);
  };

  return (
    <div className="storyboard-page-overlay" onClick={onClose}>
      <div className="storyboard-page-container" onClick={(e) => e.stopPropagation()}>
        <div className="storyboard-page-header">
          <h2>分镜表编辑</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="storyboard-page-content">
          <div className="table-wrapper">
            <table className="storyboard-table">
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
                {editedCells.map((cell, index) => (
                  <tr key={index}>
                    <td className="shot-number">{cell.shot_number}</td>
                    <td className="scene-image">
                      {cell.scene_image ? (
                        <img src={cell.scene_image} alt={`Scene ${cell.shot_number}`} />
                      ) : (
                        <div className="no-image">暂无图片</div>
                      )}
                    </td>
                    <td>
                      <textarea
                        value={cell.scene_description}
                        onChange={(e) =>
                          handleCellChange(index, 'scene_description', e.target.value)
                        }
                        rows={3}
                      />
                    </td>
                    <td>
                      <textarea
                        value={cell.dialogue}
                        onChange={(e) => handleCellChange(index, 'dialogue', e.target.value)}
                        rows={3}
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        value={cell.main_character}
                        onChange={(e) =>
                          handleCellChange(index, 'main_character', e.target.value)
                        }
                      />
                    </td>
                    <td>
                      <input
                        type="range"
                        min="0"
                        max="10"
                        step="0.1"
                        value={cell.shooting_distance}
                        onChange={(e) =>
                          handleCellChange(index, 'shooting_distance', parseFloat(e.target.value))
                        }
                      />
                      <span className="slider-value">{cell.shooting_distance.toFixed(1)}</span>
                    </td>
                    <td>
                      <input
                        type="range"
                        min="0"
                        max="10"
                        step="0.1"
                        value={cell.dynamic_intensity}
                        onChange={(e) =>
                          handleCellChange(index, 'dynamic_intensity', parseFloat(e.target.value))
                        }
                      />
                      <span className="slider-value">{cell.dynamic_intensity.toFixed(1)}</span>
                    </td>
                    <td>
                      <input
                        type="range"
                        min="0"
                        max="10"
                        step="0.1"
                        value={cell.scene_atmosphere}
                        onChange={(e) =>
                          handleCellChange(index, 'scene_atmosphere', parseFloat(e.target.value))
                        }
                      />
                      <span className="slider-value">{cell.scene_atmosphere.toFixed(1)}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="storyboard-page-footer">
          <button className="btn-cancel" onClick={onClose}>
            取消
          </button>
          <button className="btn-save-storyboard" onClick={handleSave}>
            保存并生成视频
          </button>
        </div>
      </div>
    </div>
  );
};

export default StoryboardPage;
