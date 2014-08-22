swift3-gatekeeper
-------

swift3-gatekeeper 는 openstack swift의 middleware이다.

s3 관련 작업을 처리하기 위해 사용되는 내부 User Metadata가 외부에 공개되지 않도록 걸러주는 
필터 역할을 한다.

Metadata Prefix가 '**X-Object-Meta-S3-**' 인 것들만 필터링한다.

Install
-------

0)  선행작업으로 [swift3](https://github.com/stackforge/swift3)이 설치되어 있어야한다.

1)  lifecycle을 설치하기 위해서는 ``sudo python setup.py install`` 또는
    ``sudo python setup.py develop``를 이용하여 설치할 수 있다.

2)  proxy-server.conf의 pipeline에 lifecycle을 추가한다.

    Was::

        [pipeline:main]
        pipeline = catch_errors cache swift3 tempauth proxy-server

    Change To::

        [pipeline:main]
        pipeline = catch_errors cache swift3_gatekeeper swift3 tempauth
        proxy-server


3)  proxy-server.conf 의 section에 swift3_gatekeeper WSGI filter 를 추가한다.

    [filter:swift3_gatekeeper]
    use = egg:swift3_gatekeeper#swift3_gatekeeper

