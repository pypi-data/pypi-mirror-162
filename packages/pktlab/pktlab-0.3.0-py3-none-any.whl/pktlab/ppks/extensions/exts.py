#
# Python3 script for custom cryptography extension definitions and helper functions.
# By TB Yan
# Last updated: 2022/05/17
#

from asn1tools import compile_string
from cryptography.x509 import \
    UnrecognizedExtension, ObjectIdentifier

from ..PacketLabConstants import PacketLabConstants as pconst
from .._utils import get_cert_type_str, is_good_del_type

class PacketLabCertificateDescription(UnrecognizedExtension):
    def __init__(self, description):
        spec = compile_string(
            pconst.PKTLAB_EXT_ASN1_SPEC, codec="der")
        der_value = bytes(spec.encode("PacketLabCertificateDescription", description.encode("utf-8")))
        oid = ObjectIdentifier(pconst.PKTLAB_EXT_CERT_DESCRIPTION)
        super().__init__(oid=oid, value=der_value)

class PacketLabCertType(UnrecognizedExtension):
    def __init__(self, ct):
        num_set = {
            pconst.PKTLAB_CERT_SUBCMD,
            pconst.PKTLAB_CERT_PUBCMD,
            pconst.PKTLAB_CERT_EXPPRIV,
            pconst.PKTLAB_CERT_DELPRIV,
            pconst.PKTLAB_CERT_AGENT}
        name_set = {*[get_cert_type_str(i) for i in num_set]}

        if ct not in name_set and ct not in num_set:
            raise ValueError("Unknown PacketLab certificate type ({}).".format(ct))

        if not isinstance(ct, str):
            ct = get_cert_type_str(ct)

        spec = compile_string(
            pconst.PKTLAB_EXT_ASN1_SPEC, codec="der")
        der_value = bytes(spec.encode("PacketLabCertificateType", ct.encode("utf-8")))
        oid = ObjectIdentifier(pconst.PKTLAB_EXT_CERT_TYPE)
        super().__init__(oid=oid, value=der_value)

class PacketLabFilterDigests(UnrecognizedExtension):
    def __init__(self, filter_digest_ls):
        if filter_digest_ls is None or len(filter_digest_ls) == 0:
            raise ValueError("No filter digest provided.")

        if len(filter_digest_ls) % pconst.PKTLAB_FILTER_DIGEST_LEN != 0:
            raise ValueError("Invalid digests length.")

        spec = compile_string(
            pconst.PKTLAB_EXT_ASN1_SPEC, codec="der")
        der_value = bytes(spec.encode("PacketLabFilterDigests", filter_digest_ls))
        oid = ObjectIdentifier(pconst.PKTLAB_EXT_FILTER_DIGESTS)
        super().__init__(oid=oid, value=der_value)

class PacketLabMonitorDigests(UnrecognizedExtension):
    def __init__(self, monitor_digest_ls):
        if monitor_digest_ls is None or len(monitor_digest_ls) == 0:
            raise ValueError("No monitor digest provided.")

        if len(monitor_digest_ls) % pconst.PKTLAB_MONITOR_DIGEST_LEN != 0:
            raise ValueError("Invalid digests length.")

        spec = compile_string(
            pconst.PKTLAB_EXT_ASN1_SPEC, codec="der")
        der_value = bytes(spec.encode("PacketLabMonitorDigests", monitor_digest_ls))
        oid = ObjectIdentifier(pconst.PKTLAB_EXT_MONITOR_DIGESTS)
        super().__init__(oid=oid, value=der_value)

class PacketLabPriority(UnrecognizedExtension):
    def __init__(self, priority):
        spec = compile_string(
            pconst.PKTLAB_EXT_ASN1_SPEC, codec="der")
        der_value = bytes(spec.encode("PacketLabPriority", priority.encode("utf-8")))
        oid = ObjectIdentifier(pconst.PKTLAB_EXT_PRIORITY)
        super().__init__(oid=oid, value=der_value)

class PacketLabDelegationType(UnrecognizedExtension):
    def __init__(self, dt):
        if dt is None:
            raise ValueError("No delegation type provided.")

        if not is_good_del_type(dt):
            raise ValueError("Bad delegation type: {}".format(dt))

        spec = compile_string(
            pconst.PKTLAB_EXT_ASN1_SPEC, codec="der")
        der_value = bytes(spec.encode("PacketLabDelegationType", dt))
        oid = ObjectIdentifier(pconst.PKTLAB_EXT_DEL_TYPE)
        super().__init__(oid=oid, value=der_value)

# extension not used anymore, but regex pattern may be useful afterwards
#class PacketLabUniformResourceIdentifier(UniformResourceIdentifier):
#    def __init__(self, uri):
#        if re.match("^pktlab:\/\/([a-zA-z0-9.-]+)(:[0-9]{1,5})?\/(exp|broker)\/$", uri) is None:
#            raise ValueError("Bad URI")
#        super().__init__(value=uri)

#
# UTILITY METHOD DEFINITIONS
#

def pktlab_ext_get_bytes(ext, oidstr=None):
    if ext is None: return None
    if oidstr is None: oidstr = ext.oid.dotted_string

    if oidstr == pconst.PKTLAB_EXT_CERT_TYPE:
        name = "PacketLabCertificateType"
    elif oidstr == pconst.PKTLAB_EXT_CERT_DESCRIPTION:
        name = "PacketLabCertificateDescription"
    elif oidstr == pconst.PKTLAB_EXT_FILTER_DIGESTS:
        name = "PacketLabFilterDigests"
    elif oidstr == pconst.PKTLAB_EXT_MONITOR_DIGESTS:
        name = "PacketLabMonitorDigests"
    elif oidstr == pconst.PKTLAB_EXT_PRIORITY:
        name = "PacketLabPriority"
    elif oidstr == pconst.PKTLAB_EXT_DEL_TYPE:
        name = "PacketLabDelegationType"
    else:
        raise ValueError("Unknown pktlab extension OID")

    spec = compile_string(
        pconst.PKTLAB_EXT_ASN1_SPEC, codec="der")
    return spec.decode(name, ext.value.value, check_constraints=True)