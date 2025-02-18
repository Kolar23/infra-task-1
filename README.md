### How to run the python app in a k8s cluster:
1. Create a docker image of the app and push it to a container registry (e.g., ACR, Docker Hub).
2. Create k8s deployment and service manifest. In the deployment manifest, specify the image which you've just created. Remember the port you exposed the service on, as it will be used in the next steps.
3. Using `kubectl apply -f <manifest file name>`, to create the Kubernetes Deployment and Service.
4. To configure Prometheus to scrape logs from the Python app, add the following block to the Prometheus configuration:

```
 - job_name: infra_task
   static_configs:
    - targets:
       - infra-task-1:5000
```

In this case, the infra_task job_name will be the scrape_pool, and infra-task-1 is the service which was deployed in the cluster. 

In my current setup (Dockerized setup of Prometheus and Grafana, under the same network with the Python app), I'm able to access those logs using the container name and port.

If Prometheus is deployed in the same namespace as the python app, we can use the service name, similarly to what I've done. If it's in another namespace, we need to use the FQDN.

Example for FQDN:

```
scrape_configs:
  - job_name: "infra_task"
    static_configs:
      - targets: ["infra-task-1.<namespace>.svc.cluster.local:5000"]

```
### Helm Chart Creation
Using the command `helm create <name>` we create a chart directory along with the common files and directories used in a chart.

I have changed a few values in the values.yaml:
1. First repository - this should be changed depending where and under what name is the Python App Image pushed.
2. Pull Policy - changed it to Always, so that we can ensure the latest image is always pulled
3. Tag
4. Service Account Name
5. Service Port - changed to 5000, so that it can be picked up from Prometheus
6. Liveness and Readiness Probe Path and Port - I've added a simple return when trying to access the app on root ("/"). Decided to use this as a health and readiness probe, rather than the /metrics endpoint. Port is also changed.

After we are happy with the values in the values.yaml, we need to package the chart with `helm package <name>`
Then it can be deployed by using this command. Make sure you're using the correct k8s context first.

`helm install <package name> ./path-to-chart-dir`

or in my case 

`helm install infra-task-1` ./helm/infra-task-1