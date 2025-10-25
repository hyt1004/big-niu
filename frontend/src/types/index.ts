export enum ConnectionStatus {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

export interface ClientInfo {
  client_id: string;
  status: ConnectionStatus;
  last_heartbeat?: string;
}

export interface StoryboardCell {
  shot_number: number;
  scene_image: string;
  scene_description: string;
  dialogue: string;
  main_character: string;
  shooting_distance: number;
  dynamic_intensity: number;
  scene_atmosphere: number;
}

export interface StoryboardTable {
  rows: number;
  columns: number;
  cells: StoryboardCell[];
}

export interface ModelConfig {
  anime_mode: 'blackwhite' | 'color' | 'illustration';
  era: 'medieval' | 'renaissance' | 'cold_war' | 'modern' | 'digital' | 'warring_states' | 'tang' | 'song';
  random_fine_tune: boolean;
  random_composition: boolean;
  random_shot: boolean;
  shot_direction: 'vertical' | 'horizontal';
  atmosphere: number;
  distance: number;
  realism: number;
  dynamic: number;
  characters: string[];
}

export interface AudioVideoConfig {
  audio_format: 'aac' | 'mp3' | 'wav' | 'm4a';
  sample_rate: 16000 | 32000 | 44100 | 48000;
  channels: 'mono' | 'stereo';
  audio_bitrate: number;
  video_format: 'mp4' | 'avi' | 'mkv' | 'mov' | 'webm';
  resolution: '720p' | '1080p';
  frame_rate: 25 | 30;
  video_bitrate: number;
}

export interface VideoStatus {
  status: 'pending' | 'processing' | 'completed' | 'error';
  url?: string;
  error?: string;
  progress?: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface NovelSubmitRequest {
  text: string;
  use_storyboard: boolean;
  prompt?: string;
}

export interface SessionStats {
  total_clients: number;
  active_clients: number;
  total_requests: number;
}

export type MessageType = 'success' | 'error' | 'info' | 'warning';

export interface Message {
  id: string;
  type: MessageType;
  content: string;
  duration?: number;
}

export interface NovelInputData {
  text: string;
  file?: File;
}
