import { useState } from 'react';
import NovelInput from './components/NovelInput';
import ModelConfig from './components/ModelConfig';
import VideoOutput from './components/VideoOutput';
import AudioVideoConfig from './components/AudioVideoConfig';
import { ModelConfig as ModelConfigType, AudioVideoConfig as AudioVideoConfigType } from './types';
import './App.css';

function App() {
  const [novelText, setNovelText] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoUrl] = useState<string>();
  
  const [modelConfig, setModelConfig] = useState<ModelConfigType>({
    anime_mode: 'color',
    era: 'modern',
    random_fine_tune: false,
    random_composition: false,
    random_shot: false,
    atmosphere: 0.5,
    distance: 0.5,
    realism: 0.5,
    dynamic: 0.5,
    characters: ['', '', '', '', '']
  });

  const [audioVideoConfig, setAudioVideoConfig] = useState<AudioVideoConfigType>({
    audio_format: 'aac',
    video_format: 'mp4',
    resolution: '1080p',
    frame_rate: 30,
    bitrate: '5000k'
  });

  const handleGenerate = async () => {
    if (!novelText.trim()) {
      alert('请输入小说文本');
      return;
    }

    setIsGenerating(true);
    
    try {
      console.log('生成配置:', {
        text: novelText,
        modelConfig,
        audioVideoConfig
      });
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      alert('功能开发中，后端 API 集成待完成');
    } catch (error) {
      console.error('生成失败:', error);
      alert('生成失败，请重试');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>智能动漫生成系统</h1>
      </header>
      
      <div className="app-content">
        <div className="left-column">
          <NovelInput
            onTextChange={setNovelText}
            onGenerate={handleGenerate}
          />
          <ModelConfig
            config={modelConfig}
            onChange={setModelConfig}
          />
        </div>
        
        <div className="right-column">
          <VideoOutput
            videoUrl={videoUrl}
            isGenerating={isGenerating}
          />
          <AudioVideoConfig
            config={audioVideoConfig}
            onChange={setAudioVideoConfig}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
