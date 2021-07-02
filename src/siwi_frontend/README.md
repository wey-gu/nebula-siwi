# Siwi Frontend

![demo](./images/demo.webp)

## Build Manually

Vue-cli service global was used for ease of debug(for a non-webpack engineer).

```bash
npm install -g @vue/cli-service-global

# serve for debugging
vue serve src/main.js

# build for production
vue build src/main.js
```

> Note: A reversed proxy is needed, i.e. with nginx, to mitigate the CORS that blocks siwi frontend to access backend in a different origin.

In below example, we make the following proxy rules:
- `localhost:8081/` to be proxied to vue debugging server(siwi frontend)
- `localhost:8081/query` to be proxied to siwi api server(siwi backend)

Ref: https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/

```nginx
server {
    listen       8081;
    server_name  localhost;

    location / {
        proxy_pass http://localhost:8080;
    }

    location /query {
        proxy_pass http://localhost:5000/query;
    }
}
```



## Thanks to my lovely Upstream Projects ❤️

- [VueJS](vuejs.org) for frontend framework
- [Vue Bot UI](https://github.com/juzser/vue-bot-ui ), as a lovely bot UI in vue
- [Vue Web Speech](https://github.com/Drackokacka/vue-web-speech ), for speech API vue wrapper
- [Axios](https://github.com/axios/axios ) for browser http client
- [Solarized](https://en.wikipedia.org/wiki/Solarized_(color_scheme)) for color scheme
- [Vitesome](https://github.com/alvarosaburido/vitesome) for landing page design

