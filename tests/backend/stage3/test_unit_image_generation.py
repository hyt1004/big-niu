import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from PIL import Image
from io import BytesIO
from app.services.stage3_image_generation import Stage3ImageGenerationService
from app.models.schemas import Stage2Output


class TestStage3ImageGenerationUnit:
    
    @pytest.fixture
    def sample_prompt(self):
        return "A beautiful anime-style cityscape in the morning"
    
    @pytest.fixture
    def sample_stage2_output(self):
        return Stage2Output(
            scene_id="scene_001",
            image_prompt="Test prompt",
            negative_prompt="low quality",
            style_tags=["anime"],
            characters_in_scene=["char_001"]
        )
    
    @pytest.fixture
    def mock_image_bytes(self):
        img = Image.new('RGB', (1024, 1024), color='red')
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    
    @pytest.mark.asyncio
    async def test_api_request_structure(self, sample_prompt):
        with patch('httpx.AsyncClient') as MockClient:
            mock_client = MockClient.return_value.__aenter__.return_value
            
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": [{"url": "https://test.com/image.png"}]
            }
            mock_response.raise_for_status = Mock()
            
            captured_payload = None
            
            async def capture_post(url, **kwargs):
                nonlocal captured_payload
                captured_payload = kwargs['json']
                return mock_response
            
            mock_client.post = capture_post
            mock_client.get = AsyncMock(return_value=Mock(content=b'test', raise_for_status=Mock()))
            
            service = Stage3ImageGenerationService()
            await service.generate_image_from_prompt(sample_prompt)
            
            assert captured_payload is not None
            assert captured_payload['model'] == 'dall-e-3'
            assert captured_payload['prompt'] == sample_prompt
            assert captured_payload['size'] == '1024x1024'
    
    @pytest.mark.asyncio
    async def test_custom_size_parameter(self):
        with patch('httpx.AsyncClient') as MockClient:
            mock_client = MockClient.return_value.__aenter__.return_value
            
            captured_payload = None
            
            async def capture_post(url, **kwargs):
                nonlocal captured_payload
                captured_payload = kwargs['json']
                mock_response = Mock()
                mock_response.json.return_value = {
                    "data": [{"url": "https://test.com/image.png"}]
                }
                mock_response.raise_for_status = Mock()
                return mock_response
            
            mock_client.post = capture_post
            mock_client.get = AsyncMock(return_value=Mock(content=b'test', raise_for_status=Mock()))
            
            service = Stage3ImageGenerationService()
            await service.generate_image_from_prompt("test", size="1792x1024")
            
            assert captured_payload['size'] == '1792x1024'
    
    @pytest.mark.asyncio
    async def test_quality_parameter(self):
        with patch('httpx.AsyncClient') as MockClient:
            mock_client = MockClient.return_value.__aenter__.return_value
            
            captured_payload = None
            
            async def capture_post(url, **kwargs):
                nonlocal captured_payload
                captured_payload = kwargs['json']
                mock_response = Mock()
                mock_response.json.return_value = {
                    "data": [{"url": "https://test.com/image.png"}]
                }
                mock_response.raise_for_status = Mock()
                return mock_response
            
            mock_client.post = capture_post
            mock_client.get = AsyncMock(return_value=Mock(content=b'test', raise_for_status=Mock()))
            
            service = Stage3ImageGenerationService()
            await service.generate_image_from_prompt("test", quality="hd")
            
            assert captured_payload['quality'] == 'hd'
    
    def test_save_image_creates_file(self, mock_image_bytes):
        service = Stage3ImageGenerationService(output_dir="/tmp/test_unit")
        
        filepath = service.save_image(mock_image_bytes, "test_unit.png")
        
        assert os.path.exists(filepath)
        assert filepath.endswith("test_unit.png")
        
        img = Image.open(filepath)
        assert img.format == "PNG"
        
        if os.path.exists(filepath):
            os.remove(filepath)
    
    def test_save_image_returns_correct_path(self, mock_image_bytes):
        service = Stage3ImageGenerationService(output_dir="/tmp/test_unit")
        
        filepath = service.save_image(mock_image_bytes, "scene_001.png")
        
        assert "/tmp/test_unit" in filepath
        assert "scene_001.png" in filepath
        
        if os.path.exists(filepath):
            os.remove(filepath)
    
    @pytest.mark.asyncio
    async def test_scene_id_in_filename(self, sample_stage2_output, mock_image_bytes):
        with patch('httpx.AsyncClient') as MockClient:
            mock_client = MockClient.return_value.__aenter__.return_value
            
            mock_post_response = Mock()
            mock_post_response.json.return_value = {
                "data": [{"url": "https://test.com/image.png"}]
            }
            mock_post_response.raise_for_status = Mock()
            
            mock_get_response = Mock()
            mock_get_response.content = mock_image_bytes
            mock_get_response.raise_for_status = Mock()
            
            mock_client.post = AsyncMock(return_value=mock_post_response)
            mock_client.get = AsyncMock(return_value=mock_get_response)
            
            service = Stage3ImageGenerationService(output_dir="/tmp/test_unit")
            
            result = await service.generate_scene_image(sample_stage2_output)
            
            assert sample_stage2_output.scene_id in result.image_path
            
            if os.path.exists(result.image_path):
                os.remove(result.image_path)
    
    @pytest.mark.asyncio
    async def test_output_contains_all_required_fields(self, sample_stage2_output, mock_image_bytes):
        with patch('httpx.AsyncClient') as MockClient:
            mock_client = MockClient.return_value.__aenter__.return_value
            
            mock_post_response = Mock()
            mock_post_response.json.return_value = {
                "data": [{"url": "https://test.com/image.png"}]
            }
            mock_post_response.raise_for_status = Mock()
            
            mock_get_response = Mock()
            mock_get_response.content = mock_image_bytes
            mock_get_response.raise_for_status = Mock()
            
            mock_client.post = AsyncMock(return_value=mock_post_response)
            mock_client.get = AsyncMock(return_value=mock_get_response)
            
            service = Stage3ImageGenerationService(output_dir="/tmp/test_unit")
            
            result = await service.generate_scene_image(sample_stage2_output)
            
            assert hasattr(result, 'scene_id')
            assert hasattr(result, 'image_path')
            assert hasattr(result, 'image_url')
            assert hasattr(result, 'width')
            assert hasattr(result, 'height')
            assert hasattr(result, 'generation_params')
            
            if os.path.exists(result.image_path):
                os.remove(result.image_path)
    
    @pytest.mark.asyncio
    async def test_generation_params_includes_prompt(self, sample_stage2_output, mock_image_bytes):
        with patch('httpx.AsyncClient') as MockClient:
            mock_client = MockClient.return_value.__aenter__.return_value
            
            mock_post_response = Mock()
            mock_post_response.json.return_value = {
                "data": [{"url": "https://test.com/image.png"}]
            }
            mock_post_response.raise_for_status = Mock()
            
            mock_get_response = Mock()
            mock_get_response.content = mock_image_bytes
            mock_get_response.raise_for_status = Mock()
            
            mock_client.post = AsyncMock(return_value=mock_post_response)
            mock_client.get = AsyncMock(return_value=mock_get_response)
            
            service = Stage3ImageGenerationService(output_dir="/tmp/test_unit")
            
            result = await service.generate_scene_image(sample_stage2_output)
            
            assert 'prompt' in result.generation_params
            assert sample_stage2_output.image_prompt in result.generation_params['prompt']
            
            if os.path.exists(result.image_path):
                os.remove(result.image_path)
    
    @pytest.mark.asyncio
    async def test_handles_api_error(self, sample_stage2_output):
        with patch('httpx.AsyncClient') as MockClient:
            mock_client = MockClient.return_value.__aenter__.return_value
            
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("API Error")
            
            mock_client.post = AsyncMock(return_value=mock_response)
            
            service = Stage3ImageGenerationService(output_dir="/tmp/test_unit")
            
            with pytest.raises(Exception):
                await service.generate_scene_image(sample_stage2_output)
    
    @pytest.mark.asyncio
    async def test_batch_generation_preserves_order(self):
        outputs = [
            Stage2Output(
                scene_id=f"scene_{i:03d}",
                image_prompt=f"Prompt {i}",
                negative_prompt="",
                style_tags=[],
                characters_in_scene=[]
            )
            for i in range(1, 4)
        ]
        
        with patch.object(Stage3ImageGenerationService, 'generate_scene_image') as mock_generate:
            async def mock_gen(stage2_output, **kwargs):
                from app.models.schemas import Stage3Output
                return Stage3Output(
                    scene_id=stage2_output.scene_id,
                    image_path=f"/tmp/{stage2_output.scene_id}.png",
                    width=1024,
                    height=1024,
                    generation_params={}
                )
            
            mock_generate.side_effect = mock_gen
            
            service = Stage3ImageGenerationService()
            results = await service.generate_all_images(outputs)
            
            assert len(results) == 3
            assert results[0].scene_id == "scene_001"
            assert results[1].scene_id == "scene_002"
            assert results[2].scene_id == "scene_003"
    
    def test_output_directory_created_on_init(self):
        test_dir = "/tmp/test_unit_new_dir"
        
        if os.path.exists(test_dir):
            os.rmdir(test_dir)
        
        service = Stage3ImageGenerationService(output_dir=test_dir)
        
        assert os.path.exists(test_dir)
        
        if os.path.exists(test_dir):
            os.rmdir(test_dir)
    
    @pytest.mark.asyncio
    async def test_image_dimensions_captured(self, sample_stage2_output):
        mock_img = Image.new('RGB', (512, 512), color='green')
        mock_bytes = BytesIO()
        mock_img.save(mock_bytes, format='PNG')
        mock_bytes = mock_bytes.getvalue()
        
        with patch('httpx.AsyncClient') as MockClient:
            mock_client = MockClient.return_value.__aenter__.return_value
            
            mock_post_response = Mock()
            mock_post_response.json.return_value = {
                "data": [{"url": "https://test.com/image.png"}]
            }
            mock_post_response.raise_for_status = Mock()
            
            mock_get_response = Mock()
            mock_get_response.content = mock_bytes
            mock_get_response.raise_for_status = Mock()
            
            mock_client.post = AsyncMock(return_value=mock_post_response)
            mock_client.get = AsyncMock(return_value=mock_get_response)
            
            service = Stage3ImageGenerationService(output_dir="/tmp/test_unit")
            
            result = await service.generate_scene_image(sample_stage2_output)
            
            assert result.width == 512
            assert result.height == 512
            
            if os.path.exists(result.image_path):
                os.remove(result.image_path)
