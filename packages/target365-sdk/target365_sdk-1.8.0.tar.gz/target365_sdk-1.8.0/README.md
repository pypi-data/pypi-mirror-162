## ![Strex](https://github.com/Target365/sdk-for-php/raw/master/strex.png "Strex")
Strex AS is a Norwegian payment and SMS gateway (Strex Connect) provider. Strex withholds an e-money license and processes more than 70 million transactions every year. Strex has more than 4.2 mill customers in Norway and are owned by the Norwegian mobile network operators (Telenor, Telia and Ice). Strex Connect is based on the Target365 marketing and communication platform.
## Target365 SDK for Python
[![License](https://img.shields.io/github/license/Target365/sdk-for-python.svg?style=flat)](https://opensource.org/licenses/MIT)

### Getting started
To get started, please click here: https://strex.no/strex-connect#Prispakker and register your organisation. 
For the SDK please send us an email at <sdk@strex.no> containing your EC public key in PEM-format.
You can generate your EC public/private key-pair using openssl like this:
```
openssl ecparam -name prime256v1 -genkey -noout -out mykey.pem
```
Use this openssl command to extract the public key in PEM-format:
```
openssl ec -in mykey.pem -pubout -out pubkey.pem
```
You can then send us the pubkey.pem file. The file should look something like this:
```
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEuVHnFqJxiBC9I5+8a8Sx66brBCz3
Flt70WN9l7WZ8VQVN9DZt0kW5xpiO5aG7qd5K8OcHZeoJRprFJOkBwW4Fg==
-----END PUBLIC KEY-----
```
Our Python SDK takes the raw private key as a HEX string. To get the HEX private bytes you can use this command:
```
openssl pkey -in mykey.pem -text
```
This will generate an output like this:
```
-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgKdQ8xhRtsMpX3JXV
Oot+HqcVcfCNx+ZEX2WZWw+auGahRANCAAR1LUpsVHVxSMr7cTg/Efc+Ytof8wBO
yqwJlQWnC2sbwxdiUzBqba0WikHwSDcC6jqo8i5ANdEpRE5u090gKg0B
-----END PRIVATE KEY-----
Private-Key: (256 bit)
priv:
    29:d4:3c:c6:14:6d:b0:ca:57:dc:95:d5:3a:8b:7e:
    1e:a7:15:71:f0:8d:c7:e6:44:5f:65:99:5b:0f:9a:
    b8:66
pub:
    04:75:2d:4a:6c:54:75:71:48:ca:fb:71:38:3f:11:
    f7:3e:62:da:1f:f3:00:4e:ca:ac:09:95:05:a7:0b:
    6b:1b:c3:17:62:53:30:6a:6d:ad:16:8a:41:f0:48:
    37:02:ea:3a:a8:f2:2e:40:35:d1:29:44:4e:6e:d3:
    dd:20:2a:0d:01
ASN1 OID: prime256v1
NIST CURVE: P-256
```
Use the HEX string here displayed and just remove the colon characters in between. In this example the correct private key in HEX will be:
```
29d43cc6146db0ca57dc95d53a8b7e1ea71571f08dc7e6445f65995b0f9ab866
```

For more details on using the SDK we strongly suggest you check out our [Python User Guide](USERGUIDE.md).

#### Key Name

The key name needed to initialize an ApiClient is the one associated with your key, upon registration, e.g. "AcmeInc".

### PIP
```
pip install target365-sdk
```
[![pypi version](https://img.shields.io/pypi/v/target365_sdk.svg)](https://pypi.org/project/target365-sdk/)
[![python_platform](https://img.shields.io/pypi/pyversions/target365_sdk.svg)](https://pypi.org/project/target365-sdk/)

### Test Environment
Our test-environment acts as a sandbox that simulates the real API as closely as possible. This can be used to get familiar with the service before going to production. Please be ware that the simulation isn't perfect and must not be taken to have 100% fidelity.

#### Url: https://test.target365.io/

### Production Environment
Our production environment is a mix of per-tenant isolated environments and a shared common environment. Contact <sdk@strex.no> if you're interested in an isolated per-tenant environment.

#### Url: https://shared.target365.io/

### Authors and maintainers
Target365 (<sdk@strex.no>)

### Issues / Bugs / Questions
Please feel free to raise an issue against this repository if you have any questions or problems.

### Contributing
New contributors to this project are welcome. If you are interested in contributing please
send an email to sdk@strex.no.

### License
This library is released under the MIT license.
