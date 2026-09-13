from pathlib import Path
from threading import RLock
from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlalchemy import Column, JSON
from .models import uid, now

class Record(SQLModel, table=True):
    id: str = Field(primary_key=True)
    session_id: str = Field(index=True)
    kind: str = Field(index=True)
    payload: dict = Field(sa_column=Column(JSON, nullable=False))

class Store:
    def __init__(self, directory: Path):
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine('sqlite:///' + str(self.directory / 'proofapply.db'), connect_args={'check_same_thread': False})
        SQLModel.metadata.create_all(self.engine)
        self.lock = RLock()
    def add(self, kind, session_id, payload, id=None):
        with self.lock, Session(self.engine) as db:
            id = id or uid()
            value = {**payload, 'id': id}
            db.add(Record(id=id, session_id=session_id, kind=kind, payload=value)); db.commit()
            return value
    def get(self, id, session_id=None, kind=None):
        with self.lock, Session(self.engine) as db:
            row = db.get(Record, id)
            if not row or (session_id is not None and row.session_id != session_id) or (kind and row.kind != kind): return None
            return dict(row.payload)
    def list(self, kind, session_id=None):
        with self.lock, Session(self.engine) as db:
            query=select(Record).where(Record.kind == kind)
            if session_id is not None: query=query.where(Record.session_id == session_id)
            return [dict(r.payload) for r in db.exec(query).all()]
    def update(self, id, payload):
        with self.lock, Session(self.engine) as db:
            row=db.get(Record,id)
            if not row: raise KeyError('Record expired')
            if row.kind in ('source','evidence','event','draft','evaluation','decision'): raise ValueError('Immutable record')
            row.payload={**payload,'id':id}; db.add(row); db.commit()
            return row.payload
    def delete(self, id):
        with self.lock, Session(self.engine) as db:
            row=db.get(Record,id)
            if row: db.delete(row); db.commit()
    def folder(self, session_id):
        # IDs always come from our session store, never filenames.
        if len(session_id)!=32 or any(c not in '0123456789abcdef' for c in session_id): raise ValueError('Invalid session')
        path=(self.directory / session_id).resolve()
        if not path.is_relative_to(self.directory): raise ValueError('Invalid path')
        path.mkdir(exist_ok=True)
        return path
    def delete_session(self, session_id):
        import shutil
        with self.lock, Session(self.engine) as db:
            for row in db.exec(select(Record).where(Record.session_id==session_id)).all(): db.delete(row)
            db.commit()
            path=(self.directory/session_id).resolve()
            if path.parent == self.directory and path.is_dir(): shutil.rmtree(path)
    def event(self, run, actor, action, summary, source_ids=None, status='ok', result_ids=None):
        with self.lock:
            events=[x for x in self.list('event',run['session_id']) if x['run_id']==run['id']]
            return self.add('event',run['session_id'],dict(seq=len(events)+1,run_id=run['id'],time=now(),actor=actor,action=action,summary=summary,source_ids=source_ids or [],result_ids=result_ids or [],status=status,mode=run['mode']))
