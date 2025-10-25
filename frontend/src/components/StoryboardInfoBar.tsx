import React from 'react';
import { StoryboardTable } from '../types';
import './StoryboardInfoBar.css';

interface StoryboardInfoBarProps {
  storyboard: StoryboardTable | null;
  loading: boolean;
  onExpand: () => void;
  onSubmit: () => void;
}

const StoryboardInfoBar: React.FC<StoryboardInfoBarProps> = ({
  storyboard,
  loading,
  onExpand,
  onSubmit,
}) => {
  if (!storyboard && !loading) return null;

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
              <th>画面描述</th>
              <th>台词</th>
              <th>主要角色</th>
              <th>拍摄距离</th>
              <th>动态强度</th>
              <th>画面氛围</th>
            </tr>
          </thead>
          <tbody>
            {storyboard?.cells.slice(0, 3).map((cell, index) => (
              <tr key={index}>
                <td>{cell.shot_number}</td>
                <td className="description-cell">{cell.scene_description}</td>
                <td className="dialogue-cell">{cell.dialogue}</td>
                <td>{cell.main_character}</td>
                <td>{cell.shooting_distance}</td>
                <td>{cell.dynamic_intensity}</td>
                <td>{cell.scene_atmosphere}</td>
              </tr>
            ))}
            {(storyboard?.cells.length || 0) > 3 && (
              <tr className="more-rows">
                <td colSpan={7}>还有 {(storyboard?.cells.length || 0) - 3} 个镜头...</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="storyboard-actions">
        <button className="btn-expand" onClick={onExpand}>
          <span className="icon">🔍</span>
          放大查看
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
