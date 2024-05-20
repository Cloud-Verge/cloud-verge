import grpc
import logging
import urllib.parse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.sql.expression import func

from models.file import FileData
from models.storage import StorageData

import protos.balancer_pb2 as balancer_pb
import protos.balancer_pb2_grpc as balancer_grpc
import protos.storage_pb2 as storage_pb
import protos.storage_pb2_grpc as storage_grpc


class BalancerServicer(balancer_grpc.BalancerServicer):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.session_maker = session_maker

    async def AskUpload(self, request: balancer_pb.UploadDemand, context) -> balancer_pb.DemandResponse:
        async with self.session_maker() as session:
            async with session.begin():
                storage = await session.execute(
                    select(StorageData).order_by(func.random()).limit(3)
                )
                storages = storage.scalars()

        for storage in storages:
            try:
                async with grpc.aio.insecure_channel(storage.grpc_address) as channel:
                    stub = storage_grpc.StorageStub(channel)
                    response: storage_pb.DemandResponse = await stub.AskUpload(storage_pb.UploadDemand(
                        file_id=request.file_id,
                        tmp_storage_auth=request.tmp_storage_auth,
                    ))
                    if response.status == "ok":
                        return balancer_pb.DemandResponse(
                            status="ok",
                            url=urllib.parse.urljoin(
                                storage.http_address,
                                response.handler
                            )
                        )
                    else:
                        logging.warning(f"AskUpload: Storage(id={storage.id}) answered with '{response.status}'")
            except Exception as ex:
                logging.warning(f"Exception in AskUpload: {ex}")
        else:
            return balancer_pb.DemandResponse(status="No storage node found")

    async def AskDownload(self, request: balancer_pb.DownloadDemand, context) -> balancer_pb.DemandResponse:
        async with self.session_maker() as session:
            async with session.begin():
                file = await session.execute(
                    select(FileData).where(FileData.id == request.file_id)
                )
                file = file.scalar_one_or_none()
                if file is None:
                    return balancer_pb.DemandResponse(status="File not found on the balancer")

                storages = await session.execute(
                    select(StorageData).where(StorageData.id.in_(file.locations.keys()))
                )
                locations = {storage: file.locations[storage.id] for storage in storages.scalars()}

        for storage, localpath in locations.items():
            try:
                async with grpc.aio.insecure_channel(storage.grpc_address) as channel:
                    stub = storage_grpc.StorageStub(channel)
                    response: storage_pb.DemandResponse = await stub.AskDownload(storage_pb.DownloadDemand(
                        localpath=localpath,
                        filename=file.filename,
                        tmp_storage_auth=request.tmp_storage_auth,
                    ))
                    if response.status == "ok":
                        return balancer_pb.DemandResponse(
                            status="ok",
                            url=urllib.parse.urljoin(
                                storage.http_address,
                                response.handler
                            )
                        )
                    else:
                        logging.warning(f"AskDownload: Storage(id={storage.id}) answered with '{response.status}'")
            except Exception as ex:
                logging.warning(f"Exception in AskDownload: {ex}")
        else:
            return balancer_pb.DemandResponse(status="No storage node found")

    async def AskDelete(self, request: balancer_pb.DeleteDemand, context) -> balancer_pb.SimpleResponse:
        async with self.session_maker() as session:
            async with session.begin():
                file = await session.execute(
                    select(FileData).where(FileData.id == request.file_id)
                )
                file = file.scalar_one_or_none()
                if file is None:
                    return balancer_pb.SimpleResponse(status="File not found on the balancer")

                storages = await session.execute(
                    select(StorageData).where(StorageData.id.in_(file.locations.keys()))
                )
                locations = {storage: file.locations[storage.id] for storage in storages.scalars()}

        for storage, localpath in locations.items():
            try:
                async with grpc.aio.insecure_channel(storage.grpc_address) as channel:
                    stub = storage_grpc.StorageStub(channel)
                    response: storage_pb.SimpleResponse = await stub.AskDownload(storage_pb.DeleteDemand(
                        file_id=request.file_id,
                        localpath=localpath,
                    ))
                    if response.status != "ok":
                        logging.warning(f"AskDelete: Storage(id={storage.id}) answered with '{response.status}'")
            except Exception as ex:
                logging.warning(f"Exception in AskDelete: {ex}")
        return balancer_pb.SimpleResponse(status="ok")

    async def FeedStorageEvent(self, request: balancer_pb.StorageEvent, context) -> balancer_pb.SimpleResponse:
        try:
            async with self.session_maker() as session:
                async with session.begin():
                    file = await session.execute(
                        select(FileData).where(FileData.id == request.file_id)
                    )
                    file = file.scalar_one_or_none()
                    if file is None:
                        session.add(FileData(
                            id=request.file_id,
                            filename=request.filename,
                            locations={
                                request.storage_id: request.localpath
                            },
                        ))
                    else:
                        if request.localpath:
                            file.locations[request.storage_id] = request.localpath
                        else:
                            file.locations.pop(request.storage_id, None)
                    await session.commit()
        except Exception as ex:
            return balancer_pb.SimpleResponse(status=str(ex))
        return balancer_pb.SimpleResponse(status="ok")
