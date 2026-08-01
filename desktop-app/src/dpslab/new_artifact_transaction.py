"""Compensating new-file transaction across one or more volumes."""
from __future__ import annotations
import os,uuid
from pathlib import Path
from typing import Callable,Mapping
class NewArtifactTransactionError(RuntimeError):pass
class NewArtifactTransaction:
    def __init__(self,replace:Callable[[str,str],None]=os.replace):self._replace=replace
    def commit_new(self,artifacts:Mapping[Path,bytes])->None:
        if not isinstance(artifacts,dict) or not artifacts:raise NewArtifactTransactionError("artifacts_invalid")
        targets=[]
        for path,data in artifacts.items():
            if not isinstance(path,Path) or not path.is_absolute() or not isinstance(data,bytes) or not data:raise NewArtifactTransactionError("artifact_invalid")
            target=path.resolve()
            if target.exists() or not target.parent.is_dir():raise NewArtifactTransactionError("target_unavailable")
            targets.append((target,data))
        if len({path for path,_ in targets})!=len(targets):raise NewArtifactTransactionError("target_duplicate")
        staged=[];committed=[]
        try:
            for target,data in targets:
                stage=target.parent/f".{target.name}.dpslab-stage-{uuid.uuid4().hex}"
                with stage.open("xb") as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
                staged.append((stage,target))
            for stage,target in staged:self._replace(str(stage),str(target));committed.append(target)
        except Exception as exc:
            for stage,_ in staged:
                if stage.exists():stage.unlink()
            for target in committed:
                if target.exists():target.unlink()
            raise NewArtifactTransactionError("transaction_rolled_back") from exc
