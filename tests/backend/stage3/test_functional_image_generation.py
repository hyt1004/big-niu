import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from PIL import Image
from io import BytesIO
from app.services.stage3_image_generation import Stage3ImageGenerationService
from app.models.schemas import Stage2Output, Stage3Output


class TestStage3ImageGenerationFunctional:
    
    @pytest.fixture
    def sample_stage2_output(self):
        return Stage2Output(
            scene_id="scene_001",
            image_prompt="A beautiful morning cityscape with tall buildings, sunlight streaming between skyscrapers, wide angle overhead view, anime style, masterpiece, best quality, highly detailed, 4k, cinematic lighting",
            negative_prompt="low quality, blurry, distorted, ugly, bad anatomy",
            style_tags=["anime", "high_quality", "4k"],
            characters_in_scene=["char_001"]
        )
    
    @pytest.fixture
    def sample_stage2_outputs(self):
        return [
            Stage2Output(
                scene_id="scene_001",
                image_prompt="A beautiful morning cityscape with tall buildings",
                negative_prompt="low quality, blurry",
                style_tags=["anime"],
                characters_in_scene=["char_001"]
            ),
            Stage2Output(
                scene_id="scene_002",
                image_prompt="A cozy coffee shop interior with warm lighting",
                negative_prompt="low quality, blurry",
                style_tags=["anime"],
                characters_in_scene=["char_001", "char_002"]
            ),
        ]
    
    @pytest.fixture
    def mock_image_data(self):
        img = Image.new('RGB', (1024, 1024), color='blue')
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr.read()
    
    @pytest.mark.asyncio
    async def test_generate_image_from_prompt(self, sample_stage2_output, mock_image_data):
        with patch('httpx.AsyncClient') as MockAsyncClient:
            mock_client = MockAsyncClient.return_value.__aenter__.return_value
            
            mock_post_response = Mock()
            mock_post_response.json.return_value = {
                "data": [{"url": "https://test.com/image.png"}]
            }
            mock_post_response.raise_for_status = Mock()
            
            mock_get_response = Mock()
            mock_get_response.content = mock_image_data
            mock_get_response.raise_for_status = Mock()
            
            mock_client.post = AsyncMock(return_value=mock_post_response)
            mock_client.get = AsyncMock(return_value=mock_get_response)
            
            service = Stage3ImageGenerationService(output_dir="/tmp/test_images")
            
            result = await service.generate_image_from_prompt(
                prompt=sample_stage2_output.image_prompt
            )
            
            assert result is not None
            assert isinstance(result, bytes)
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_save_image(self, mock_image_data):
        service = Stage3ImageGenerationService(output_dir="/tmp/test_images")
        
        filepath = service.save_image(mock_image_data, "test_scene.png")
        
        assert os.path.exists(filepath)
        assert filepath.endswith("test_scene.png")
        
        img = Image.open(filepath)
        assert img.size == (1024, 1024)
        
        if os.path.exists(filepath):
            os.remove(filepath)
    
    @pytest.mark.asyncio
    async def test_generate_scene_image(self, sample_stage2_output, mock_image_data):
        with patch('httpx.AsyncClient') as MockAsyncClient:
            mock_client = MockAsyncClient.return_value.__aenter__.return_value
            
            mock_post_response = Mock()
            mock_post_response.json.return_value = {
                "data": [{"url": "https://test.com/image.png"}]
            }
            mock_post_response.raise_for_status = Mock()
            
            mock_get_response = Mock()
            mock_get_response.content = mock_image_data
            mock_get_response.raise_for_status = Mock()
            
            mock_client.post = AsyncMock(return_value=mock_post_response)
            mock_client.get = AsyncMock(return_value=mock_get_response)
            
            service = Stage3ImageGenerationService(output_dir="/tmp/test_images")
            
            result = await service.generate_scene_image(sample_stage2_output)
            
            assert isinstance(result, Stage3Output)
            assert result.scene_id == "scene_001"
            assert os.path.exists(result.image_path)
            assert result.width == 1024
            assert result.height == 1024
            assert result.generation_params["model"] == "dall-e-3"
            
            if os.path.exists(result.image_path):
                os.remove(result.image_path)
    
    @pytest.mark.asyncio
    async def test_generate_all_images(self, sample_stage2_outputs, mock_image_data):
        with patch('httpx.AsyncClient') as MockAsyncClient:
            mock_client = MockAsyncClient.return_value.__aenter__.return_value
            
            mock_post_response = Mock()
            mock_post_response.json.return_value = {
                "data": [{"url": "https://test.com/image.png"}]
            }
            mock_post_response.raise_for_status = Mock()
            
            mock_get_response = Mock()
            mock_get_response.content = mock_image_data
            mock_get_response.raise_for_status = Mock()
            
            mock_client.post = AsyncMock(return_value=mock_post_response)
            mock_client.get = AsyncMock(return_value=mock_get_response)
            
            service = Stage3ImageGenerationService(output_dir="/tmp/test_images")
            
            results = await service.generate_all_images(sample_stage2_outputs)
            
            assert len(results) == 2
            assert all(isinstance(r, Stage3Output) for r in results)
            assert results[0].scene_id == "scene_001"
            assert results[1].scene_id == "scene_002"
            
            for result in results:
                if os.path.exists(result.image_path):
                    os.remove(result.image_path)
    
    @pytest.mark.asyncio
    async def test_prompt_includes_negative_prompt(self, sample_stage2_output, mock_image_data):
        with patch('httpx.AsyncClient') as MockAsyncClient:
            mock_client = MockAsyncClient.return_value.__aenter__.return_value
            
            captured_prompt = None
            
            async def capture_post(url, **kwargs):
                nonlocal captured_prompt
                captured_prompt = kwargs['json']['prompt']
                mock_response = Mock()
                mock_response.json.return_value = {
                    "data": [{"url": "https://test.com/image.png"}]
                }
                mock_response.raise_for_status = Mock()
                return mock_response
            
            mock_get_response = Mock()
            mock_get_response.content = mock_image_data
            mock_get_response.raise_for_status = Mock()
            
            mock_client.post = capture_post
            mock_client.get = AsyncMock(return_value=mock_get_response)
            
            service = Stage3ImageGenerationService(output_dir="/tmp/test_images")
            
            result = await service.generate_scene_image(sample_stage2_output)
            
            assert "Avoid:" in captured_prompt
            assert sample_stage2_output.negative_prompt in captured_prompt
            
            if os.path.exists(result.image_path):
                os.remove(result.image_path)
    
    @pytest.mark.asyncio
    async def test_output_directory_creation(self):
        test_dir = "/tmp/test_images_new"
        
        if os.path.exists(test_dir):
            os.rmdir(test_dir)
        
        service = Stage3ImageGenerationService(output_dir=test_dir)
        
        assert os.path.exists(test_dir)
        
        if os.path.exists(test_dir):
            os.rmdir(test_dir)
    
    @pytest.mark.asyncio
    async def test_image_format_is_png(self, sample_stage2_output, mock_image_data):
        with patch('httpx.AsyncClient') as MockAsyncClient:
            mock_client = MockAsyncClient.return_value.__aenter__.return_value
            
            mock_post_response = Mock()
            mock_post_response.json.return_value = {
                "data": [{"url": "https://test.com/image.png"}]
            }
            mock_post_response.raise_for_status = Mock()
            
            mock_get_response = Mock()
            mock_get_response.content = mock_image_data
            mock_get_response.raise_for_status = Mock()
            
            mock_client.post = AsyncMock(return_value=mock_post_response)
            mock_client.get = AsyncMock(return_value=mock_get_response)
            
            service = Stage3ImageGenerationService(output_dir="/tmp/test_images")
            
            result = await service.generate_scene_image(sample_stage2_output)
            
            assert result.image_path.endswith(".png")
            
            img = Image.open(result.image_path)
            assert img.format == "PNG"
            
            if os.path.exists(result.image_path):
                os.remove(result.image_path)
    
    @pytest.mark.asyncio
    async def test_generation_params_captured(self, sample_stage2_output, mock_image_data):
        with patch('httpx.AsyncClient') as MockAsyncClient:
            mock_client = MockAsyncClient.return_value.__aenter__.return_value
            
            mock_post_response = Mock()
            mock_post_response.json.return_value = {
                "data": [{"url": "https://test.com/image.png"}]
            }
            mock_post_response.raise_for_status = Mock()
            
            mock_get_response = Mock()
            mock_get_response.content = mock_image_data
            mock_get_response.raise_for_status = Mock()
            
            mock_client.post = AsyncMock(return_value=mock_post_response)
            mock_client.get = AsyncMock(return_value=mock_get_response)
            
            service = Stage3ImageGenerationService(output_dir="/tmp/test_images")
            
            result = await service.generate_scene_image(
                sample_stage2_output,
                size="1024x1024",
                quality="hd"
            )
            
            assert "model" in result.generation_params
            assert "size" in result.generation_params
            assert "quality" in result.generation_params
            assert "prompt" in result.generation_params
            assert result.generation_params["size"] == "1024x1024"
            assert result.generation_params["quality"] == "hd"
            
            if os.path.exists(result.image_path):
                os.remove(result.image_path)
