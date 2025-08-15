# Kubernetes

[Kubernetes the hard way](https://github.com/kelseyhightower/kubernetes-the-hard-way).

Kubernetes, también conocido como K8s, es un sistema de código abierto para automatizar la implementación, el escalado y la gestión de aplicaciones en contenedores.

Agrupa los contenedores que componen una aplicación en unidades lógicas para facilitar la gestión y el descubrimiento. Kubernetes se basa en 15 años de experiencia en la ejecución de cargas de trabajo de producción en Google, combinado con las mejores ideas y prácticas de la comunidad.

---

## Instalación

### Minikube

Es una distribución de Kubernetes orientada a nuevos usuarios y trabajo de desarrollo. Sin embargo, no está diseñado para implementaciones de producción, ya que solo puede ejecutar un clúster de un solo nodo en su máquina. [Instrucciones de instalación](https://minikube.sigs.k8s.io/docs/start/).

```bash
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

Inicia el Cluster

```bash
minikube start -p valenta
```

Interactuar con su clúster
Si ya tiene instalado kubectl, ahora puede usarlo para acceder a su nuevo y brillante clúster:

```bash
    kubectl get po -A
```

### micrk8s

[Instrucciones de instalación](https://microk8s.io/#install-microk8s).

Instalar Microk8s on Linux

```bash
    sudo snap install microk8s --classic
```

Validar el estado, revisar cuando kubernetes inicie y este listo

```bash
    microk8s status --wait-ready
```

Empezar a usar kubernetes

```bash
microk8s kubectl get all --all-namespaces
```

Acceder al dashboard de Kubernetes

```bash
microk8s dashboard-proxy
```

## Pasar de docker compose a kubernetes

### Linux

Descargar, dar permisos y mover kompose

```bash
    curl -L https://github.com/kubernetes/kompose/releases/download/v1.26.0/kompose-linux-amd64 -o kompose
    chmod +x kompose
    sudo mv ./kompose /usr/local/bin/kompose
```

### Windows

Kompose can be installed via [Chocolatey](https://chocolatey.org/packages/kubernetes-kompose)

```console
choco install kubernetes-kompose
```

or using winget

```console
winget install Kubernetes.kompose
```

### Docker

You can build an image from the official repo for [Docker](https://docs.docker.com/engine/reference/commandline/build/) or [Podman](https://docs.podman.io/en/latest/markdown/podman-build.1.html):

```bash
docker build -t kompose https://github.com/kubernetes/kompose.git\#main
```

To run the built image against the current directory, run the following command:

```bash
docker run --rm -it -v $PWD:/opt -w /opt kompose kompose convert
```

## macOS

On macOS, you can install the latest release via [Homebrew](https://brew.sh) or [MacPorts](https://www.macports.org/).

```bash
brew install kompose
```

### Este ejemplo esta pensado a partir de un proceso de inferencia simple

Convertir docker compose a archivos de configuración yaml

```bash
    kompose convert
    # Usando una carpeta en especifico, especificando como tratar los volumenes
    kompose convert -f docker-compose.yml -o komposefiles/ --volumes hostPath
```

Nota: Si desea agregar balanceador de carga para poder exponer servicios, agregue lo siguiente en cada servicio.

labels:
      kompose.service.type: LoadBalancer

```bash
INFO Kubernetes file "komposefiles/adminer-service.yaml" created 
INFO Kubernetes file "komposefiles/inference-service.yaml" created 
INFO Kubernetes file "komposefiles/train-service.yaml" created 
INFO Kubernetes file "komposefiles/adminer-deployment.yaml" created 
INFO Kubernetes file "komposefiles/inference-deployment.yaml" created 
INFO Kubernetes file "komposefiles/train-deployment.yaml" created 
```

se debe aplicar estas configuraciones  agregando cada uno de los archivos de configuración creados, separados por coma

```bash
    microk8s kubectl apply -f inference-tcp-service.yaml,train-tcp-service.yaml,inference-deployment.yaml,netinference-networkpolicy.yaml,train-deployment.yaml,taller1-net-db-networkpolicy.yaml
    # Usando una carpeta en especifico
    microk8s kubectl apply -f komposefiles/
```

```bash
deployment.apps/adminer created
service/adminer created
deployment.apps/inference created
service/inference created
deployment.apps/train created
service/train created
```

Validar el estado de todo:

```bash
    microk8s kubectl get all --all-namespaces
```

Para ver especificamente los servicios:

```bash
    microk8s kubectl get service
```

Para exponer de manera temporal un servicio en especifico:

```bash
    microk8s kubectl port-forward --address 0.0.0.0 service/adminer 8080:8080
```

Si se desea borrar todos los componentes de un namespace especifico (default):

```bash
    microk8s kubectl delete --all daemonsets,replicasets,services,deployments,pods,rc,ingress --namespace=default
```

Mas informacion sobre [kompose](https://kubernetes.io/docs/tasks/configure-pod-container/translate-compose-kubernetes/)