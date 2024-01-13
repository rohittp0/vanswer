ARG PG_MAJOR=16
FROM postgres:$PG_MAJOR
ARG PG_MAJOR

RUN apt-get update && apt-get install -y wget unzip

RUN wget https://codeload.github.com/pgvector/pgvector/zip/refs/heads/master -O /tmp/pgvector.zip
RUN unzip /tmp/pgvector.zip -d /tmp
RUN mv /tmp/pgvector-master /tmp/pgvector && rm /tmp/pgvector.zip

RUN apt-get update && \
		apt-mark hold locales && \
		apt-get install -y --no-install-recommends build-essential postgresql-server-dev-$PG_MAJOR && \
		cd /tmp/pgvector && \
		make clean && \
		make OPTFLAGS="" && \
		make install && \
		mkdir /usr/share/doc/pgvector && \
		cp LICENSE README.md /usr/share/doc/pgvector && \
		rm -r /tmp/pgvector && \
		apt-get remove -y build-essential postgresql-server-dev-$PG_MAJOR && \
		apt-get autoremove -y && \
		apt-mark unhold locales && \
		rm -rf /var/lib/apt/lists/*
