# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['DomainCertificateArgs', 'DomainCertificate']

@pulumi.input_type
class DomainCertificateArgs:
    def __init__(__self__, *,
                 certificate: pulumi.Input[str],
                 certificate_chain: pulumi.Input[str],
                 domain_id: pulumi.Input[str],
                 private_key: pulumi.Input[str],
                 type: pulumi.Input[str]):
        """
        The set of arguments for constructing a DomainCertificate resource.
        :param pulumi.Input[str] certificate: Certificate content.
        :param pulumi.Input[str] certificate_chain: Certificate certificate chain.
        :param pulumi.Input[str] domain_id: Domain ID.
        :param pulumi.Input[str] private_key: Certificate private key.
        :param pulumi.Input[str] type: Certificate type. Valid value is `"PEM"`.
        """
        pulumi.set(__self__, "certificate", certificate)
        pulumi.set(__self__, "certificate_chain", certificate_chain)
        pulumi.set(__self__, "domain_id", domain_id)
        pulumi.set(__self__, "private_key", private_key)
        pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter
    def certificate(self) -> pulumi.Input[str]:
        """
        Certificate content.
        """
        return pulumi.get(self, "certificate")

    @certificate.setter
    def certificate(self, value: pulumi.Input[str]):
        pulumi.set(self, "certificate", value)

    @property
    @pulumi.getter(name="certificateChain")
    def certificate_chain(self) -> pulumi.Input[str]:
        """
        Certificate certificate chain.
        """
        return pulumi.get(self, "certificate_chain")

    @certificate_chain.setter
    def certificate_chain(self, value: pulumi.Input[str]):
        pulumi.set(self, "certificate_chain", value)

    @property
    @pulumi.getter(name="domainId")
    def domain_id(self) -> pulumi.Input[str]:
        """
        Domain ID.
        """
        return pulumi.get(self, "domain_id")

    @domain_id.setter
    def domain_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "domain_id", value)

    @property
    @pulumi.getter(name="privateKey")
    def private_key(self) -> pulumi.Input[str]:
        """
        Certificate private key.
        """
        return pulumi.get(self, "private_key")

    @private_key.setter
    def private_key(self, value: pulumi.Input[str]):
        pulumi.set(self, "private_key", value)

    @property
    @pulumi.getter
    def type(self) -> pulumi.Input[str]:
        """
        Certificate type. Valid value is `"PEM"`.
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: pulumi.Input[str]):
        pulumi.set(self, "type", value)


@pulumi.input_type
class _DomainCertificateState:
    def __init__(__self__, *,
                 certificate: Optional[pulumi.Input[str]] = None,
                 certificate_chain: Optional[pulumi.Input[str]] = None,
                 domain_id: Optional[pulumi.Input[str]] = None,
                 private_key: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering DomainCertificate resources.
        :param pulumi.Input[str] certificate: Certificate content.
        :param pulumi.Input[str] certificate_chain: Certificate certificate chain.
        :param pulumi.Input[str] domain_id: Domain ID.
        :param pulumi.Input[str] private_key: Certificate private key.
        :param pulumi.Input[str] type: Certificate type. Valid value is `"PEM"`.
        """
        if certificate is not None:
            pulumi.set(__self__, "certificate", certificate)
        if certificate_chain is not None:
            pulumi.set(__self__, "certificate_chain", certificate_chain)
        if domain_id is not None:
            pulumi.set(__self__, "domain_id", domain_id)
        if private_key is not None:
            pulumi.set(__self__, "private_key", private_key)
        if type is not None:
            pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter
    def certificate(self) -> Optional[pulumi.Input[str]]:
        """
        Certificate content.
        """
        return pulumi.get(self, "certificate")

    @certificate.setter
    def certificate(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "certificate", value)

    @property
    @pulumi.getter(name="certificateChain")
    def certificate_chain(self) -> Optional[pulumi.Input[str]]:
        """
        Certificate certificate chain.
        """
        return pulumi.get(self, "certificate_chain")

    @certificate_chain.setter
    def certificate_chain(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "certificate_chain", value)

    @property
    @pulumi.getter(name="domainId")
    def domain_id(self) -> Optional[pulumi.Input[str]]:
        """
        Domain ID.
        """
        return pulumi.get(self, "domain_id")

    @domain_id.setter
    def domain_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "domain_id", value)

    @property
    @pulumi.getter(name="privateKey")
    def private_key(self) -> Optional[pulumi.Input[str]]:
        """
        Certificate private key.
        """
        return pulumi.get(self, "private_key")

    @private_key.setter
    def private_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "private_key", value)

    @property
    @pulumi.getter
    def type(self) -> Optional[pulumi.Input[str]]:
        """
        Certificate type. Valid value is `"PEM"`.
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "type", value)


class DomainCertificate(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 certificate: Optional[pulumi.Input[str]] = None,
                 certificate_chain: Optional[pulumi.Input[str]] = None,
                 domain_id: Optional[pulumi.Input[str]] = None,
                 private_key: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages certificate for the domain.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_okta as okta

        example = okta.Domain("example")
        test = okta.DomainCertificate("test",
            domain_id=okta_domain["test"]["id"],
            type="PEM",
            certificate=\"\"\"-----BEGIN CERTIFICATE-----
        MIIFNzCCBB+gAwIBAgISBAXomJWRama3ypu8TIxdA9wzMA0GCSqGSIb3DQEBCwUA
        MDIxCzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MQswCQYDVQQD
        EwJSMzAeFw0yMTAyMTAwNTEzMDVaFw0yMTA1MTEwNTEzMDVaMCQxIjAgBgNVBAMT
        GWFuaXRhdGVzdC5zaWdtYW5ldGNvcnAudXMwggEiMA0GCSqGSIb3DQEBAQUAA4IB
        DwAwggEKAoIBAQC5cyk6x63iBJSWvtgsOBqIxfO8euPHcRnyWsL9dsvnbNyOnyvc
        qFWxdiW3sh2cItzYtoN1Zfgj5lWGOVXbHxP0VaNG9fHVX3+NHP6LFHQz92BzAYQm
        pqi9zaP/aKJklk6LdPFbVLGhuZfm34+ijW9YsgLTKR2WTaZJK5QtamVVmP+VsSCl
        a2ifFzjz2FCkMMEc/Y0zUyP+en/mbL71K+VnpZdlEC1s38EvjRTFKFZTKVw5wpWg
        CZQq/AZYj9RxR23IIuRcUJ8TQ2pyoc3kIXPWjiIarSgBlA8G9kCsxgzXP2RyLwKr
        IBIo+qyHweifpPYW28ipdSbPjiypAMdpbGLDAgMBAAGjggJTMIICTzAOBgNVHQ8B
        Af8EBAMCBaAwHQYDVR0lBBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMAwGA1UdEwEB
        /wQCMAAwHQYDVR0OBBYEFPVZKiovtIK4Av/IBUQeLUs29pT6MB8GA1UdIwQYMBaA
        FBQusxe3WFbLrlAJQOYfr52LFMLGMFUGCCsGAQUFBwEBBEkwRzAhBggrBgEFBQcw
        AYYVaHR0cDovL3IzLm8ubGVuY3Iub3JnMCIGCCsGAQUFBzAChhZodHRwOi8vcjMu
        aS5sZW5jci5vcmcvMCQGA1UdEQQdMBuCGWFuaXRhdGVzdC5zaWdtYW5ldGNvcnAu
        dXMwTAYDVR0gBEUwQzAIBgZngQwBAgEwNwYLKwYBBAGC3xMBAQEwKDAmBggrBgEF
        BQcCARYaaHR0cDovL2Nwcy5sZXRzZW5jcnlwdC5vcmcwggEDBgorBgEEAdZ5AgQC
        BIH0BIHxAO8AdgBc3EOS/uarRUSxXprUVuYQN/vV+kfcoXOUsl7m9scOygAAAXeK
        kmOsAAAEAwBHMEUCIQDSudPEWXk969BT8yz3ag6BJWCMRU5tefEw9nXEQMsh5gIg
        UmfGIuUlcNNI5PydVIHj+zns+SR8P7zfd3FIxW4gK0QAdQD2XJQv0XcwIhRUGAgw
        lFaO400TGTO/3wwvIAvMTvFk4wAAAXeKkmOlAAAEAwBGMEQCIHQkr2qOGuInvonv
        W4vvdI61nraax5V6SC3E0D2JSO91AiBVhpX4BBafRAh36r7l8LrxAfxBM3CjBmAC
        q8fUrWfIWDANBgkqhkiG9w0BAQsFAAOCAQEAgGDMKXofKpDdv5kkID3s5GrKdzaj
        jFmb/6kyqd1E6eGXZAewCP1EF5BVvR6lBP2aRXiZ6sJVZktoIfztZnbxBGgbPHfv
        R3iXIG6fxkklzR9Y8puPMBFadANE/QV78tIRAlyaqeSNsoxHi7ssQjHTP111B2lf
        3KmuTpsruut1UesEJcPReLk/1xTkRx262wAncach5Wp+6GWWduTZYJbsNFyrK1RP
        YQ0qYpP9wt2qR+DGaRUBG8i1XLnZS8pkyxtKhVw/a5Fowt+NqCpEBjjJiWJRSGnG
        NSgRtSXq11j8O4JONi8EXe7cEtvzUiLR5PL3itsK2svtrZ9jIwQ95wOPaA==
        -----END CERTIFICATE-----\"\"\",
            private_key=\"\"\"-----BEGIN PRIVATE KEY-----
        MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC5cyk6x63iBJSW
        vtgsOBqIxfO8euPHcRnyWsL9dsvnbNyOnyvcqFWxdiW3sh2cItzYtoN1Zfgj5lWG
        OVXbHxP0VaNG9fHVX3+NHP6LFHQz92BzAYQmpqi9zaP/aKJklk6LdPFbVLGhuZfm
        34+ijW9YsgLTKR2WTaZJK5QtamVVmP+VsSCla2ifFzjz2FCkMMEc/Y0zUyP+en/m
        bL71K+VnpZdlEC1s38EvjRTFKFZTKVw5wpWgCZQq/AZYj9RxR23IIuRcUJ8TQ2py
        oc3kIXPWjiIarSgBlA8G9kCsxgzXP2RyLwKrIBIo+qyHweifpPYW28ipdSbPjiyp
        AMdpbGLDAgMBAAECggEAUXVfT91z6IqghhKwO8QtC5T/+fN06B8rCYSKj/FFoZL0
        0oTiLFuYwImoCadoUDQUE/Efj0rKE2LSgFHg/44IItQXE01m+5WmHmL1ADxsyoLH
        z9yDosKj7jNM7RyV8F8Bg0pL1hU+rU4rhhL/MaS0mx4eFYjC4UmcWBmXTdelSVJa
        kvXvQLT5y86bqh7tqMjM/kALTWRz5CgNJFk/ONA1yo5RTX9S7SIXimBgAvuGqP8i
        MPEhJou7U3DfzXVfvP8byqNdsZs6ZNhG3wXspl61mRyrY+51SOaNLA7Bkji7x4bH
        Nw6mJI0IJTAP9oc1Z8fYeMuxT1bfuD7VOupSP0mAMQKBgQDk+KuyQkmPymeP/Wwu
        II4DUpleVzxTK9obMQQoCEEElbQ6+jTb+8ixP0bWLvBXg/rX734j7OWfn/bljWLH
        XLrSoqQZF1+XMVeY4g4wx9UuTK/D2n791zdOgQivxbIPdWL3a4ap86ar8uyMgJu8
        BLXfFBAOc+9myqUkbeO7wt0e6QKBgQDPV04jPtIJoMrggpQDNreGrANKOmsXWxj4
        OHW13QNdJ2KGQpoTdoqQ8ZmlxuA8Bf2RjHsnB2kgGVTVQR74zRib4MByhvsdhvVm
        F2LNsJoIDfqtv3c+oj13VonRUGuzUeJpwT/snyaL+jQ/ZZcYz0jDgDhIODTcFYj8
        DMSD5SHgywKBgHH6MwWuJ44TNBAiF2qyu959jGjAxf+k0ZI9iRMgYLUWjDvbdtqW
        cCWDGRDfFraJtSEuTz003GzkJPPJuIUC7OCTI1p2HxhU8ITi6itwHfdJJyk4J4TW
        T+qdIqTUpTk6tsPw23zYE3x+lS+viVZDhgEArKl1HpOthh0nMnixnH6ZAoGBAKGn
        V+xy1h9bldFk/TFkP8Jn6ki9MzGKfPVKT7vzDORcCJzU4Hu8OFy5gSmW3Mzvfrsz
        4/CR/oxgM5vwoc0pWr5thJ3GT5K93iYypX3o6q7M91zvonDa3UFl3x2qrc2pUfVS
        DhzWGJ+Z+5JSCnP1aK3EEh18dPoCcELTUYPj6X3xAoGBALAllTb3RCIaqIqk+s3Y
        6KDzikgwGM6j9lmOI2MH4XmCVym4Z40YGK5nxulDh2Ihn/n9zm13Z7ul2DJwgQSO
        0zBc7/CMOsMEBaNXuKL8Qj4enJXMtub4waQ/ywqHIdc50YaPI5Ax8dD/10h9M6Qc
        nUFLNE8pXSnsqb0eOL74f3uQ
        -----END PRIVATE KEY-----\"\"\",
            certificate_chain=(lambda path: open(path).read())("www.example.com/fullchain.pem"))
        ```

        ## Import

        This resource does not support importing.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] certificate: Certificate content.
        :param pulumi.Input[str] certificate_chain: Certificate certificate chain.
        :param pulumi.Input[str] domain_id: Domain ID.
        :param pulumi.Input[str] private_key: Certificate private key.
        :param pulumi.Input[str] type: Certificate type. Valid value is `"PEM"`.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: DomainCertificateArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages certificate for the domain.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_okta as okta

        example = okta.Domain("example")
        test = okta.DomainCertificate("test",
            domain_id=okta_domain["test"]["id"],
            type="PEM",
            certificate=\"\"\"-----BEGIN CERTIFICATE-----
        MIIFNzCCBB+gAwIBAgISBAXomJWRama3ypu8TIxdA9wzMA0GCSqGSIb3DQEBCwUA
        MDIxCzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MQswCQYDVQQD
        EwJSMzAeFw0yMTAyMTAwNTEzMDVaFw0yMTA1MTEwNTEzMDVaMCQxIjAgBgNVBAMT
        GWFuaXRhdGVzdC5zaWdtYW5ldGNvcnAudXMwggEiMA0GCSqGSIb3DQEBAQUAA4IB
        DwAwggEKAoIBAQC5cyk6x63iBJSWvtgsOBqIxfO8euPHcRnyWsL9dsvnbNyOnyvc
        qFWxdiW3sh2cItzYtoN1Zfgj5lWGOVXbHxP0VaNG9fHVX3+NHP6LFHQz92BzAYQm
        pqi9zaP/aKJklk6LdPFbVLGhuZfm34+ijW9YsgLTKR2WTaZJK5QtamVVmP+VsSCl
        a2ifFzjz2FCkMMEc/Y0zUyP+en/mbL71K+VnpZdlEC1s38EvjRTFKFZTKVw5wpWg
        CZQq/AZYj9RxR23IIuRcUJ8TQ2pyoc3kIXPWjiIarSgBlA8G9kCsxgzXP2RyLwKr
        IBIo+qyHweifpPYW28ipdSbPjiypAMdpbGLDAgMBAAGjggJTMIICTzAOBgNVHQ8B
        Af8EBAMCBaAwHQYDVR0lBBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMAwGA1UdEwEB
        /wQCMAAwHQYDVR0OBBYEFPVZKiovtIK4Av/IBUQeLUs29pT6MB8GA1UdIwQYMBaA
        FBQusxe3WFbLrlAJQOYfr52LFMLGMFUGCCsGAQUFBwEBBEkwRzAhBggrBgEFBQcw
        AYYVaHR0cDovL3IzLm8ubGVuY3Iub3JnMCIGCCsGAQUFBzAChhZodHRwOi8vcjMu
        aS5sZW5jci5vcmcvMCQGA1UdEQQdMBuCGWFuaXRhdGVzdC5zaWdtYW5ldGNvcnAu
        dXMwTAYDVR0gBEUwQzAIBgZngQwBAgEwNwYLKwYBBAGC3xMBAQEwKDAmBggrBgEF
        BQcCARYaaHR0cDovL2Nwcy5sZXRzZW5jcnlwdC5vcmcwggEDBgorBgEEAdZ5AgQC
        BIH0BIHxAO8AdgBc3EOS/uarRUSxXprUVuYQN/vV+kfcoXOUsl7m9scOygAAAXeK
        kmOsAAAEAwBHMEUCIQDSudPEWXk969BT8yz3ag6BJWCMRU5tefEw9nXEQMsh5gIg
        UmfGIuUlcNNI5PydVIHj+zns+SR8P7zfd3FIxW4gK0QAdQD2XJQv0XcwIhRUGAgw
        lFaO400TGTO/3wwvIAvMTvFk4wAAAXeKkmOlAAAEAwBGMEQCIHQkr2qOGuInvonv
        W4vvdI61nraax5V6SC3E0D2JSO91AiBVhpX4BBafRAh36r7l8LrxAfxBM3CjBmAC
        q8fUrWfIWDANBgkqhkiG9w0BAQsFAAOCAQEAgGDMKXofKpDdv5kkID3s5GrKdzaj
        jFmb/6kyqd1E6eGXZAewCP1EF5BVvR6lBP2aRXiZ6sJVZktoIfztZnbxBGgbPHfv
        R3iXIG6fxkklzR9Y8puPMBFadANE/QV78tIRAlyaqeSNsoxHi7ssQjHTP111B2lf
        3KmuTpsruut1UesEJcPReLk/1xTkRx262wAncach5Wp+6GWWduTZYJbsNFyrK1RP
        YQ0qYpP9wt2qR+DGaRUBG8i1XLnZS8pkyxtKhVw/a5Fowt+NqCpEBjjJiWJRSGnG
        NSgRtSXq11j8O4JONi8EXe7cEtvzUiLR5PL3itsK2svtrZ9jIwQ95wOPaA==
        -----END CERTIFICATE-----\"\"\",
            private_key=\"\"\"-----BEGIN PRIVATE KEY-----
        MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC5cyk6x63iBJSW
        vtgsOBqIxfO8euPHcRnyWsL9dsvnbNyOnyvcqFWxdiW3sh2cItzYtoN1Zfgj5lWG
        OVXbHxP0VaNG9fHVX3+NHP6LFHQz92BzAYQmpqi9zaP/aKJklk6LdPFbVLGhuZfm
        34+ijW9YsgLTKR2WTaZJK5QtamVVmP+VsSCla2ifFzjz2FCkMMEc/Y0zUyP+en/m
        bL71K+VnpZdlEC1s38EvjRTFKFZTKVw5wpWgCZQq/AZYj9RxR23IIuRcUJ8TQ2py
        oc3kIXPWjiIarSgBlA8G9kCsxgzXP2RyLwKrIBIo+qyHweifpPYW28ipdSbPjiyp
        AMdpbGLDAgMBAAECggEAUXVfT91z6IqghhKwO8QtC5T/+fN06B8rCYSKj/FFoZL0
        0oTiLFuYwImoCadoUDQUE/Efj0rKE2LSgFHg/44IItQXE01m+5WmHmL1ADxsyoLH
        z9yDosKj7jNM7RyV8F8Bg0pL1hU+rU4rhhL/MaS0mx4eFYjC4UmcWBmXTdelSVJa
        kvXvQLT5y86bqh7tqMjM/kALTWRz5CgNJFk/ONA1yo5RTX9S7SIXimBgAvuGqP8i
        MPEhJou7U3DfzXVfvP8byqNdsZs6ZNhG3wXspl61mRyrY+51SOaNLA7Bkji7x4bH
        Nw6mJI0IJTAP9oc1Z8fYeMuxT1bfuD7VOupSP0mAMQKBgQDk+KuyQkmPymeP/Wwu
        II4DUpleVzxTK9obMQQoCEEElbQ6+jTb+8ixP0bWLvBXg/rX734j7OWfn/bljWLH
        XLrSoqQZF1+XMVeY4g4wx9UuTK/D2n791zdOgQivxbIPdWL3a4ap86ar8uyMgJu8
        BLXfFBAOc+9myqUkbeO7wt0e6QKBgQDPV04jPtIJoMrggpQDNreGrANKOmsXWxj4
        OHW13QNdJ2KGQpoTdoqQ8ZmlxuA8Bf2RjHsnB2kgGVTVQR74zRib4MByhvsdhvVm
        F2LNsJoIDfqtv3c+oj13VonRUGuzUeJpwT/snyaL+jQ/ZZcYz0jDgDhIODTcFYj8
        DMSD5SHgywKBgHH6MwWuJ44TNBAiF2qyu959jGjAxf+k0ZI9iRMgYLUWjDvbdtqW
        cCWDGRDfFraJtSEuTz003GzkJPPJuIUC7OCTI1p2HxhU8ITi6itwHfdJJyk4J4TW
        T+qdIqTUpTk6tsPw23zYE3x+lS+viVZDhgEArKl1HpOthh0nMnixnH6ZAoGBAKGn
        V+xy1h9bldFk/TFkP8Jn6ki9MzGKfPVKT7vzDORcCJzU4Hu8OFy5gSmW3Mzvfrsz
        4/CR/oxgM5vwoc0pWr5thJ3GT5K93iYypX3o6q7M91zvonDa3UFl3x2qrc2pUfVS
        DhzWGJ+Z+5JSCnP1aK3EEh18dPoCcELTUYPj6X3xAoGBALAllTb3RCIaqIqk+s3Y
        6KDzikgwGM6j9lmOI2MH4XmCVym4Z40YGK5nxulDh2Ihn/n9zm13Z7ul2DJwgQSO
        0zBc7/CMOsMEBaNXuKL8Qj4enJXMtub4waQ/ywqHIdc50YaPI5Ax8dD/10h9M6Qc
        nUFLNE8pXSnsqb0eOL74f3uQ
        -----END PRIVATE KEY-----\"\"\",
            certificate_chain=(lambda path: open(path).read())("www.example.com/fullchain.pem"))
        ```

        ## Import

        This resource does not support importing.

        :param str resource_name: The name of the resource.
        :param DomainCertificateArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(DomainCertificateArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 certificate: Optional[pulumi.Input[str]] = None,
                 certificate_chain: Optional[pulumi.Input[str]] = None,
                 domain_id: Optional[pulumi.Input[str]] = None,
                 private_key: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = DomainCertificateArgs.__new__(DomainCertificateArgs)

            if certificate is None and not opts.urn:
                raise TypeError("Missing required property 'certificate'")
            __props__.__dict__["certificate"] = certificate
            if certificate_chain is None and not opts.urn:
                raise TypeError("Missing required property 'certificate_chain'")
            __props__.__dict__["certificate_chain"] = certificate_chain
            if domain_id is None and not opts.urn:
                raise TypeError("Missing required property 'domain_id'")
            __props__.__dict__["domain_id"] = domain_id
            if private_key is None and not opts.urn:
                raise TypeError("Missing required property 'private_key'")
            __props__.__dict__["private_key"] = private_key
            if type is None and not opts.urn:
                raise TypeError("Missing required property 'type'")
            __props__.__dict__["type"] = type
        super(DomainCertificate, __self__).__init__(
            'okta:index/domainCertificate:DomainCertificate',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            certificate: Optional[pulumi.Input[str]] = None,
            certificate_chain: Optional[pulumi.Input[str]] = None,
            domain_id: Optional[pulumi.Input[str]] = None,
            private_key: Optional[pulumi.Input[str]] = None,
            type: Optional[pulumi.Input[str]] = None) -> 'DomainCertificate':
        """
        Get an existing DomainCertificate resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] certificate: Certificate content.
        :param pulumi.Input[str] certificate_chain: Certificate certificate chain.
        :param pulumi.Input[str] domain_id: Domain ID.
        :param pulumi.Input[str] private_key: Certificate private key.
        :param pulumi.Input[str] type: Certificate type. Valid value is `"PEM"`.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _DomainCertificateState.__new__(_DomainCertificateState)

        __props__.__dict__["certificate"] = certificate
        __props__.__dict__["certificate_chain"] = certificate_chain
        __props__.__dict__["domain_id"] = domain_id
        __props__.__dict__["private_key"] = private_key
        __props__.__dict__["type"] = type
        return DomainCertificate(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def certificate(self) -> pulumi.Output[str]:
        """
        Certificate content.
        """
        return pulumi.get(self, "certificate")

    @property
    @pulumi.getter(name="certificateChain")
    def certificate_chain(self) -> pulumi.Output[str]:
        """
        Certificate certificate chain.
        """
        return pulumi.get(self, "certificate_chain")

    @property
    @pulumi.getter(name="domainId")
    def domain_id(self) -> pulumi.Output[str]:
        """
        Domain ID.
        """
        return pulumi.get(self, "domain_id")

    @property
    @pulumi.getter(name="privateKey")
    def private_key(self) -> pulumi.Output[str]:
        """
        Certificate private key.
        """
        return pulumi.get(self, "private_key")

    @property
    @pulumi.getter
    def type(self) -> pulumi.Output[str]:
        """
        Certificate type. Valid value is `"PEM"`.
        """
        return pulumi.get(self, "type")

