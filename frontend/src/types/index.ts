export interface ModelConfig {
  anime_mode: 'blackwhite' | 'color' | 'illustration';
  era: 'ancient' | 'medieval' | 'renaissance' | 'industrial' | 'modern' | 'future' | 'cyberpunk' | 'fantasy';
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
  video_format: 'mp4' | 'avi' | 'mkv' | 'mov';
  resolution: '720p' | '1080p' | '1440p' | '4k';
  frame_rate: 24 | 30 | 60;
  bitrate: string;
}

export interface NovelInputData {
  text: string;
  file?: File;
}
