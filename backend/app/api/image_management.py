import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from .schemas import ImageUploadResponse, ImageListResponse
from .client_session import session_manager

router = APIRouter(prefix="/images", tags=["图片管理"])


def get_images_dir(client_id: str) -> Path:
    return Path(f"configs/clients/{client_id}/images")


def get_test_images_dir() -> Path:
    return Path("test_data/images")


@router.get("/{client_id}", response_model=ImageListResponse)
async def get_images(client_id: str):
    if not session_manager.is_client_online(client_id):
        raise HTTPException(status_code=410, detail="客户端已离线")
    
    images_dir = get_images_dir(client_id)
    
    if not images_dir.exists():
        return ImageListResponse(
            success=True,
            images=[]
        )
    
    try:
        images = []
        for img_file in images_dir.glob("*"):
            if img_file.is_file() and img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                images.append({
                    "filename": img_file.name,
                    "url": f"/api/v1/bigniu/images/{client_id}/{img_file.name}",
                    "size": img_file.stat().st_size,
                    "created_at": img_file.stat().st_ctime
                })
        
        images.sort(key=lambda x: x["created_at"], reverse=True)
        
        return ImageListResponse(
            success=True,
            images=images
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图片列表失败: {str(e)}")


@router.post("/{client_id}", response_model=ImageUploadResponse)
async def upload_image(client_id: str, file: UploadFile = File(...)):
    if not session_manager.is_client_online(client_id):
        raise HTTPException(status_code=410, detail="客户端已离线")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="文件类型必须是图片")
    
    images_dir = get_images_dir(client_id)
    images_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        file_path = images_dir / file.filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return ImageUploadResponse(
            success=True,
            image_url=f"/api/v1/bigniu/images/{client_id}/{file.filename}"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传图片失败: {str(e)}")


@router.get("/test/{filename}")
async def get_test_image(filename: str):
    test_images_dir = get_test_images_dir()
    test_images_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = test_images_dir / filename
    
    if not file_path.exists():
        placeholder_path = test_images_dir / "placeholder.png"
        
        if not placeholder_path.exists():
            from PIL import Image, ImageDraw, ImageFont
            
            img = Image.new('RGB', (800, 600), color=(73, 109, 137))
            d = ImageDraw.Draw(img)
            d.text((400, 300), filename, fill=(255, 255, 255), anchor="mm")
            img.save(placeholder_path)
        
        return FileResponse(placeholder_path, media_type="image/png")
    
    return FileResponse(file_path)


@router.get("/{client_id}/{filename}")
async def get_image(client_id: str, filename: str):
    if not session_manager.is_client_online(client_id):
        raise HTTPException(status_code=410, detail="客户端已离线")
    
    images_dir = get_images_dir(client_id)
    file_path = images_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="图片未找到")
    
    return FileResponse(file_path)
