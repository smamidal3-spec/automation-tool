from __future__ import annotations

import json

from sqlalchemy import desc, select

from app.database import get_session
from app.db_models import AuditLog
from app.models import AuditEvent, AuditLogItem


class AuditService:
    def log(self, event: AuditEvent) -> None:
        with get_session() as session:
            row = AuditLog(
                user_id=event.user_id,
                role=event.role,
                timestamp=event.timestamp,
                repo=event.repo,
                file_path=event.file_path,
                key_path=event.key_path,
                old_value=json.dumps(event.old_value, default=str),
                new_value=json.dumps(event.new_value, default=str),
                pull_request_url=event.pull_request_url,
                status=event.status,
                error=event.error,
            )
            session.add(row)
            session.commit()

    def list_events(self, limit: int = 200) -> list[AuditLogItem]:
        with get_session() as session:
            stmt = select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit)
            rows = session.execute(stmt).scalars().all()
            return [
                AuditLogItem(
                    id=row.id,
                    user_id=row.user_id,
                    role=row.role,
                    timestamp=row.timestamp,
                    repo=row.repo,
                    file_path=row.file_path,
                    key_path=row.key_path,
                    old_value=json.loads(row.old_value),
                    new_value=json.loads(row.new_value),
                    pull_request_url=row.pull_request_url,
                    status=row.status,
                    error=row.error,
                )
                for row in rows
            ]


audit_service = AuditService()
