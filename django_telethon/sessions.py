import logging

from django.core.exceptions import ObjectDoesNotExist
from telethon import utils
from telethon.crypto import AuthKey
from telethon.sessions import MemorySession
from telethon.tl import types
from telethon.tl.types import InputDocument, InputPhoto, PeerChannel, PeerChat, PeerUser

from .models import ClientSession, Entity, Session, UpdateState
from .models.sentfiles import SentFileType

"""
Read the following carefully before changing anything in this file.
https://github.com/LonamiWebs/Telethon/blob/master/telethon/sessions.py
"""


class DjangoSession(MemorySession):
    """This session contains the required information to login into your
    Telegram account. NEVER give the saved session file to anyone, since
    they would gain instant access to all your messages and contacts.

    If you think the session has been compromised, close all the sessions
    through an official Telegram client to revoke the authorization.
    """

    def __init__(self, client_session: ClientSession, *args, **kwargs):
        self.save_entities = True
        super().__init__()
        self.client_session = client_session
        if hasattr(self.client_session, 'session'):
            session = self.client_session.session
            self._dc_id = session.data_center_id
            self._server_address = session.server_address
            self._port = session.port
            self._takeout_id = session.takeout_id
            auth_key = session.auth_key
            if isinstance(auth_key, memoryview):
                auth_key = auth_key.tobytes()
            self._auth_key = AuthKey(data=auth_key)
        else:
            self._auth_key = None

    def clone(self, to_instance=None):
        cloned = super().clone(to_instance)
        cloned.save_entities = self.save_entities
        return cloned

    # Data from sessions should be kept as properties
    # not to fetch the database every time we need it
    def set_dc(self, dc_id, server_address, port):
        super().set_dc(dc_id, server_address, port)
        self._update_session_table()
        # Fetch the auth_key corresponding to this data center
        try:
            session = Session.objects.get(client_session=self.client_session)
            auth_key = session.auth_key
            if isinstance(auth_key, memoryview):
                auth_key = auth_key.tobytes()
        except ObjectDoesNotExist:
            auth_key = None
        self._auth_key = AuthKey(data=auth_key) if auth_key else None

    @MemorySession.auth_key.setter
    def auth_key(self, value):
        if value == self._auth_key:
            return
        self._auth_key = value
        self._update_session_table()

    @MemorySession.takeout_id.setter
    def takeout_id(self, value):
        self._takeout_id = value
        if value == self._takeout_id:
            return
        self._update_session_table()

    def _update_session_table(self):
        # While we can save multiple rows into the sessions table
        # currently we only want to keep ONE as the tables don't
        # tell us which auth_key's are usable and will work. Needs
        # some more work before being able to save auth_key's for
        # multiple DCs. Probably done differently.
        defaults = {
            'data_center_id': self._dc_id,
            'server_address': self._server_address,
            'port': self._port,
            'auth_key': self._auth_key.key if self._auth_key else b'',
            'takeout_id': self._takeout_id,
        }
        Session.objects.update_or_create(
            client_session=self.client_session,
            defaults=defaults,
        )

    def get_update_state(self, entity_id):
        try:
            state = self.client_session.updatestate_set.get(pk=entity_id)
            return types.updates.State(state.pts, state.qts, state.date, state.seq, unread_count=0)
        except UpdateState.DoesNotExist:
            return None

    def set_update_state(self, entity_id, state):
        self.client_session.updatestate_set.update_or_create(
            pk=entity_id,
            defaults={
                'pts': state.pts,
                'qts': state.qts,
                'date': state.date,
                'seq': state.seq,
            },
        )

    def save(self):
        """Saves the current session object as session_user_id.session"""
        # This is a no-op if there are no changes to commit, so there's
        # no need for us to keep track of an "unsaved changes" variable.
        pass

    def delete(self):

        """Deletes the current session file"""
        try:
            self.client_session.delete()
            return True
        except Exception:
            logging.exception('Failed to delete session')
            return False

    @classmethod
    def list_sessions(cls):

        """Lists all the sessions of the users who have ever connected
        using this client and never logged out
        """
        return ClientSession.objects.all().values_list('name', flat=True)

    # Entity processing

    def process_entities(self, tlo):
        """
        Processes all the found entities on the given TLObject,
        unless .save_entities is False.
        """
        self._process_entities(tlo)

    def _process_entities(self, tlo):
        if not self.save_entities:
            return

        rows = self._entities_to_rows(tlo)
        if not rows:
            return

        entities = self.client_session.entity_set.filter(entity_id__in=[row[0] for row in rows])
        entities_does_not_exists = []
        for row in rows:
            is_find = False
            for entity in entities:
                if entity.entity_id == row[0]:
                    is_find = True
                    entity.hash_value = row[1]
                    entity.username = row[2]
                    entity.phone = row[3]
                    entity.name = row[4]
            if not is_find:
                entities_does_not_exists.append(
                    Entity(
                        entity_id=row[0],
                        client_session=self.client_session,
                        hash_value=row[1],
                        username=row[2],
                        phone=row[3],
                        name=row[4],
                    )
                )
        self.client_session.entity_set.bulk_update(entities, ['hash_value', 'username', 'phone', 'name'])
        self.client_session.entity_set.bulk_create(entities_does_not_exists)

    def get_entity_rows_by_phone(self, phone):

        return self.client_session.entity_set.filter(phone=phone).values_list('entity_id', 'hash_value').first()

    def get_entity_rows_by_username(self, username):

        queryset = list(self.client_session.entity_set.filter(username=username).order_by('-date'))
        if len(queryset) > 1:
            # If there is more than one result for the same username, evict the oldest one
            logging.warning('Found more than one entity with username %s', username)
            self.client_session.entity_set.filter(entity_id__in=[obj.entity_id for obj in queryset[1:]]).update(
                username=None
            )
        if not queryset:
            return None
        return queryset[0].entity_id, queryset[0].hash_value

    def get_entity_rows_by_name(self, name):

        return self.client_session.entity_set.filter(name=name).values_list('entity_id', 'hash_value').first()

    def get_entity_rows_by_id(self, id, exact=True):

        if exact:
            return self.client_session.entity_set.filter(entity_id=id).values_list('entity_id', 'hash_value').first()
        else:
            return (
                self.client_session.entity_set.filter(
                    entity_id__in=[
                        utils.get_peer_id(PeerUser(id)),
                        utils.get_peer_id(PeerChat(id)),
                        utils.get_peer_id(PeerChannel(id)),
                    ]
                )
                .values_list('entity_id', 'hash_value')
                .first()
            )

    # File processing

    def get_file(self, md5_digest, file_size, cls):

        if (
            row := self.client_session.sentfile_set.filter(
                md5_digest=md5_digest, file_size=file_size, file_type=SentFileType.from_type(cls).value
            )
            .values_list('pk', 'hash_value')
            .first()
        ):
            # Both allowed classes have (id, access_hash) as parameters
            return cls(row[0], row[1])

    def cache_file(self, md5_digest, file_size, instance):

        if not isinstance(instance, (InputDocument, InputPhoto)):
            raise TypeError(f'Cannot cache {type(instance)} instance')
        self.client_session.sentfile_set.update_or_create(
            md5_digest=md5_digest,
            file_size=file_size,
            file_type=SentFileType.from_type(type(instance)).value,
            defaults={'hash_value': instance.access_hash, 'file_id': instance.id},
        )
