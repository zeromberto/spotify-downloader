from ..mopidy_api import MopidyWSController


class PlaylistsController(MopidyWSController):
    ''' Auto-generated PlaylistsController Class for Mopidy JSON/RPC API version 2.2.2'''


    def delete(self, uri, **options):
        '''Delete playlist identified by the URI.
        If the URI doesn't match the URI schemes handled by the current
        backends, nothing happens.
        Returns :class:`True` if deleted, :class:`False` otherwise.
        :param uri: URI of the playlist to delete
        :type uri: string
        :rtype: :class:`bool`
        .. versionchanged:: 2.2
            Return type defined.
        '''
        return self.mopidy_request('core.playlists.delete', uri=uri, **options)

    def refresh(self, uri_scheme=None, **options):
        '''Refresh the playlists in :attr:`playlists`.
        If ``uri_scheme`` is :class:`None`, all backends are asked to refresh.
        If ``uri_scheme`` is an URI scheme handled by a backend, only that
        backend is asked to refresh. If ``uri_scheme`` doesn't match any
        current backend, nothing happens.
        :param uri_scheme: limit to the backend matching the URI scheme
        :type uri_scheme: string
        '''
        return self.mopidy_request('core.playlists.refresh', uri_scheme=uri_scheme, **options)

    def create(self, name, uri_scheme=None, **options):
        '''Create a new playlist.
        If ``uri_scheme`` matches an URI scheme handled by a current backend,
        that backend is asked to create the playlist. If ``uri_scheme`` is
        :class:`None` or doesn't match a current backend, the first backend is
        asked to create the playlist.
        All new playlists must be created by calling this method, and **not**
        by creating new instances of :class:`mopidy.models.Playlist`.
        :param name: name of the new playlist
        :type name: string
        :param uri_scheme: use the backend matching the URI scheme
        :type uri_scheme: string
        :rtype: :class:`mopidy.models.Playlist` or :class:`None`
        '''
        return self.mopidy_request('core.playlists.create', name=name, uri_scheme=uri_scheme, **options)

    # DEPRECATED
    def filter(self, criteria=None, **options):
        '''Filter playlists by the given criterias.
        Examples::
            # Returns track with name 'a'
            filter({'name': 'a'})
            # Returns track with URI 'xyz'
            filter({'uri': 'xyz'})
            # Returns track with name 'a' and URI 'xyz'
            filter({'name': 'a', 'uri': 'xyz'})
        :param criteria: one or more criteria to match by
        :type criteria: dict
        :rtype: list of :class:`mopidy.models.Playlist`
        .. deprecated:: 1.0
            Use :meth:`as_list` and filter yourself.
        '''
        return self.mopidy_request('core.playlists.filter', criteria=criteria, **options)

    def as_list(self, **options):
        '''Get a list of the currently available playlists.
        Returns a list of :class:`~mopidy.models.Ref` objects referring to the
        playlists. In other words, no information about the playlists' content
        is given.
        :rtype: list of :class:`mopidy.models.Ref`
        .. versionadded:: 1.0
        '''
        return self.mopidy_request('core.playlists.as_list', **options)

    def get_uri_schemes(self, **options):
        '''Get the list of URI schemes that support playlists.
        :rtype: list of string
        .. versionadded:: 2.0
        '''
        return self.mopidy_request('core.playlists.get_uri_schemes', **options)

    def get_items(self, uri, **options):
        '''Get the items in a playlist specified by ``uri``.
        Returns a list of :class:`~mopidy.models.Ref` objects referring to the
        playlist's items.
        If a playlist with the given ``uri`` doesn't exist, it returns
        :class:`None`.
        :rtype: list of :class:`mopidy.models.Ref`, or :class:`None`
        .. versionadded:: 1.0
        '''
        return self.mopidy_request('core.playlists.get_items', uri=uri, **options)

    def save(self, playlist, **options):
        '''Save the playlist.
        For a playlist to be saveable, it must have the ``uri`` attribute set.
        You must not set the ``uri`` atribute yourself, but use playlist
        objects returned by :meth:`create` or retrieved from :attr:`playlists`,
        which will always give you saveable playlists.
        The method returns the saved playlist. The return playlist may differ
        from the saved playlist. E.g. if the playlist name was changed, the
        returned playlist may have a different URI. The caller of this method
        must throw away the playlist sent to this method, and use the
        returned playlist instead.
        If the playlist's URI isn't set or doesn't match the URI scheme of a
        current backend, nothing is done and :class:`None` is returned.
        :param playlist: the playlist
        :type playlist: :class:`mopidy.models.Playlist`
        :rtype: :class:`mopidy.models.Playlist` or :class:`None`
        '''
        return self.mopidy_request('core.playlists.save', playlist=playlist, **options)

    def lookup(self, uri, **options):
        '''Lookup playlist with given URI in both the set of playlists and in any
        other playlist sources. Returns :class:`None` if not found.
        :param uri: playlist URI
        :type uri: string
        :rtype: :class:`mopidy.models.Playlist` or :class:`None`
        '''
        return self.mopidy_request('core.playlists.lookup', uri=uri, **options)

    # DEPRECATED
    def get_playlists(self, include_tracks=True, **options):
        '''Get the available playlists.
        :rtype: list of :class:`mopidy.models.Playlist`
        .. versionchanged:: 1.0
            If you call the method with ``include_tracks=False``, the
            :attr:`~mopidy.models.Playlist.last_modified` field of the returned
            playlists is no longer set.
        .. deprecated:: 1.0
            Use :meth:`as_list` and :meth:`get_items` instead.
        '''
        return self.mopidy_request('core.playlists.get_playlists', include_tracks=include_tracks, **options)