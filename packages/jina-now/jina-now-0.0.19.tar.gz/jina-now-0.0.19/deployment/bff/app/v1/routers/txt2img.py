import base64
from typing import List

from docarray import Document, DocumentArray
from fastapi import APIRouter

from deployment.bff.app.v1.models.image import (
    NowImageIndexRequestModel,
    NowImageResponseModel,
)
from deployment.bff.app.v1.models.text import NowTextSearchRequestModel
from deployment.bff.app.v1.routers.helper import get_jina_client, process_query

router = APIRouter()


# Index
@router.post(
    "/index",
    summary='Add more image data to the indexer',
)
def index(data: NowImageIndexRequestModel):
    """
    Append the list of image data to the indexer. Each image data should be
    `base64` encoded using human-readable characters - `utf-8`.
    """
    index_docs = DocumentArray()
    jwt = data.jwt
    for image, tags in zip(data.images, data.tags):
        base64_bytes = image.encode('utf-8')
        message = base64.decodebytes(base64_bytes)
        index_docs.append(Document(blob=message, tags=tags))

    get_jina_client(data.host, data.port).post(
        '/index', index_docs, parameters={'jwt': jwt}
    )


# Search
@router.post(
    "/search",
    response_model=List[NowImageResponseModel],
    summary='Search image data via text as query',
)
def search(data: NowTextSearchRequestModel):
    """
    Retrieve matching images for a given text as query.
    """
    query_doc = process_query(text=data.text)
    jwt = data.jwt
    docs = get_jina_client(data.host, data.port).post(
        '/search',
        query_doc,
        parameters={"limit": data.limit, 'jwt': jwt},
    )
    return docs[0].matches.to_dict()
