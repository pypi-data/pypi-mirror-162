#
# Python3 script for pktlab constants.
# By TB Yan
# Last updated: 2022/05/17
#

# CLASS DEFINITIONS
#

#
# pktlab (cert) constants
# todo: import them from pktlab.h header with cython
# todo: add rlimits (probably a general attribute type will be better)
# todo: add filter monitor type
#

class PacketLabConstants:
    PKTLAB_SHA256_DIGEST_LEN  = 32
    PKTLAB_KEYID_LEN          = PKTLAB_SHA256_DIGEST_LEN
    PKTLAB_FILTER_DIGEST_LEN  = PKTLAB_SHA256_DIGEST_LEN
    PKTLAB_MONITOR_DIGEST_LEN = PKTLAB_SHA256_DIGEST_LEN

    # X.509 Private Extension OIDs
    PKTLAB_EXT_CERT_TYPE             = "1.2.3.1"
    PKTLAB_EXT_CERT_DESCRIPTION      = "1.2.3.3"
    PKTLAB_EXT_FILTER_DIGESTS        = "1.2.3.5"
    PKTLAB_EXT_MONITOR_DIGESTS       = "1.2.3.6"
    PKTLAB_EXT_PRIORITY              = "1.2.3.7"
    PKTLAB_EXT_DEL_TYPE              = "1.2.3.8"

    # Certificate Type Value
    PKTLAB_CERT_SUBCMD    = 0
    PKTLAB_CERT_PUBCMD    = 1
    PKTLAB_CERT_EXPPRIV   = 2
    PKTLAB_CERT_DELPRIV   = 3
    PKTLAB_CERT_AGENT     = 4
    PKTLAB_CERT_UNKNOWN   = 127 # unknown is not really a cert type
    PKTLAB_MIN_CERT_TYPE  = PKTLAB_CERT_SUBCMD
    PKTLAB_MAX_CERT_TYPE  = PKTLAB_CERT_AGENT

    PKTLAB_CERTTYPE_STR_SUBCMD   = "subcmd"
    PKTLAB_CERTTYPE_STR_PUBCMD   = "pubcmd"
    PKTLAB_CERTTYPE_STR_EXPPRIV  = "exppriv"
    PKTLAB_CERTTYPE_STR_DELPRIV  = "delpriv"
    PKTLAB_CERTTYPE_STR_AGENT    = "agent"
    PKTLAB_CERTTYPE_STR_UNKNOWN  = "unknown"

    PKTLAB_DEL_TYPE_EXPPRIV = 0x1
    PKTLAB_DEL_TYPE_REPPRIV = 0x2

    PKTLAB_EXT_ASN1_SPEC  = \
"""
PacketLabExtensions DEFINITIONS ::=
BEGIN

    -- PacketLab Certificate Type --
    PacketLabCertificateType ::= OCTET STRING (SIZE(1..MAX))

    -- PacketLab Certificate Description --
    PacketLabCertificateDescription ::= OCTET STRING (SIZE(1..MAX))

    -- PacketLab Filter Digests --
    PacketLabFilterDigests ::= OCTET STRING (SIZE(1..MAX))

    -- PacketLab Monitor Digests --
    PacketLabMonitorDigests ::= OCTET STRING (SIZE(1..MAX))

    -- PacketLab Priority --
    PacketLabPriority ::= OCTET STRING (SIZE(1..MAX))

    -- PacketLab Delegation Type --
    PacketLabDelegationType ::= OCTET STRING (SIZE(1))
END
"""