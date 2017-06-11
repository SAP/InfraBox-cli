FROM alpine

ADD result.json /result.json
ADD entrypoint.sh /entrypoint.sh

RUN adduser -S tester
USER tester

CMD /entrypoint.sh
