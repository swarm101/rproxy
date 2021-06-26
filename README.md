# rproxy

Proxy reverso http e https com auto configuração através de labels!

Para utilizar fazer o seguinte processo:
- implantar rproxy
- utilizar rproxy

### Implantar rproxy

Esse é o compose para implantar o rproxy, mais a frente vou detalhar:

```yml
version: "3.6"

services:
    rproxy:
        image: rproxy
        deploy:
            placement:
                constraints: 
                - node.role == manager
        ports:
        - 80:80
        - 443:443
        volumes:
        - /var/run/docker.sock:/var/run/docker.sock
        - rproxy_data:/data
        networks:
        - rproxy

volumes:
    rproxy_data:

networks:
    rproxy:
        name: "rproxy"
        attachable: true
```

Executar o comando para implantar o rproxy

```sh
docker stack up -c docker-compose.yml rproxy
```

Esse compose da acesso ao socket do docker para o rproxy, isso é necessário pois ele escuta por eventos para configurar o proxy automáticamente. Também é criado um volume para o /data para persistir dados importantes do rproxy. Uma limitação é adicionada para que o serviço rode no manager (já que precisa se comunicar com o docker). Como o rproxy é um proxy http e https utiliza as portas 80 e 443. Uma rede para o rproxy é adicionada, os container que vão utilizar o proxy precisam estar nessa rede.

### Utilizar rproxy

Utilizando o rproxy para seus serviços

```yml
version: "3.6"

services:
    teste1:
        image: nginx
        deploy:
            labels:
                io.github.swarm101.rproxy.domains: "https://site1.duckdns.org http://site2.duckdns.org."
                io.github.swarm101.rproxy.upstream: "http://{name}:80"
        networks:
        - rproxy

networks:
    rproxy:
        external: true
```

Executar o seguinte comando para implantar seu serviço

```sh
docker stack up -c docker-compose.yml teste
```

Esse compose tem uma rede externa chamada rproxy (que criamos no serviço do rproxy), dessa forma o rproxy pode falar com esse serviço, repare que não é necessário exportar a porta pois ambos serviços estão nas mesma rede. Depois disso apenas adicionar os labels:

**io.github.swarm101.rproxy.domains**

Informar um ou mais domínio com o protocol. Se o protocolo for https será gerado o certificado para o domínio, automaticamente o http direciona para o https. Caso seja informado para o mesmo domínio o http e https ambos serão criados porem o http não redireciona para o https. Se informar apenas o http o certificado não será gerado.

**io.github.swarm101.rproxy.upstream**

Informar a URL com protocol para onde o rproxy deve encaminhar as requisições para utilizar o nome do serviço passar {name}.

