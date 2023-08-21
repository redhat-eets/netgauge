# Sample Manifests for Single Node OpenShift

This directory includes a collection of manifest files designed to facilitate the deployment of the "testpmd" container within a single-node OpenShift cluster. These manifests have been thoroughly tested and optimized for compatibility with OpenShift version 4.13.6. It's important to note that some of the configuration elements utilized in these manifest files might not be applicable to earlier OpenShift versions. This distinction arises due to the progressive evolution of cri-o features and related provisioning processes in preceding versions.

To ensure a successful deployment, it's recommended to adhere to a specific sequence when applying the YAML files. Following a fresh installation, the order of application is as follows:

1. Apply performance-profile.yaml
2. Apply sub-sriov.yaml
3. Apply sriov-nic-policy.yaml
4. Apply sriov-network.yaml
5. Apply namespace.yaml
6. Apply pod-testpmd.yaml

This sequential application of the manifest files is crucial for the proper configuration and functioning of the "testpmd" container within the OpenShift environment.

Once all the provided YAML files have been successfully applied in the specified order, the "testpmd" container should be optimized and prepared to efficiently forward network traffic. This sequence of manifest application ensures that the necessary configurations, profiles, policies, and network settings are in place for the "testpmd" container to function optimally within the single-node OpenShift cluster.

