import React from 'react';
import './VideoOutput.css';

interface VideoOutputProps {
  videoUrl?: string;
  isGenerating: boolean;
}

const VideoOutput: React.FC<VideoOutputProps> = ({ videoUrl, isGenerating }) => {
  const handleDownload = () => {
    if (videoUrl) {
      const link = document.createElement('a');
      link.href = videoUrl;
      link.download = 'anime-video.mp4';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="video-output">
      <h3>视频输出</h3>
      <div className="video-container">
        {isGenerating ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>正在生成视频...</p>
          </div>
        ) : videoUrl ? (
          <video controls className="video-player">
            <source src={videoUrl} type="video/mp4" />
            您的浏览器不支持视频播放
          </video>
        ) : (
          <div className="placeholder">
            <p>视频将在此处显示</p>
          </div>
        )}
      </div>
      <div className="button-container">
        <button
          className="download-btn"
          onClick={handleDownload}
          disabled={!videoUrl || isGenerating}
        >
          下载视频
        </button>
      </div>
    </div>
  );
};

export default VideoOutput;
