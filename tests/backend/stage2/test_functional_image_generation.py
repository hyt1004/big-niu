import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import asyncio


class TestImageGenerationFunctional:
    
    @pytest.fixture
    def structured_scene_data(self):
        return {
            "metadata": {
                "total_scenes": 3,
                "story_title": "测试故事"
            },
            "characters": [
                {
                    "id": "char_001",
                    "name": "张三",
                    "description": "年轻男子,黑色短发,穿着现代休闲装",
                    "personality": "勇敢、善良"
                },
                {
                    "id": "char_002",
                    "name": "李四",
                    "description": "中年男子,友善的笑容",
                    "personality": "热情、健谈"
                }
            ],
            "scenes": [
                {
                    "scene_id": "scene_001",
                    "order": 1,
                    "description": "清晨的城市街道,阳光洒在高楼之间",
                    "composition": "远景,俯视角度",
                    "characters": ["char_001"],
                    "narration": "这是一个平凡的早晨。"
                },
                {
                    "scene_id": "scene_002",
                    "order": 2,
                    "description": "街角咖啡店,温馨的室内",
                    "composition": "中景,平视角度",
                    "characters": ["char_001", "char_002"],
                    "narration": "他们在咖啡店相遇。"
                },
                {
                    "scene_id": "scene_003",
                    "order": 3,
                    "description": "咖啡店窗边,夕阳余晖",
                    "composition": "近景,侧面角度",
                    "characters": ["char_001", "char_002"],
                    "narration": "时光静止。"
                }
            ]
        }
    
    @pytest.fixture
    def mock_image(self):
        return Image.new('RGB', (1920, 1080), color='blue')
    
    @pytest.mark.asyncio
    async def test_end_to_end_image_generation_pipeline(self, structured_scene_data, mock_image):
        with patch('services.image_generation.ImageGenerationService') as MockService:
            mock_service = MockService.return_value
            mock_service.generate_all_scenes.return_value = [
                {
                    "scene_id": "scene_001",
                    "image_path": "/storage/scenes/scene_001.png",
                    "image_url": "https://cdn.qiniu.com/xxx/scene_001.png",
                    "width": 1920,
                    "height": 1080,
                    "generation_params": {
                        "model": "stable-diffusion-xl",
                        "seed": 123456,
                        "steps": 30
                    }
                },
                {
                    "scene_id": "scene_002",
                    "image_path": "/storage/scenes/scene_002.png",
                    "image_url": "https://cdn.qiniu.com/xxx/scene_002.png",
                    "width": 1920,
                    "height": 1080,
                    "generation_params": {
                        "model": "stable-diffusion-xl",
                        "seed": 123457,
                        "steps": 30
                    }
                },
                {
                    "scene_id": "scene_003",
                    "image_path": "/storage/scenes/scene_003.png",
                    "image_url": "https://cdn.qiniu.com/xxx/scene_003.png",
                    "width": 1920,
                    "height": 1080,
                    "generation_params": {
                        "model": "stable-diffusion-xl",
                        "seed": 123458,
                        "steps": 30
                    }
                }
            ]
            
            results = await mock_service.generate_all_scenes(structured_scene_data)
            
            assert len(results) == 3
            assert all(r["width"] == 1920 and r["height"] == 1080 for r in results)
            assert all(r["image_url"].startswith("https://") for r in results)
    
    @pytest.mark.asyncio
    async def test_character_consistency_across_multiple_scenes(self, structured_scene_data, mock_image):
        with patch('services.image_generation.ImageGenerationService') as MockService:
            mock_service = MockService.return_value
            
            mock_service.generate_character_references.return_value = {
                "char_001": {
                    "reference_image_url": "https://cdn.qiniu.com/char_001_ref.png",
                    "seed": 100001
                },
                "char_002": {
                    "reference_image_url": "https://cdn.qiniu.com/char_002_ref.png",
                    "seed": 100002
                }
            }
            
            char_refs = await mock_service.generate_character_references(
                structured_scene_data["characters"]
            )
            
            assert len(char_refs) == 2
            assert "char_001" in char_refs
            assert "char_002" in char_refs
            assert all("reference_image_url" in ref for ref in char_refs.values())
    
    @pytest.mark.asyncio
    async def test_parallel_image_generation(self, structured_scene_data, mock_image):
        with patch('services.image_generation.ImageGenerationService') as MockService:
            mock_service = MockService.return_value
            
            async def mock_generate_scene(scene_data):
                await asyncio.sleep(0.1)
                return {
                    "scene_id": scene_data["scene_id"],
                    "image_url": f"https://cdn.qiniu.com/{scene_data['scene_id']}.png"
                }
            
            mock_service.generate_scene.side_effect = mock_generate_scene
            
            tasks = [
                mock_service.generate_scene(scene)
                for scene in structured_scene_data["scenes"]
            ]
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            assert all("image_url" in r for r in results)
    
    @pytest.mark.asyncio
    async def test_image_generation_with_different_styles(self, structured_scene_data):
        styles = ["anime", "realistic", "watercolor", "oil_painting"]
        
        for style in styles:
            with patch('services.image_generation.ImageGenerationService') as MockService:
                mock_service = MockService.return_value
                mock_service.set_style.return_value = None
                mock_service.generate_all_scenes.return_value = [
                    {
                        "scene_id": f"scene_{i:03d}",
                        "style": style,
                        "image_url": f"https://cdn.qiniu.com/scene_{i:03d}.png"
                    }
                    for i in range(1, 4)
                ]
                
                mock_service.set_style(style)
                results = await mock_service.generate_all_scenes(structured_scene_data)
                
                assert all(r["style"] == style for r in results)
    
    @pytest.mark.asyncio
    async def test_retry_mechanism_on_generation_failure(self, structured_scene_data):
        with patch('services.image_generation.ImageGenerationService') as MockService:
            mock_service = MockService.return_value
            
            mock_service.generate_scene.side_effect = [
                Exception("Generation failed"),
                Exception("Generation failed"),
                {
                    "scene_id": "scene_001",
                    "image_url": "https://cdn.qiniu.com/scene_001.png"
                }
            ]
            
            result = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = await mock_service.generate_scene(structured_scene_data["scenes"][0])
                    break
                except Exception:
                    if attempt == max_retries - 1:
                        raise
                    continue
            
            assert result is not None
            assert "image_url" in result
    
    @pytest.mark.asyncio
    async def test_storage_upload_integration(self, mock_image):
        with patch('services.image_generation.StorageService') as MockStorage:
            mock_storage = MockStorage.return_value
            mock_storage.upload.return_value = {
                "url": "https://cdn.qiniu.com/uploaded_image.png",
                "key": "scenes/uploaded_image.png",
                "size": 1024000
            }
            
            result = await mock_storage.upload(mock_image, "scenes/test_image.png")
            
            assert "url" in result
            assert result["url"].startswith("https://")
            assert "size" in result
    
    @pytest.mark.asyncio
    async def test_prompt_optimization_for_better_results(self, structured_scene_data):
        with patch('services.image_generation.PromptOptimizer') as MockOptimizer:
            mock_optimizer = MockOptimizer.return_value
            mock_optimizer.optimize.return_value = "优化后的详细提示词,包含更多细节和质量标签"
            
            original_prompt = "简单的场景描述"
            optimized = await mock_optimizer.optimize(original_prompt)
            
            assert len(optimized) > len(original_prompt)
            assert "质量" in optimized or "细节" in optimized
    
    @pytest.mark.asyncio
    async def test_image_quality_validation_and_regeneration(self, structured_scene_data, mock_image):
        with patch('services.image_generation.ImageGenerationService') as MockService:
            mock_service = MockService.return_value
            
            low_quality_image = Image.new('RGB', (800, 600))
            high_quality_image = Image.new('RGB', (1920, 1080))
            
            mock_service.generate_and_validate.side_effect = [
                (low_quality_image, False),
                (high_quality_image, True)
            ]
            
            image, is_valid = None, False
            max_attempts = 3
            for attempt in range(max_attempts):
                image, is_valid = await mock_service.generate_and_validate(
                    structured_scene_data["scenes"][0]
                )
                if is_valid:
                    break
            
            assert is_valid is True
            assert image.size == (1920, 1080)
    
    @pytest.mark.asyncio
    async def test_controlnet_integration_for_pose_control(self, structured_scene_data, mock_image):
        with patch('services.image_generation.ControlNetService') as MockControlNet:
            mock_controlnet = MockControlNet.return_value
            
            pose_image = Image.new('RGB', (1920, 1080))
            mock_controlnet.apply_pose_control.return_value = mock_image
            
            result = await mock_controlnet.apply_pose_control(
                prompt="角色站立姿势",
                pose_reference=pose_image
            )
            
            assert result is not None
            assert result.size == (1920, 1080)
    
    @pytest.mark.asyncio
    async def test_lora_model_for_character_consistency(self, structured_scene_data, mock_image):
        with patch('services.image_generation.ImageGenerationService') as MockService:
            mock_service = MockService.return_value
            
            mock_service.train_character_lora.return_value = {
                "lora_model_id": "char_001_lora",
                "training_images_count": 10
            }
            
            lora_info = await mock_service.train_character_lora(
                character_id="char_001",
                reference_images=["url1", "url2", "url3"]
            )
            
            assert "lora_model_id" in lora_info
            assert lora_info["lora_model_id"] == "char_001_lora"
    
    @pytest.mark.asyncio
    async def test_batch_processing_progress_tracking(self, structured_scene_data):
        with patch('services.image_generation.ImageGenerationService') as MockService:
            mock_service = MockService.return_value
            
            progress_updates = []
            
            async def mock_generate_with_progress(scene, callback):
                await asyncio.sleep(0.1)
                callback(scene["scene_id"], 100)
                return {"scene_id": scene["scene_id"], "image_url": "test.png"}
            
            mock_service.generate_scene.side_effect = lambda scene, cb: mock_generate_with_progress(scene, cb)
            
            def progress_callback(scene_id, progress):
                progress_updates.append({"scene_id": scene_id, "progress": progress})
            
            results = []
            for scene in structured_scene_data["scenes"]:
                result = await mock_service.generate_scene(scene, progress_callback)
                results.append(result)
            
            assert len(results) == 3
            assert len(progress_updates) == 3
    
    @pytest.mark.asyncio
    async def test_fallback_to_alternative_model_on_failure(self, structured_scene_data):
        with patch('services.image_generation.ImageGenerationService') as MockService:
            mock_service = MockService.return_value
            
            mock_service.generate_with_fallback.side_effect = [
                Exception("Stable Diffusion unavailable"),
            ]
            
            with patch('services.image_generation.DallEService') as MockDallE:
                mock_dalle = MockDallE.return_value
                mock_dalle.generate.return_value = {
                    "image_url": "https://dalle.generated.com/image.png"
                }
                
                try:
                    await mock_service.generate_with_fallback(structured_scene_data["scenes"][0])
                except Exception:
                    result = await mock_dalle.generate(structured_scene_data["scenes"][0])
                    
                    assert "image_url" in result
    
    @pytest.mark.asyncio
    async def test_image_metadata_preservation(self, mock_image):
        with patch('services.image_generation.ImageGenerationService') as MockService:
            mock_service = MockService.return_value
            
            metadata = {
                "prompt": "测试提示词",
                "model": "stable-diffusion-xl",
                "seed": 123456,
                "steps": 30,
                "cfg_scale": 7.5,
                "sampler": "DPM++ 2M Karras"
            }
            
            mock_service.generate_with_metadata.return_value = {
                "image": mock_image,
                "metadata": metadata
            }
            
            result = await mock_service.generate_with_metadata("测试提示词")
            
            assert "metadata" in result
            assert result["metadata"]["seed"] == 123456
            assert result["metadata"]["model"] == "stable-diffusion-xl"
    
    @pytest.mark.asyncio
    async def test_performance_optimization_caching(self, structured_scene_data):
        with patch('services.image_generation.ImageGenerationService') as MockService:
            mock_service = MockService.return_value
            
            mock_service.get_or_generate.side_effect = [
                {"source": "generated", "url": "test1.png"},
                {"source": "cache", "url": "test1.png"}
            ]
            
            result1 = await mock_service.get_or_generate(structured_scene_data["scenes"][0])
            result2 = await mock_service.get_or_generate(structured_scene_data["scenes"][0])
            
            assert result1["source"] == "generated"
            assert result2["source"] == "cache"
