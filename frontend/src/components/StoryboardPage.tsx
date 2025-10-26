import React, { useState, useEffect } from 'react';
import { StoryboardTable, StoryboardCell } from '../types';
import './StoryboardPage.css';

interface StoryboardPageProps {
  storyboard: StoryboardTable;
  onClose: () => void;
  onSave: (storyboard: StoryboardTable) => void;
  isExample?: boolean;
}

const StoryboardPage: React.FC<StoryboardPageProps> = ({
  storyboard,
  onClose,
  onSave,
  isExample = false,
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
          <h2>{isExample ? '分镜表示例' : '分镜表编辑'}</h2>
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
                      {isExample ? (
                        <div className="readonly-text">{cell.scene_description}</div>
                      ) : (
                        <textarea
                          value={cell.scene_description}
                          onChange={(e) =>
                            handleCellChange(index, 'scene_description', e.target.value)
                          }
                          rows={3}
                        />
                      )}
                    </td>
                    <td>
                      {isExample ? (
                        <div className="readonly-text">{cell.dialogue}</div>
                      ) : (
                        <textarea
                          value={cell.dialogue}
                          onChange={(e) => handleCellChange(index, 'dialogue', e.target.value)}
                          rows={3}
                        />
                      )}
                    </td>
                    <td>
                      {isExample ? (
                        <div className="readonly-text">{cell.main_character}</div>
                      ) : (
                        <input
                          type="text"
                          value={cell.main_character}
                          onChange={(e) =>
                            handleCellChange(index, 'main_character', e.target.value)
                          }
                        />
                      )}
                    </td>
                    <td>
                      {isExample ? (
                        <div className="readonly-number">{cell.shooting_distance.toFixed(1)}</div>
                      ) : (
                        <div className="number-control">
                          <button
                            type="button"
                            className="number-btn number-btn-minus"
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
                            className="number-input"
                          />
                          <button
                            type="button"
                            className="number-btn number-btn-plus"
                            onClick={() => {
                              const newValue = Math.min(1, cell.shooting_distance + 0.1);
                              handleCellChange(index, 'shooting_distance', parseFloat(newValue.toFixed(1)));
                            }}
                          >
                            +
                          </button>
                        </div>
                      )}
                    </td>
                    <td>
                      {isExample ? (
                        <div className="readonly-number">{cell.dynamic_intensity.toFixed(1)}</div>
                      ) : (
                        <div className="number-control">
                          <button
                            type="button"
                            className="number-btn number-btn-minus"
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
                            className="number-input"
                          />
                          <button
                            type="button"
                            className="number-btn number-btn-plus"
                            onClick={() => {
                              const newValue = Math.min(1, cell.dynamic_intensity + 0.1);
                              handleCellChange(index, 'dynamic_intensity', parseFloat(newValue.toFixed(1)));
                            }}
                          >
                            +
                          </button>
                        </div>
                      )}
                    </td>
                    <td>
                      {isExample ? (
                        <div className="readonly-number">{cell.scene_atmosphere.toFixed(1)}</div>
                      ) : (
                        <div className="number-control">
                          <button
                            type="button"
                            className="number-btn number-btn-minus"
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
                            className="number-input"
                          />
                          <button
                            type="button"
                            className="number-btn number-btn-plus"
                            onClick={() => {
                              const newValue = Math.min(1, cell.scene_atmosphere + 0.1);
                              handleCellChange(index, 'scene_atmosphere', parseFloat(newValue.toFixed(1)));
                            }}
                          >
                            +
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="storyboard-page-footer">
          <button className="btn-cancel" onClick={onClose}>
            {isExample ? '关闭' : '取消'}
          </button>
          {!isExample && (
            <button className="btn-save-storyboard" onClick={handleSave}>
              保存
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default StoryboardPage;
