import json
import uuid
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
from .schemas import ClientStatus


class ClientSession:
    def __init__(
        self,
        client_id: str,
        client_name: str,
        client_ip: str = "127.0.0.1",
        status: ClientStatus = ClientStatus.ONLINE
    ):
        self.client_id = client_id
        self.client_name = client_name
        self.client_ip = client_ip
        self.last_heartbeat = datetime.now()
        self.status = status
        self.created_at = datetime.now()
        self.data_dir = Path(f"configs/clients/{client_id}")
        self.heartbeat_count = 0
        self.last_activity = datetime.now()
        self.connection_info = {}
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def update_heartbeat(self) -> None:
        self.last_heartbeat = datetime.now()
        self.last_activity = datetime.now()
        self.heartbeat_count += 1
        self.status = ClientStatus.ONLINE
    
    def is_expired(self, timeout_minutes: int = 5) -> bool:
        time_since_heartbeat = datetime.now() - self.last_heartbeat
        return time_since_heartbeat > timedelta(minutes=timeout_minutes)
    
    def get_offline_duration(self) -> str:
        if self.status == ClientStatus.ONLINE:
            return "0:00:00"
        duration = datetime.now() - self.last_heartbeat
        return str(duration).split('.')[0]
    
    def to_dict(self) -> dict:
        return {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "client_ip": self.client_ip,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "heartbeat_count": self.heartbeat_count,
            "last_activity": self.last_activity.isoformat(),
            "connection_info": self.connection_info,
            "offline_duration": self.get_offline_duration()
        }


class ClientSessionManager:
    def __init__(self, sessions_file: str = "configs/sessions.json", timeout_minutes: int = 5):
        self.sessions: Dict[str, ClientSession] = {}
        self.sessions_file = Path(sessions_file)
        self.timeout_minutes = timeout_minutes
        self.max_clients = 100
        self.lock = threading.Lock()
        
        self.sessions_file.parent.mkdir(parents=True, exist_ok=True)
        self.load_sessions()
    
    def register_client(self, client_name: Optional[str] = None, client_ip: str = "127.0.0.1") -> ClientSession:
        with self.lock:
            if len(self.sessions) >= self.max_clients:
                self.cleanup_expired_clients()
                if len(self.sessions) >= self.max_clients:
                    raise ValueError(f"Maximum number of clients ({self.max_clients}) reached")
            
            client_id = str(uuid.uuid4())
            if client_name is None:
                client_name = f"Client-{client_id[:8]}"
            
            session = ClientSession(client_id, client_name, client_ip)
            self.sessions[client_id] = session
            self.save_sessions()
            
            return session
    
    def get_client(self, client_id: str) -> Optional[ClientSession]:
        return self.sessions.get(client_id)
    
    def update_heartbeat(self, client_id: str) -> bool:
        with self.lock:
            session = self.sessions.get(client_id)
            if session:
                session.update_heartbeat()
                self.save_sessions()
                return True
            return False
    
    def is_client_online(self, client_id: str) -> bool:
        session = self.sessions.get(client_id)
        if not session:
            return False
        
        if session.is_expired(self.timeout_minutes):
            session.status = ClientStatus.EXPIRED
            return False
        
        return session.status == ClientStatus.ONLINE
    
    def cleanup_expired_clients(self) -> int:
        with self.lock:
            expired_clients = []
            for client_id, session in self.sessions.items():
                if session.is_expired(self.timeout_minutes):
                    session.status = ClientStatus.EXPIRED
                    expired_clients.append(client_id)
            
            for client_id in expired_clients:
                self._cleanup_client_data(client_id)
                del self.sessions[client_id]
            
            if expired_clients:
                self.save_sessions()
            
            return len(expired_clients)
    
    def cleanup_client(self, client_id: str) -> bool:
        with self.lock:
            if client_id in self.sessions:
                self._cleanup_client_data(client_id)
                del self.sessions[client_id]
                self.save_sessions()
                return True
            return False
    
    def _cleanup_client_data(self, client_id: str) -> None:
        data_dir = Path(f"configs/clients/{client_id}")
        if data_dir.exists():
            import shutil
            shutil.rmtree(data_dir, ignore_errors=True)
    
    def get_online_clients(self) -> Dict[str, ClientSession]:
        self.cleanup_expired_clients()
        return {
            client_id: session
            for client_id, session in self.sessions.items()
            if session.status == ClientStatus.ONLINE
        }
    
    def get_offline_clients(self) -> Dict[str, ClientSession]:
        return {
            client_id: session
            for client_id, session in self.sessions.items()
            if session.status != ClientStatus.ONLINE
        }
    
    def get_stats(self) -> dict:
        total = len(self.sessions)
        online = len(self.get_online_clients())
        offline = len(self.get_offline_clients())
        
        return {
            "total_clients": total,
            "online_clients": online,
            "offline_clients": offline,
            "max_clients": self.max_clients,
            "timeout_minutes": self.timeout_minutes
        }
    
    def save_sessions(self) -> None:
        data = {
            "sessions": {
                client_id: session.to_dict()
                for client_id, session in self.sessions.items()
            },
            "last_updated": datetime.now().isoformat(),
            "total_clients": len(self.sessions),
            "online_clients": len(self.get_online_clients())
        }
        
        with open(self.sessions_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_sessions(self) -> None:
        if not self.sessions_file.exists():
            return
        
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for client_id, session_data in data.get("sessions", {}).items():
                session = ClientSession(
                    client_id=session_data["client_id"],
                    client_name=session_data["client_name"],
                    client_ip=session_data.get("client_ip", "127.0.0.1"),
                    status=ClientStatus(session_data.get("status", "online"))
                )
                session.last_heartbeat = datetime.fromisoformat(session_data["last_heartbeat"])
                session.created_at = datetime.fromisoformat(session_data["created_at"])
                session.heartbeat_count = session_data.get("heartbeat_count", 0)
                session.last_activity = datetime.fromisoformat(
                    session_data.get("last_activity", session_data["last_heartbeat"])
                )
                session.connection_info = session_data.get("connection_info", {})
                
                self.sessions[client_id] = session
            
            self.cleanup_expired_clients()
        
        except Exception as e:
            print(f"Error loading sessions: {e}")
            self.sessions = {}


session_manager = ClientSessionManager()
