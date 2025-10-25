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
  StoryboardTable,
  StoryboardCell,
} from './types';
import './App.css';

function App() {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(ConnectionStatus.DISCONNECTED);
  const [clientId, setClientId] = useState<string | null>(null);
  const [novelText, setNovelText] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string>();
  const [showStoryboardPage, setShowStoryboardPage] = useState(false);
  
  const [showAudioVideoModal, setShowAudioVideoModal] = useState(false);
  const [showModelConfigModal, setShowModelConfigModal] = useState(false);
  
  const [toastMessage, setToastMessage] = useState<string>('');
  const [toastType, setToastType] = useState<'success' | 'error' | 'info' | 'warning'>('info');
  const [showToast, setShowToast] = useState(false);
  
  const [storyboardEnabled, setStoryboardEnabled] = useState(false);
  const [storyboardData, setStoryboardData] = useState<StoryboardTable | null>(null);
  const [storyboardLoading, setStoryboardLoading] = useState(false);
  const [storyboardSaving, setStoryboardSaving] = useState(false);
  const [isExampleStoryboard, setIsExampleStoryboard] = useState(false);
  
  const [currentStep, setCurrentStep] = useState(1);

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
        showMessage('客户端连接成功', 'success');
      } catch (error) {
        console.error('Failed to register client:', error);
        setConnectionStatus(ConnectionStatus.ERROR);
        showMessage('客户端连接失败', 'error');
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


  const showMessage = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
  };
  
  const hideToast = () => {
    setShowToast(false);
  };

  const handleStoryboardToggle = (enabled: boolean) => {
    setStoryboardEnabled(enabled);
    if (!enabled) {
      setStoryboardData(null);
    }
  };
  
  const handleStoryboardCellUpdate = (shotNumber: number, field: keyof StoryboardCell, value: any) => {
    if (!storyboardData) return;
    
    const updatedCells = storyboardData.cells.map(cell => 
      cell.shot_number === shotNumber ? { ...cell, [field]: value } : cell
    );
    
    setStoryboardData({
      ...storyboardData,
      cells: updatedCells
    });
  };
  
  const handleSaveStoryboard = async () => {
    if (!storyboardData) return;
    
    setStoryboardSaving(true);
    try {
      await apiService.saveStoryboard(storyboardData);
      showMessage('分镜表已保存', 'success');
    } catch (error) {
      showMessage('分镜表保存失败', 'error');
    } finally {
      setStoryboardSaving(false);
    }
  };

  const handleModelConfigSave = async (config: ModelConfigType) => {
    try {
      await apiService.saveModelConfig(config);
      showMessage('模型配置已保存', 'success');
      setShowModelConfigModal(false);
    } catch (error) {
      console.error('Failed to save model config:', error);
      showMessage('模型配置保存失败', 'error');
    }
  };
  
  const handleAudioVideoConfigSave = async (config: AudioVideoConfigType) => {
    try {
      await apiService.saveAudioVideoConfig(config);
      showMessage('音视频配置已保存', 'success');
      setShowAudioVideoModal(false);
    } catch (error) {
      console.error('Failed to save audio/video config:', error);
      showMessage('音视频配置保存失败', 'error');
    }
  };

  const handleGenerate = async () => {
    if (!novelText.trim()) {
      showMessage('请输入小说文本', 'warning');
      return;
    }
    
    setCurrentStep(2);
    setIsGenerating(true);
    
    try {
      await apiService.submitNovel({
        text: novelText,
        use_storyboard: storyboardEnabled,
      });

      showMessage('小说文本已提交', 'success');

      if (storyboardEnabled) {
        setStoryboardLoading(true);
        setCurrentStep(3);
        setTimeout(async () => {
          try {
            const data = await apiService.getStoryboard();
            if (data) {
              setStoryboardData(data);
              showMessage('分镜表已生成', 'success');
              setCurrentStep(4);
            }
          } catch (error) {
            console.error('Failed to get storyboard:', error);
            showMessage('分镜表生成失败', 'error');
          } finally {
            setStoryboardLoading(false);
          }
        }, 2000);
      } else {
        setCurrentStep(4);
        checkVideoStatus();
      }
    } catch (error) {
      console.error('Failed to submit novel:', error);
      showMessage('提交失败,请重试', 'error');
      setCurrentStep(1);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleStoryboardSubmit = async () => {
    if (!storyboardData) return;

    setShowStoryboardPage(false);
    setIsGenerating(true);
    setCurrentStep(5);

    try {
      await apiService.saveStoryboard(storyboardData);
      showMessage('分镜表已提交,开始生成视频', 'success');
      checkVideoStatus();
    } catch (error) {
      console.error('Failed to save storyboard:', error);
      showMessage('分镜表提交失败', 'error');
      setIsGenerating(false);
    }
  };

  const handleStoryboardPageSave = async (updatedStoryboard: StoryboardTable) => {
    setStoryboardData(updatedStoryboard);
    setShowStoryboardPage(false);
    setIsGenerating(true);
    setCurrentStep(5);

    try {
      await apiService.saveStoryboard(updatedStoryboard);
      showMessage('分镜表已保存,开始生成视频', 'success');
      checkVideoStatus();
    } catch (error) {
      console.error('Failed to save storyboard:', error);
      showMessage('分镜表保存失败', 'error');
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
          showMessage('视频生成完成', 'success');
          setCurrentStep(6);
          clearInterval(interval);
        } else if (status?.status === 'error') {
          setIsGenerating(false);
          showMessage('视频生成失败: ' + (status.error || '未知错误'), 'error');
          setCurrentStep(1);
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
          <div className="header-title">
            <h1>智能动漫生成系统</h1>
            <p className="app-subtitle">将小说文本智能转换为动漫视频</p>
          </div>
          <div className="connection-status">
            <div className={`status-indicator ${connectionStatus.toLowerCase()}`}>
              <div className="status-dot"></div>
              <span className="status-text">
                {connectionStatus === ConnectionStatus.CONNECTED && '已连接'}
                {connectionStatus === ConnectionStatus.CONNECTING && '连接中'}
                {connectionStatus === ConnectionStatus.DISCONNECTED && '已断开'}
                {connectionStatus === ConnectionStatus.RECONNECTING && '重连中'}
                {connectionStatus === ConnectionStatus.ERROR && '连接错误'}
              </span>
            </div>
            {clientId && (
              <div className="client-info">
                <div 
                  className="client-id-container"
                  style={{ position: 'relative', display: 'inline-block' }}
                >
                  <span 
                    className="client-id" 
                    style={{ 
                      cursor: 'help', 
                      borderBottom: '1px dotted #ccc',
                      position: 'relative'
                    }}
                    onMouseEnter={(e) => {
                      const tooltip = document.createElement('div');
                      tooltip.id = 'client-id-tooltip';
                      tooltip.textContent = clientId;
                      tooltip.style.cssText = `
                        position: fixed;
                        background: #333;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 4px;
                        font-size: 12px;
                        white-space: nowrap;
                        z-index: 1000;
                        pointer-events: none;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                        max-width: 90vw;
                        word-break: break-all;
                      `;
                      
                      const rect = e.currentTarget.getBoundingClientRect();
                      const tooltipWidth = Math.min(300, clientId.length * 8);
                      const tooltipHeight = 30;
                      
                      let left = rect.left;
                      let top = rect.top - tooltipHeight - 5;
                      
                      if (left + tooltipWidth > window.innerWidth) {
                        left = window.innerWidth - tooltipWidth - 10;
                      }
                      
                      if (left < 10) {
                        left = 10;
                      }
                      
                      if (top < 10) {
                        top = rect.bottom + 5;
                      }
                      
                      tooltip.style.left = `${left}px`;
                      tooltip.style.top = `${top}px`;
                      
                      document.body.appendChild(tooltip);
                    }}
                    onMouseLeave={() => {
                      const tooltip = document.getElementById('client-id-tooltip');
                      if (tooltip) {
                        tooltip.remove();
                      }
                    }}
                  >
                    ID: {clientId.substring(0, 8)}...
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="app-content">
        <div className="control-panel">
          <div className="panel-header">
            <h2 className="panel-title">AI 创作控制台</h2>
            <p className="panel-subtitle">专业级小说转视频工具</p>
          </div>
          
          <div className="config-section">
            <div className="section-header">
              <h3 className="section-title">参数配置</h3>
              <div className="section-divider"></div>
            </div>
            
            <div className="config-buttons">
              <button 
                className="config-btn audio-video-btn"
                onClick={() => setShowAudioVideoModal(true)}
              >
                <span className="btn-icon">🎵</span>
                <div className="btn-content">
                  <span className="btn-title">音视频配置</span>
                  <span className="btn-subtitle">格式 · 采样率 · 码率</span>
                </div>
              </button>
              
              <button 
                className="config-btn model-btn"
                onClick={() => setShowModelConfigModal(true)}
              >
                <span className="btn-icon">⚙️</span>
                <div className="btn-content">
                  <span className="btn-title">模型配置</span>
                  <span className="btn-subtitle">风格 · 参数 · 角色</span>
                </div>
              </button>
            </div>
          </div>
          
          <div className="workflow-section">
            <div className="section-header">
              <h3 className="section-title">创作流程</h3>
              <div className="section-divider"></div>
            </div>
            <div className="workflow-steps">
              <div className={`workflow-step ${currentStep >= 1 ? 'active' : ''}`}>
                <div className="step-number">1</div>
                <div className="step-content">
                  <div className="step-title">输入文本</div>
                  <div className="step-desc">输入小说内容</div>
                </div>
              </div>
              <div className={`workflow-step ${currentStep >= 2 ? 'active' : ''}`}>
                <div className="step-number">2</div>
                <div className="step-content">
                  <div className="step-title">AI 分析</div>
                  <div className="step-desc">智能解析场景</div>
                </div>
              </div>
              <div className={`workflow-step ${currentStep >= 3 ? 'active' : ''}`}>
                <div className="step-number">3</div>
                <div className="step-content">
                  <div className="step-title">生成视频</div>
                  <div className="step-desc">输出动漫视频</div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="example-section">
            <div className="section-header">
              <h3 className="section-title">分镜表示例</h3>
              <div className="section-divider"></div>
            </div>
            <button 
              className="example-btn"
              onClick={() => {
                setIsExampleStoryboard(true);
                setShowStoryboardPage(true);
              }}
            >
              <span className="example-icon">📋</span>
              <span className="example-text">查看分镜表示例</span>
            </button>
          </div>
        </div>
        
        <div className="workspace">
          <div className="workspace-header">
            <h2 className="workspace-title">创作工作台</h2>
            <div className="workspace-status">
              {isGenerating && <span className="generating-badge">生成中...</span>}
            </div>
          </div>
          
          <div className="workspace-content">
            <div className="input-section">
              <NovelInput
                onTextChange={setNovelText}
                onGenerate={handleGenerate}
                storyboardEnabled={storyboardEnabled}
                onStoryboardToggle={handleStoryboardToggle}
                storyboardData={storyboardData}
                storyboardLoading={storyboardLoading}
                onStoryboardCellUpdate={handleStoryboardCellUpdate}
                onSaveStoryboard={handleSaveStoryboard}
                onShowMessage={showMessage}
              />
            </div>
            
            <div className="output-section">
              <VideoOutput
                videoUrl={videoUrl}
                isGenerating={isGenerating}
              />
            </div>
          </div>
          
          {storyboardEnabled && storyboardData && (
            <div className="storyboard-bottom-section">
              <StoryboardInfoBar
                storyboard={storyboardData}
                loading={storyboardLoading}
                onExpand={() => {
                  setIsExampleStoryboard(false);
                  setShowStoryboardPage(true);
                }}
                onSubmit={handleStoryboardSubmit}
              />
            </div>
          )}
        </div>
      </div>

      {showModelConfigModal && (
        <div className="modal-overlay" onClick={() => setShowModelConfigModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <ModelConfig 
              config={modelConfig} 
              onChange={setModelConfig} 
              onSave={handleModelConfigSave}
              onShowMessage={showMessage}
            />
          </div>
        </div>
      )}

      {showAudioVideoModal && (
        <div className="modal-overlay" onClick={() => setShowAudioVideoModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <AudioVideoConfig 
              config={audioVideoConfig} 
              onChange={setAudioVideoConfig}
              onSave={handleAudioVideoConfigSave}
            />
          </div>
        </div>
      )}

      {showStoryboardPage && storyboardData && (
        <StoryboardPage
          storyboard={storyboardData}
          onClose={() => setShowStoryboardPage(false)}
          onSave={handleStoryboardPageSave}
        />
      )}

      {showToast && (
        <MessageToast
          message={toastMessage}
          type={toastType}
          onClose={hideToast}
        />
      )}
    </div>
  );
}

export default App;
