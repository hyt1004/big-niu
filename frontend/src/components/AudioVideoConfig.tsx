import React from 'react';
import { AudioVideoConfig as AudioVideoConfigType } from '../types';
import './AudioVideoConfig.css';

interface AudioVideoConfigProps {
  config: AudioVideoConfigType;
  onChange: (config: AudioVideoConfigType) => void;
}

const AudioVideoConfig: React.FC<AudioVideoConfigProps> = ({ config, onChange }) => {
  const handleChange = (field: keyof AudioVideoConfigType, value: any) => {
    onChange({ ...config, [field]: value });
  };

  return (
    <div className="audio-video-config">
      <h3>音视频配置</h3>
      
      <div className="config-grid">
        <div className="config-item">
          <label>音频格式</label>
          <select
            value={config.audio_format}
            onChange={(e) => handleChange('audio_format', e.target.value)}
          >
            <option value="aac">AAC</option>
            <option value="mp3">MP3</option>
            <option value="wav">WAV</option>
            <option value="m4a">M4A</option>
          </select>
        </div>

        <div className="config-item">
          <label>视频格式</label>
          <select
            value={config.video_format}
            onChange={(e) => handleChange('video_format', e.target.value)}
          >
            <option value="mp4">MP4</option>
            <option value="avi">AVI</option>
            <option value="mkv">MKV</option>
            <option value="mov">MOV</option>
          </select>
        </div>

        <div className="config-item">
          <label>分辨率</label>
          <select
            value={config.resolution}
            onChange={(e) => handleChange('resolution', e.target.value)}
          >
            <option value="720p">720p</option>
            <option value="1080p">1080p</option>
            <option value="1440p">1440p</option>
            <option value="4k">4K</option>
          </select>
        </div>

        <div className="config-item">
          <label>帧率</label>
          <select
            value={config.frame_rate}
            onChange={(e) => handleChange('frame_rate', parseInt(e.target.value))}
          >
            <option value="24">24 fps</option>
            <option value="30">30 fps</option>
            <option value="60">60 fps</option>
          </select>
        </div>

        <div className="config-item full-width">
          <label>码率</label>
          <input
            type="text"
            value={config.bitrate}
            onChange={(e) => handleChange('bitrate', e.target.value)}
            placeholder="例如: 5000k"
          />
        </div>
      </div>
    </div>
  );
};

export default AudioVideoConfig;
