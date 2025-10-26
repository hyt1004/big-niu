import axios, { AxiosInstance } from 'axios';
import {
  ConnectionStatus,
  ClientInfo,
  ModelConfig,
  AudioVideoConfig,
  NovelSubmitRequest,
  StoryboardTable,
  VideoStatus,
  SessionStats,
  ApiResponse
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiService {
  private axiosInstance: AxiosInstance;
  private clientId: string | null = null;
  private heartbeatInterval: number | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 404 && error.config.url?.includes('/client/')) {
          await this.handleClientExpired();
        }
        return Promise.reject(error);
      }
    );
  }

  private async handleClientExpired(): Promise<void> {
    this.stopHeartbeat();
    this.clientId = null;
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      await this.registerClient();
    }
  }

  async registerClient(): Promise<ClientInfo> {
    try {
      const response = await this.axiosInstance.post<any>(
        '/api/v1/bigniu/client/register',
        { client_name: 'Big Niu Frontend' }
      );
      
      if (response.data.success) {
        this.clientId = response.data.client_id;
        this.reconnectAttempts = 0;
        this.startHeartbeat();
        return {
          client_id: response.data.client_id,
          status: ConnectionStatus.CONNECTED,
          last_heartbeat: response.data.created_at
        };
      }
      
      throw new Error(response.data.message || 'Failed to register client');
    } catch (error) {
      console.error('Failed to register client:', error);
      throw error;
    }
  }

  private startHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }

    this.heartbeatInterval = window.setInterval(() => {
      this.sendHeartbeat();
    }, 30000);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  async sendHeartbeat(): Promise<void> {
    if (!this.clientId) return;

    try {
      await this.axiosInstance.post(
        `/api/v1/bigniu/client/heartbeat/${this.clientId}`
      );
    } catch (error) {
      console.error('Heartbeat failed:', error);
    }
  }

  async checkClientStatus(): Promise<ConnectionStatus> {
    if (!this.clientId) return ConnectionStatus.DISCONNECTED;

    try {
      const response = await this.axiosInstance.get<ApiResponse<ClientInfo>>(
        `/api/v1/bigniu/client/status/${this.clientId}`
      );
      
      if (response.data.success && response.data.data) {
        return response.data.data.status;
      }
      
      return ConnectionStatus.ERROR;
    } catch (error) {
      console.error('Failed to check client status:', error);
      return ConnectionStatus.ERROR;
    }
  }

  async getSessionStats(): Promise<SessionStats | null> {
    try {
      const response = await this.axiosInstance.get<ApiResponse<SessionStats>>(
        '/api/v1/bigniu/client/stats'
      );
      
      return response.data.success ? response.data.data || null : null;
    } catch (error) {
      console.error('Failed to get session stats:', error);
      return null;
    }
  }

  async saveModelConfig(config: ModelConfig): Promise<boolean> {
    if (!this.clientId) throw new Error('Client not registered');

    try {
      const response = await this.axiosInstance.post<ApiResponse>(
        `/api/v1/bigniu/config/model/${this.clientId}`,
        config
      );
      
      return response.data.success;
    } catch (error) {
      console.error('Failed to save model config:', error);
      return false;
    }
  }

  async getModelConfig(): Promise<ModelConfig | null> {
    if (!this.clientId) throw new Error('Client not registered');

    try {
      const response = await this.axiosInstance.get<ApiResponse<ModelConfig>>(
        `/api/v1/bigniu/config/model/${this.clientId}`
      );
      
      return response.data.success ? response.data.data || null : null;
    } catch (error) {
      console.error('Failed to get model config:', error);
      return null;
    }
  }

  async saveAudioVideoConfig(config: AudioVideoConfig): Promise<boolean> {
    if (!this.clientId) throw new Error('Client not registered');

    try {
      const response = await this.axiosInstance.post<ApiResponse>(
        `/api/v1/bigniu/config/audiovideo/${this.clientId}`,
        config
      );
      
      return response.data.success;
    } catch (error) {
      console.error('Failed to save audio/video config:', error);
      return false;
    }
  }

  async getAudioVideoConfig(): Promise<AudioVideoConfig | null> {
    if (!this.clientId) throw new Error('Client not registered');

    try {
      const response = await this.axiosInstance.get<ApiResponse<AudioVideoConfig>>(
        `/api/v1/bigniu/config/audiovideo/${this.clientId}`
      );
      
      return response.data.success ? response.data.data || null : null;
    } catch (error) {
      console.error('Failed to get audio/video config:', error);
      return null;
    }
  }

  async submitNovel(request: NovelSubmitRequest): Promise<boolean> {
    if (!this.clientId) throw new Error('Client not registered');

    try {
      const response = await this.axiosInstance.post<ApiResponse>(
        `/api/v1/bigniu/novel/submit/${this.clientId}`,
        request
      );
      
      return response.data.success;
    } catch (error) {
      console.error('Failed to submit novel:', error);
      throw error;
    }
  }

  async getStoryboard(): Promise<StoryboardTable | null> {
    if (!this.clientId) throw new Error('Client not registered');

    try {
      const response = await this.axiosInstance.get<ApiResponse<StoryboardTable>>(
        `/api/v1/bigniu/storyboard/${this.clientId}`
      );
      
      return response.data.success ? response.data.data || null : null;
    } catch (error) {
      console.error('Failed to get storyboard:', error);
      return null;
    }
  }

  async getStoryboardExamples(): Promise<any[]> {
    try {
      const response = await this.axiosInstance.get<any>(
        '/api/v1/bigniu/storyboard/examples'
      );
      
      return response.data.success ? response.data.examples || [] : [];
    } catch (error) {
      console.error('Failed to get storyboard examples:', error);
      return [];
    }
  }

  async saveStoryboard(storyboard: StoryboardTable): Promise<boolean> {
    if (!this.clientId) throw new Error('Client not registered');

    try {
      const response = await this.axiosInstance.post<ApiResponse>(
        `/api/v1/bigniu/storyboard/${this.clientId}`,
        storyboard
      );
      
      return response.data.success;
    } catch (error) {
      console.error('Failed to save storyboard:', error);
      throw error;
    }
  }

  async getVideoStatus(): Promise<VideoStatus | null> {
    if (!this.clientId) throw new Error('Client not registered');

    try {
      const response = await this.axiosInstance.get<ApiResponse<VideoStatus>>(
        `/api/v1/bigniu/video/status/${this.clientId}`
      );
      
      return response.data.success ? response.data.data || null : null;
    } catch (error) {
      console.error('Failed to get video status:', error);
      return null;
    }
  }

  async downloadVideo(): Promise<Blob | null> {
    if (!this.clientId) throw new Error('Client not registered');

    try {
      const response = await this.axiosInstance.get(
        `/api/v1/bigniu/video/download/${this.clientId}`,
        { responseType: 'blob' }
      );
      
      return response.data;
    } catch (error) {
      console.error('Failed to download video:', error);
      return null;
    }
  }

  async getTestVideo(): Promise<string> {
    try {
      const response = await this.axiosInstance.get<ApiResponse<{ url: string }>>(
        '/api/v1/bigniu/video/test'
      );
      
      if (response.data.success && response.data.data) {
        return response.data.data.url;
      }
      
      return '';
    } catch (error) {
      console.error('Failed to get test video:', error);
      return '';
    }
  }

  getClientId(): string | null {
    return this.clientId;
  }

  disconnect(): void {
    this.stopHeartbeat();
    this.clientId = null;
  }
}

export default new ApiService();
