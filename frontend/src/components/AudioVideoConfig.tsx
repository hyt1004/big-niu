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
      <h3 className="panel-title">音视频配置</h3>
      
      <div className="config-section">
        <h4 className="section-subtitle">音频配置</h4>
        <div className="config-grid-4">
          <div className="config-item">
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
            <select
              value={config.sample_rate}
              onChange={(e) => handleChange('sample_rate', parseInt(e.target.value))}
            >
              <option value="16000">16000 Hz</option>
              <option value="32000">32000 Hz</option>
              <option value="44100">44100 Hz</option>
              <option value="48000">48000 Hz</option>
            </select>
          </div>

          <div className="config-item">
            <select
              value={config.channels}
              onChange={(e) => handleChange('channels', e.target.value)}
            >
              <option value="mono">单声道</option>
              <option value="stereo">双声道</option>
            </select>
          </div>

          <div className="config-item">
            <div className="slider-container">
              <label>码率(kbps): {config.audio_bitrate}</label>
              <input
                type="range"
                min="64"
                max="256"
                step="32"
                value={config.audio_bitrate}
                onChange={(e) => handleChange('audio_bitrate', parseInt(e.target.value))}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="config-section">
        <h4 className="section-subtitle">视频配置</h4>
        <div className="config-grid-4">
          <div className="config-item">
            <select
              value={config.video_format}
              onChange={(e) => handleChange('video_format', e.target.value)}
            >
              <option value="mp4">MP4</option>
              <option value="avi">AVI</option>
              <option value="mov">MOV</option>
              <option value="mkv">MKV</option>
              <option value="webm">WEBM</option>
            </select>
          </div>

          <div className="config-item">
            <select
              value={config.resolution}
              onChange={(e) => handleChange('resolution', e.target.value)}
            >
              <option value="720p">720p</option>
              <option value="1080p">1080p</option>
            </select>
          </div>

          <div className="config-item">
            <select
              value={config.frame_rate}
              onChange={(e) => handleChange('frame_rate', parseInt(e.target.value))}
            >
              <option value="25">25 fps</option>
              <option value="30">30 fps</option>
            </select>
          </div>

          <div className="config-item">
            <div className="slider-container">
              <label>码率(kbps): {config.video_bitrate}</label>
              <input
                type="range"
                min="500"
                max="10000"
                step="100"
                value={config.video_bitrate}
                onChange={(e) => handleChange('video_bitrate', parseInt(e.target.value))}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AudioVideoConfig;
