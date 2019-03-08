FROM kong:1.0

COPY start-up.sh /
RUN curl https://raw.githubusercontent.com/eficode/wait-for/master/wait-for -o /usr/bin/wait-for && chmod +x /usr/bin/wait-for /start-up.sh

CMD ["wait-for", "kongsql:5432", "--", "/start-up.sh"]