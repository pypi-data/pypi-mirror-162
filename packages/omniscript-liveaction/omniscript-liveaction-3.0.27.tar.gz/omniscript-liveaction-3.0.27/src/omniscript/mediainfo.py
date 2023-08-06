"""MediaInfo class.
"""
#Copyright (c) LiveAction, Inc. 2022. All rights reserved.
#Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
#Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from .invariant import MEDIA_DOMAIN_NONE, MEDIA_TYPE_802_3, \
    MEDIA_SUB_TYPE_NATIVE, MEDIA_SUB_TYPE_NATIVE

from .omniid import OmniId

_mediainfo_prop_dict = {
    'clsid' : 'class_id',
    'linkSpeed' : 'link_speed',
    'mediaDomain' : 'domain',
    'mediaSubType' : 'media_sub_type',
    'mediaType' : 'media_type'
}


class MediaInfo(object):
    """The MediaInfo class.
    """

    class_id = None
    """The class id of the Media Info object."""

    domain = MEDIA_DOMAIN_NONE
    """The media domain, one of the MEDIA_DOMAIN constants."""

    link_speed = 0
    """The media's link speed in bits per second."""

    media_type = MEDIA_TYPE_802_3
    """The media type, one of the MEDIA_TYPE constants."""

    media_sub_type = MEDIA_SUB_TYPE_NATIVE
    """The media sub type, one of the MEDIA_SUB_TYPE constants."""

    def __init__(self, props=None):
        self.class_id = MediaInfo.class_id
        self.link_speed = MediaInfo.link_speed
        self.domain = MediaInfo.domain
        self.media_type = MediaInfo.media_type
        self.media_sub_type = MediaInfo.media_sub_type
        #
        self.load(props)

    def __str__(self):
        return f'MediaInfo: {self.media_type}'

    def load(self, props):
        if isinstance(props, dict):
            for k,v in props.items():
                a = _mediainfo_prop_dict.get(k)
                if a is not None:
                    if hasattr(self, a):
                        if isinstance(getattr(self, a), int):
                            setattr(self, a, int(v) if v else 0)
                        elif getattr(self, a) is None:
                            if (a == 'class_id'):
                                setattr(self, a, OmniId(v))
