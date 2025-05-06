import os
import json
import uuid
import dataclasses
from grpc import ServicerContext
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakGetError
from src.proxyproto.proxyproto_pb2_grpc import CentrifugoProxyServicer
from src.proxyproto.proxyproto_pb2 import (
    PublishRequest,
    PublishResponse,
    PublishResult,
    SubscribeRequest,
    SubscribeResponse,
    SubscribeResult,
    RPCRequest,
    RPCResponse,
    RPCResult,
    Error
)

from src.database.channel import Querier, models, CreateUserParams
from src.database.engine import engine

class CentrifugoHandler(CentrifugoProxyServicer):
    def __init__(self):
        self._conn = engine.connect()
        self.querier = Querier(self._conn)
        self.keycloak_admin = KeycloakAdmin(
            server_url=os.getenv('KEYCLOAK_SERVER_URL'),
            username=os.getenv('KEYCLOAK_ADMIN_USER'),
            password=os.getenv('KEYCLOAK_ADMIN_PASSWORD'),
            realm_name=os.getenv('KEYCLOAK_REALM'),
            client_id=os.getenv('KEYCLOAK_CLIENT_ID'),
            client_secret_key=os.getenv('KEYCLOAK_CLIENT_SECRET'),
            verify=True
        )

    def _get_or_create_user(self, user_id: str) -> models.User:
        """Получаем или создаем пользователя в БД и Keycloak"""
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise ValueError("Invalid user ID format")

        # Проверяем существование в БД
        db_user = self.querier.get_user_by_id(id=user_uuid)
        if db_user:
            return db_user

        # Если нет в БД - проверяем в Keycloak и создаем
        try:
            kc_user = self.keycloak_admin.get_user(user_id, True)
        except KeycloakGetError:
            raise PermissionError("User not found in Keycloak")

        # Создаем в БД
        new_user = CreateUserParams(
            id=user_uuid,
            username=kc_user['username'],
            given_name=kc_user.get('firstName', ''),
            family_name=kc_user.get('lastName', ''),
            enabled=kc_user['enabled']
        )
        self.querier.create_user(new_user)
        self._conn.commit()
        return models.User(**dataclasses.asdict(new_user))

    def _check_publish_permission(self, user_id: str, channel: str) -> bool:
        """Проверка прав на публикацию в канал"""
        try:
            user = self._get_or_create_user(user_id)
            if not user.enabled:
                return False

            
            return self.querier.user_can_publish(id=user_id, channel=channel) or False

        except Exception as e:
            print(f"Publish permission check failed: {e}")
            return False

    def _check_subscription_permission(self, user_id: str, channel: str) -> bool:
        """Проверка прав на подписку"""
        try:
            user = self._get_or_create_user(user_id)
            if not user.enabled:
                return False

            # Получаем список каналов пользователя
            for user_channel in self.querier.chan_list_by_user_id(user_id=user.id):
                if user_channel.channel == channel:
                    return True
            return False

        except Exception as e:
            print(f"Subscription permission check failed: {e}")
            return False

    def Publish(self, request: PublishRequest, context: ServicerContext) -> PublishResponse:
        try:
            if not self._check_publish_permission(request.user, request.channel):
                return PublishResponse(
                    error=Error(code=403, message="Publish forbidden", temporary=False)
                )

            # Остальная логика публикации...
            return PublishResponse(result=PublishResult())

        except Exception as e:
            return PublishResponse(
                error=Error(code=500, message=str(e), temporary=True)
            )

    def Subscribe(self, request: SubscribeRequest, context: ServicerContext) -> SubscribeResponse:
        try:
            if not self._check_subscription_permission(request.user, request.channel):
                return SubscribeResponse(
                    error=Error(code=403, message="Subscription forbidden", temporary=False)
                )

            return SubscribeResponse(result=SubscribeResult())

        except Exception as e:
            return SubscribeResponse(
                error=Error(code=500, message=str(e), temporary=True)
            )
# дополнительное для вывода доступных пользователю каналов.    
    def RPC(self, request: RPCRequest, context: ServicerContext) -> RPCResponse:
        try:
            if request.method == "get_channels":
                user = self._get_or_create_user(request.user)
                channels = [
                    channel.channel 
                    for channel in self.querier.chan_list_by_user_id(user_id=user.id)
                ]
                data = json.dumps({"channels": channels}).encode()
                return RPCResponse(
                    result=RPCResult(data=data)
                )
            
            return RPCResponse(
                error=Error(code=404, message="Method not found")
            )

        except Exception as e:
            return RPCResponse(
                error=Error(code=500, message=str(e), temporary=True
            ))