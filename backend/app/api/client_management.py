from fastapi import APIRouter, HTTPException, Request
from .schemas import (
    ClientRegisterRequest,
    ClientResponse,
    HeartbeatResponse,
    ClientStatusResponse,
    SessionListResponse,
    SessionStatsResponse,
    OnlineClientsResponse,
    OfflineClientsResponse,
    CleanupResponse
)
from .client_session import session_manager

router = APIRouter(prefix="/client", tags=["客户端管理"])


@router.post("/register", response_model=ClientResponse)
async def register_client(request: ClientRegisterRequest, req: Request):
    try:
        client_ip = req.client.host if req.client else "127.0.0.1"
        session = session_manager.register_client(
            client_name=request.client_name,
            client_ip=client_ip
        )
        
        return ClientResponse(
            success=True,
            client_id=session.client_id,
            client_name=session.client_name,
            created_at=session.created_at.isoformat(),
            message="客户端注册成功"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


@router.post("/heartbeat/{client_id}", response_model=HeartbeatResponse)
async def heartbeat(client_id: str):
    if not session_manager.update_heartbeat(client_id):
        raise HTTPException(status_code=404, detail="客户端未找到")
    
    session = session_manager.get_client(client_id)
    
    return HeartbeatResponse(
        success=True,
        client_id=client_id,
        last_heartbeat=session.last_heartbeat.isoformat()
    )


@router.get("/sessions", response_model=SessionListResponse)
async def get_sessions():
    sessions_dict = {
        client_id: session.to_dict()
        for client_id, session in session_manager.sessions.items()
    }
    
    return SessionListResponse(
        success=True,
        sessions=sessions_dict,
        total_count=len(sessions_dict)
    )


@router.get("/status/{client_id}", response_model=ClientStatusResponse)
async def get_client_status(client_id: str):
    session = session_manager.get_client(client_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="客户端未找到")
    
    is_online = session_manager.is_client_online(client_id)
    
    return ClientStatusResponse(
        success=True,
        client_id=client_id,
        status=session.status.value,
        is_online=is_online,
        last_heartbeat=session.last_heartbeat.isoformat(),
        offline_duration=session.get_offline_duration()
    )


@router.get("/stats", response_model=SessionStatsResponse)
async def get_stats():
    stats = session_manager.get_stats()
    
    return SessionStatsResponse(
        success=True,
        stats=stats
    )


@router.post("/cleanup/{client_id}", response_model=CleanupResponse)
async def cleanup_client(client_id: str):
    if not session_manager.cleanup_client(client_id):
        raise HTTPException(status_code=404, detail="客户端未找到")
    
    return CleanupResponse(
        success=True,
        message=f"客户端 {client_id} 已清理"
    )


@router.post("/cleanup/expired", response_model=CleanupResponse)
async def cleanup_expired():
    count = session_manager.cleanup_expired_clients()
    
    return CleanupResponse(
        success=True,
        message=f"已清理 {count} 个过期客户端"
    )


@router.get("/online", response_model=OnlineClientsResponse)
async def get_online_clients():
    online_clients = session_manager.get_online_clients()
    online_dict = {
        client_id: session.to_dict()
        for client_id, session in online_clients.items()
    }
    
    return OnlineClientsResponse(
        success=True,
        online_clients=online_dict,
        count=len(online_dict)
    )


@router.get("/offline", response_model=OfflineClientsResponse)
async def get_offline_clients():
    offline_clients = session_manager.get_offline_clients()
    offline_dict = {
        client_id: session.to_dict()
        for client_id, session in offline_clients.items()
    }
    
    return OfflineClientsResponse(
        success=True,
        offline_clients=offline_dict,
        count=len(offline_dict)
    )
