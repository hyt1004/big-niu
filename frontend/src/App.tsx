import { useState, useEffect } from 'react';
import NovelInput from './components/NovelInput';
import ModelConfig from './components/ModelConfig';
import VideoOutput from './components/VideoOutput';
import AudioVideoConfig from './components/AudioVideoConfig';
import MessageToast from './components/MessageToast';
import StoryboardInfoBar from './components/StoryboardInfoBar';
import StoryboardPage from './components/StoryboardPage';
import apiService from './services/api';
import {
  ModelConfig as ModelConfigType,
  AudioVideoConfig as AudioVideoConfigType,
  ConnectionStatus,
  Message,
  StoryboardTable,
} from './types';
import './App.css';

function App() {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(ConnectionStatus.DISCONNECTED);
  const [clientId, setClientId] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [storyboard, setStoryboard] = useState<StoryboardTable | null>(null);
  const [isLoadingStoryboard, setIsLoadingStoryboard] = useState(false);
  const [showStoryboardPage, setShowStoryboardPage] = useState(false);

  const [modelConfig, setModelConfig] = useState<ModelConfigType>({
    anime_mode: 'color',
    era: 'modern',
    random_fine_tune: false,
    random_composition: false,
    random_shot: false,
    shot_direction: 'horizontal',
    atmosphere: 0.5,
    distance: 0.5,
    realism: 0.5,
    dynamic: 0.5,
    characters: ['', ''],
  });

  const [audioVideoConfig, setAudioVideoConfig] = useState<AudioVideoConfigType>({
    audio_format: 'aac',
    sample_rate: 44100,
    channels: 'stereo',
    audio_bitrate: 128,
    video_format: 'mp4',
    resolution: '720p',
    frame_rate: 25,
    video_bitrate: 2000,
  });

  useEffect(() => {
    const initializeClient = async () => {
      setConnectionStatus(ConnectionStatus.CONNECTING);
      try {
        const client = await apiService.registerClient();
        setClientId(client.client_id);
        setConnectionStatus(ConnectionStatus.CONNECTED);
        addMessage('success', '客户端连接成功');
      } catch (error) {
        console.error('Failed to register client:', error);
        setConnectionStatus(ConnectionStatus.ERROR);
        addMessage('error', '客户端连接失败');
      }
    };

    initializeClient();

    const handleVisibilityChange = () => {
      if (document.hidden) {
        apiService.disconnect();
      } else {
        initializeClient();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      apiService.disconnect();
    };
  }, []);

  useEffect(() => {
    const newPrompt = generatePrompt();
    setPrompt(newPrompt);
  }, [modelConfig]);

  const generatePrompt = (): string => {
    const { anime_mode, era, atmosphere, distance, realism, dynamic, characters } = modelConfig;
    const characterDesc = characters.filter((c) => c.trim()).join(', ');
    return `模式:${anime_mode}|时代:${era}|气氛:${atmosphere}|距离:${distance}|写实:${realism}|动态:${dynamic}|角色:${characterDesc}`;
  };

  const addMessage = (type: Message['type'], content: string) => {
    const message: Message = {
      id: Date.now().toString(),
      type,
      content,
      duration: 3000,
    };
    setMessages((prev) => [...prev, message]);
  };

  const removeMessage = (id: string) => {
    setMessages((prev) => prev.filter((msg) => msg.id !== id));
  };

  const handleModelConfigSave = async (config: ModelConfigType) => {
    try {
      await apiService.saveModelConfig(config);
      addMessage('success', '模型配置已保存');
    } catch (error) {
      console.error('Failed to save model config:', error);
      addMessage('error', '模型配置保存失败');
    }
  };

  const handleNovelSubmit = async (text: string, useStoryboard: boolean) => {
    if (!text.trim()) {
      addMessage('warning', '请输入小说文本');
      return;
    }

    setIsGenerating(true);
    try {
      await apiService.submitNovel({
        text,
        use_storyboard: useStoryboard,
        prompt,
      });

      addMessage('success', '小说文本已提交');

      if (useStoryboard) {
        setIsLoadingStoryboard(true);
        setTimeout(async () => {
          try {
            const storyboardData = await apiService.getStoryboard();
            if (storyboardData) {
              setStoryboard(storyboardData);
              addMessage('success', '分镜表已生成');
            }
          } catch (error) {
            console.error('Failed to get storyboard:', error);
            addMessage('error', '分镜表生成失败');
          } finally {
            setIsLoadingStoryboard(false);
          }
        }, 2000);
      } else {
        checkVideoStatus();
      }
    } catch (error) {
      console.error('Failed to submit novel:', error);
      addMessage('error', '提交失败,请重试');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleStoryboardSubmit = async () => {
    if (!storyboard) return;

    setShowStoryboardPage(false);
    setIsGenerating(true);

    try {
      await apiService.saveStoryboard(storyboard);
      addMessage('success', '分镜表已提交,开始生成视频');
      checkVideoStatus();
    } catch (error) {
      console.error('Failed to save storyboard:', error);
      addMessage('error', '分镜表提交失败');
      setIsGenerating(false);
    }
  };

  const handleStoryboardSave = async (updatedStoryboard: StoryboardTable) => {
    setStoryboard(updatedStoryboard);
    setShowStoryboardPage(false);
    setIsGenerating(true);

    try {
      await apiService.saveStoryboard(updatedStoryboard);
      addMessage('success', '分镜表已保存,开始生成视频');
      checkVideoStatus();
    } catch (error) {
      console.error('Failed to save storyboard:', error);
      addMessage('error', '分镜表保存失败');
      setIsGenerating(false);
    }
  };

  const checkVideoStatus = () => {
    const interval = setInterval(async () => {
      try {
        const status = await apiService.getVideoStatus();
        if (status?.status === 'completed' && status.url) {
          setVideoUrl(status.url);
          setIsGenerating(false);
          addMessage('success', '视频生成完成');
          clearInterval(interval);
        } else if (status?.status === 'error') {
          setIsGenerating(false);
          addMessage('error', '视频生成失败: ' + (status.error || '未知错误'));
          clearInterval(interval);
        }
      } catch (error) {
        console.error('Failed to check video status:', error);
      }
    }, 3000);

    setTimeout(() => clearInterval(interval), 120000);
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case ConnectionStatus.CONNECTING:
        return '连接中...';
      case ConnectionStatus.CONNECTED:
        return '已连接';
      case ConnectionStatus.DISCONNECTED:
        return '已断开';
      case ConnectionStatus.RECONNECTING:
        return '重连中...';
      case ConnectionStatus.ERROR:
        return '连接错误';
      default:
        return '未知';
    }
  };

  const getConnectionStatusClass = () => {
    switch (connectionStatus) {
      case ConnectionStatus.CONNECTED:
        return 'status-connected';
      case ConnectionStatus.CONNECTING:
      case ConnectionStatus.RECONNECTING:
        return 'status-connecting';
      default:
        return 'status-error';
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>智能动漫生成系统</h1>
          <div className="header-info">
            <div className={`connection-status ${getConnectionStatusClass()}`}>
              <span className="status-dot"></span>
              <span>{getConnectionStatusText()}</span>
            </div>
            {clientId && <div className="client-id">ID: {clientId.substring(0, 8)}</div>}
          </div>
        </div>
      </header>

      <div className="app-content">
        <div className="left-panel">
          <NovelInput
            onTextChange={() => {}}
            onSubmit={handleNovelSubmit}
            onPromptChange={setPrompt}
            prompt={prompt}
          />
          <ModelConfig config={modelConfig} onChange={setModelConfig} onSave={handleModelConfigSave} />
          <AudioVideoConfig config={audioVideoConfig} onChange={setAudioVideoConfig} />
        </div>

        <div className="right-panel">
          <VideoOutput videoUrl={videoUrl} isGenerating={isGenerating} />
          <StoryboardInfoBar
            storyboard={storyboard}
            loading={isLoadingStoryboard}
            onExpand={() => setShowStoryboardPage(true)}
            onSubmit={handleStoryboardSubmit}
          />
        </div>
      </div>

      {showStoryboardPage && storyboard && (
        <StoryboardPage
          storyboard={storyboard}
          onClose={() => setShowStoryboardPage(false)}
          onSave={handleStoryboardSave}
        />
      )}

      <div className="messages-container">
        {messages.map((message) => (
          <MessageToast key={message.id} message={message} onClose={removeMessage} />
        ))}
      </div>
    </div>
  );
}

export default App;
