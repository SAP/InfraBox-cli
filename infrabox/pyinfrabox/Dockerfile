FROM stege/baseimage:1

RUN apk add --no-cache py-pip py-yaml git
RUN pip install coverage future xmlrunner pyyaml

ENV PYTHONPATH=/

RUN adduser -S tester

COPY pyinfrabox /pyinfrabox
COPY infrabox/pyinfrabox/entrypoint.sh /pyinfrabox/entrypoint.sh

RUN chown -R tester /pyinfrabox

USER tester

WORKDIR /pyinfrabox

RUN dos2unix /pyinfrabox/entrypoint.sh

CMD /pyinfrabox/entrypoint.sh
