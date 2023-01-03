
1- kubectl -f node-port-20036.yml apply
2- kubectl -f service-account.yml apply
3- get token by using: kubectl -n kubernetes-dashboard create token admin-user --duration=8760h
-----------------------------------------------------------------------------------
eyJhbGciOiJSUzI1NiIsImtpZCI6Il9JajBGdkd2ZXduNGUtZFRZRGd1Qmg0b3EyOGk4b3ZGNE55aWZzNzFGOHcifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiXSwiZXhwIjoxNzA0MjQ3NDk2LCJpYXQiOjE2NzI3MTE0OTYsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsInNlcnZpY2VhY2NvdW50Ijp7Im5hbWUiOiJhZG1pbi11c2VyIiwidWlkIjoiYzQwOGUyMzItYjU0Mi00ODMyLWE5Y2ItZDViYmVlNWRjZDRjIn19LCJuYmYiOjE2NzI3MTE0OTYsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlcm5ldGVzLWRhc2hib2FyZDphZG1pbi11c2VyIn0.zw0zjqIbdZg5d93fXW43wwTBVgcrZf8iy4Kpg7ocXNYtY_ozDKpIV45xyl-7zT7KMMqn19iqyvPC_j0Kbv25ROdLyG0xQxPj6HbacL-4sB7eHoJn0OD5B5-24SzvLEETA3ezyxPyislRV82tDVa03_6-4UgtmtOIk2DgpQoFmvhhg0tzg1_wUONCkrc7OBbu7VFIzRZkF5m27V9dNPY_pbhjzbVTT90Q7HhQKMXyhkcmVPURGnzKlFVWRcH9pHuuOeyqXCHbQPsJHIGafphKt-hO0Dfv9472v921WX8DKEu0RKzgPc4pWr__ttAwAEmyLHVxsYIaT0HlsH211dGC-g
docker run -d \
-m 4G \
-p 7070:7070 \
-p 8088:8088 \
-p 50070:50070 \
-p 8032:8032 \
-p 8042:8042 \
-p 2181:2181 \
apachekylin/apache-kylin-standalone:4.0.0
kubectl rollout restart -n xdoc-web deployment xdoc-web
------------------------------------------------------------------------