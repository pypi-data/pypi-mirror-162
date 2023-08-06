import json
from typing import Optional

from aiogoogle import GoogleAPI
from pydantic import create_model
from tygle.base import REST
from tygle.base.requests import DataRequest
from tygle.client import Client
from tygle_docs.base import BatchUpdateRequest
from tygle_docs.types.enums import SuggestionsViewMode
from tygle_docs.types.requests import BatchUpdateBody
from tygle_docs.types.resources import Document, DocumentRESTs
from tygle_docs.types.responses import BatchUpdateResponse


class Documents(REST):
    def __init__(self, client: Client, parent: GoogleAPI):
        self.Document = create_model("Document", __base__=Document)
        self.Document.__rests__ = DocumentRESTs(self)
        super().__init__(client, parent)

    def batch_update(
        self, document_id: str, /, batch_update_body: BatchUpdateBody
    ) -> BatchUpdateRequest[BatchUpdateResponse]:
        return BatchUpdateRequest(
            self.client,
            self.parent.docs.batchUpdate(
                documentId=document_id,
                json=json.loads(batch_update_body.json()),
            ),
            BatchUpdateResponse,
            batch_update_body,
        )

    def create(self, document: Optional[Document] = None) -> DataRequest[Document]:
        return DataRequest(
            self.client,
            self.parent.docs.create(
                json=json.loads(document.json()) if document else None,
            ),
            self.Document,
        )

    def get(
        self,
        document_id: str,
        /,
        *,
        suggestions_view_mode: Optional[SuggestionsViewMode] = None,
    ) -> DataRequest[Document]:
        return DataRequest(
            self.client,
            self.parent.docs.get(
                documentId=document_id,
                suggestionsViewMode=suggestions_view_mode,
            ),
            self.Document,
        )
