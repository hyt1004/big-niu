export interface ModelConfig {
  anime_mode: 'blackwhite' | 'color' | 'illustration';
  era: 'medieval' | 'renaissance' | 'cold_war' | 'modern' | 'digital' | 'warring_states' | 'tang' | 'song';
  random_fine_tune: boolean;
  random_composition: boolean;
  random_shot: boolean;
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

export interface NovelInputData {
  text: string;
  file?: File;
}
