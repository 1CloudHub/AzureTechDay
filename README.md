## Deploy an application on AKS cluster using Azure DevOps

###  What's covered in this guide,

The following tasks will be performed:
- Creating a Resource group and configure Azure cloud shell
- Creating an Azure Container Registry (ACR), AKS cluster
- Setting up Azure DevOps account
- Creating Azure build and release pipelines for application automation

### Pre-requisites 
- Azure Subscription
- Azure DevOps account
- Bash Shell ( Azure Cloud Shell)
- Container registry
- Visual Studio Code

### Infrastructure Setup
#### Creating a Resource Group
A resource group is a logical way to organize instances you spin up on Azure. 

To create a resource group, click Resource groups on the left side bar and click + Add,

[![resource-group](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/resource-group.jpg "resource-group")]()

Enter a name for the resource group and change the resource group location to Southeast Asia. After that, click Review + Create. In the Summary page, click on Create.

![resource group](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/resource-group-1.png "resource group")

If you click Resource groups again from the left side bar, you should see that your resource group has been created. We will use this resource group to logically contain all our resources created during this lab session 

#### Configure Azure Cloud Shell

Once your Azure Subscription and Resource Group is configured, you can enable and use your associated Azure Cloud Shell session. In this article, we will use Bash.

Navigate to **Cloud Shell**

 ![cloudshell](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/cloudshell.png "cloudshell")

Click on **Advanced settings** option and update the Cloud Shell region as **Southeast Asia**

 ![cloud-shell](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/cloudshell-1.png "cloud-shell")
 
Click on **Create storage** to complete storage account setup
 
![cloudshell](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/cloudshell-2.png "cloudshell")
 
#### Setup Azure Container Registry
##### Parameters:
    $ location="SoutheastAsia" 
    $ rg="aksdevops" 
    $ acr="devpythonregistry" 

**If the DNS name is already in use. You can check if the name is already claimed using following API: https://docs.microsoft.com/en-us/rest/api/containerregistry/registries/checknameavailability

#### Create an ACR registry using below command

`$ az acr create -n $acr -g $rg -l $location --sku Basic`

##### Setup AKS Cluster
##### Parameters:

    $ name="hellopython"
    $ latestK8sVersion=$(az aks get-versions -l $location --query 'orchestrators[-1].orchestratorVersion' -o tsv)

**Create AKS cluster**

`$ az aks create -l $location -n $name -g $rg --generate-ssh-keys -k $latestK8sVersion --enable-addons http_application_routing --node-count 3 --zones 1 2 3`

** Here, we are deploying 3 node cluster. You can change the --node-count value based on the requirement. 

Use the below command to get the credentials to interact with your AKS cluster once it is created. Approx. it will take 10-15 mins to complete the cluster setup. 

`$ az aks get-credentials -n $name -g $rg`

Once Cluster is UP and running use the below command to setup tiller for Helm. We will use this later in this session

`$ kubectl create serviceaccount tiller --namespace kube-system `

`$ kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller `

Create namespace as helloworld, we will deploy apps with this namespace it later in this session. 

`$ kubectl create namespace helloworld `
`$ kubectl create clusterrolebinding default-view --clusterrole=view --serviceaccount=helloworld:default`

**Roles and Permissions for ACR**
We need to assign 2 specific service principals that need to interact with ACR. 
- Grant the AKS-generated service principal pull access to our ACR, the AKS cluster will be able to pull images of our ACR
	
```
 $ CLIENT_ID=$(az aks show -g $rg -n $name --query "servicePrincipalProfile.clientId" -o tsv)
 $ ACR_ID=$(az acr show -n $acr -g $rg --query "id" -o tsv)
```
	 
`$ az role assignment create --assignee $CLIENT_ID --role acrpull --scope $ACR_ID `

- Create a specific Service Principal for our Azure DevOps pipelines to be able to push and pull images and charts of our ACR

`$ registryPassword=$(az ad sp create-for-rbac -n $acr-push --scopes $ACR_ID --role acrpush --query password -o tsv)`

We will need this registry password later in this section to create Build pipeline and Release pipeline.

`$ echo $registryPassword`
7d21xxxx-xxxx-xxxx-xxxxx3216

Now, we have an ACR registry and AKS cluster ready to use throughout this session,

#### Azure DevOps account Setup
Navigate to **Azure DevOps** and Click on **My Azure DevOps Organizations**
 
 ![devops](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/devops-acc.png "devops")
 
Click on **Create** new organization

 ![org](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/organization.png "org")

Click on **Continue** to get started with Azure DevOps

 ![org](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/org-1.png "org")
 
Enter Name for Azure DevOps organization and Click on Continue to complete the setup

 ![org](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/org-2.png "org")

**Create New Project**
Click on **+ New project** to create new project in DevOps Organization. 

 ![project](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/project-1.png "project")
 
Enter Project Name and Description (optional) and Click on Create. 

 ![project](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/project-2.png "project")
 
**Source Control**
Import Git Repo into devops project

Click **Repos** on the left side bar and then click **Files** to import git repo.

 ![repo](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/repository-1.png "repo")
 
Click on **Import** to import a repository from Git

 ![repo](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/repository-2.png "repo")
 
We are using the existing Github repo https://github.com/1CloudHub/AzureTechDay  in this session. 
Copy and paste the git URL to import.
Enter Git URL and then click on Import

![repo](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/repository-3.png "repo")

Source code for application setup will be available once imported. 

 ![repo](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/repository-4.png "repo")

**Create a Build pipeline**
Now, we will create an Azure build pipeline for python (hello-world) app. 
Click **Pipeline** on the left side bar and then click **Builds** to create new build pipeline.
 
 ![pipeline](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/pipeline-1.png "pipeline")
 
Click on **+ New** and then select New build pipeline 
 
 ![pipeline](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/pipeline-2.png "pipeline")
 
Click on Use the **classic editor** to create a pipeline.

![pipeline](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/pipeline-3.png "pipeline")
 
Select **Azure Repos Git** as a Source and then click on **Continue**,

![pipeline](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/pipeline-4.png "pipeline")
 
Under Configuration as a code select **YAML** and click on **Apply**
 
 ![pipeline](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/pipeline-5.png "pipeline")
 
Now, configure build pipeline as follows
1.	Enter name for build pipeline
2.	Select Azure Pipelines as agent pool for YAML
3.	Browse YAML file path and select azure-build-pipeline.yml file under python folder
 
 ![pipeline](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/pipeline-6.png "pipeline") 
 
 ![pipeline](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/pipeline-7.png "pipeline") 
 
Navigate to **Variables** to set some variables for this build pipeline definition,
Select Pipeline variables and **click + Add**

 ![pipeline](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/pipeline-8.png "pipeline") 
 
**Variables and Values,**
Variable Name: ProjectName
This is for python project. Use python as projectName
Variable Name: registryLogin
Run the below command from Azure Cloud Shell to get registryLogin value

`$ az ad sp show --id http://$acr-push --query appId -o tsv`

Variable Name: registryName
Run the below command from Azure Cloud Shell to get registryName

`$ az acr show -n $acr --query name`

Variable Name: registryPassword
We got this value during service principal setup [echo $registryPassword].
 
 ![pipeline](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/pipeline-9.png "pipeline") 
 
Make sure you have enabled continuous integration
 
 ![pipeline](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/pipeline-10.png "pipeline") 
 
Now, **Save & Queue** a new build which will push both docker image and the Helm chart to ACR.
 
  ![pipeline](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/pipeline-11.png "pipeline") 
   
  ![pipeline](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/pipeline-12.png "pipeline") 
   
Now, run the below Azure CLI commands from Azure Cloud Shell to check on the images and helm charts pushed to ACR
**List Docker images from your ACR**

`$ az acr repository list -n $acr`

**List Helm charts from your ACR**

`$ az acr helm list -n $acr`

Now, both Docker image and Helm chart can be used for any Kubernetes cluster. 
Navigate to **Kubernetes Service** and Click on the cluster created above. 
 
 ![aks](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/aks-1.png "aks")
 
Copy **HTTP application routing domain** value and update **values.yaml** file.

Navigate to **AzureDevOps-->Projects-->Repos** and select **values.yaml** file to update the domain value,

![values](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/values.png "values")
 
Update the base domain value in values.yaml file

**Edit** and **commit** the changes

![edit](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/edit-and-commit-buils.png "edit")
 
**Create Release Pipeline**

Now, we will create an Azure release pipeline for python (hello-world) app to be able to via its associated Helm chart. 

Click Pipeline on the left side bar and then click Releases to create new release pipeline.

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-1.png "release")
 
Click on **+ New ** and then select **New release pipeline** 

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-2.png "release")
 
Start with an empty job, click on Empty job

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-3.png "release")
 
1.	Update release pipeline name
2.	Click on Add an artifact
3.	From the dropdown, Select the Source (build pipeline)
4.	Click on Add

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-4.png "release")
 
Make sure continuous deployment trigger enabled,
 
![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-5.png "release")

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-7.png "release")

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-8.png "release")
 
**Task Definition**

1.	Navigate to Tasks and select Stage 1
2.	Click on Agent job
3.	Select Agent pool as Azure Pipelines
4.	Select Agent Specification as ubuntu-16.04

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-9.png "release")

Add a task to Agent job

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-10.png "release")
 
Search for Helm and add below tasks, add Package and deploy Helm charts twice. 

- Helm tool installer
- Package and deploy Helm charts
 
 ![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-11.png "release")
 
Search for Bash and add below task,

- Bash
 
 ![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-12.png "release")
 
Reorder the Agent job task as below,

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-13.png "release")
 
**Helm tool installer – Install Helm**
1. Helm Version Spec – 2.14.1
2. Disable Check for latest version of Helm

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-14.png "release")
 
**Package and deploy Helm charts – helm init**

1. Select 1st helm ls task
2. Select Azure Resource Manager for Connection Type
3. Select available Azure Subscription and Click on Authorize to configure an Azure Service connection.
	*if prompted for sign-in, provide same username and password used for azure account setup.*

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-15.png "release")

4. Select available Azure service connection from the dropdown
5. Select the existing Resource group and Kubernetes cluster
6. In the command box, type init
7. Enable Upgrade Tiller and Wait
8. In Arguments box, type `--service-account tiller`

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-16.png "release")
 
**Bash – helm repo add**

1. Select Inline for Type
2. Enter the below script in Script box
` helm repo add $(registryName) https://$(registryName).azurecr.io/helm/v1/repo --username $(registryLogin) --password $(registryPassword) `

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-17.png "release")
 
**Package and deploy Helm charts – helm upgrade**

1.	Select last helm ls task
2.	Select Azure Resource Manager for Connection Type
3.	Select available Azure service connection for Azure Subscription
4.	Enter helloworld in Namespaces
5.	In the command box, type upgrade
6.	Select Name for Chart Type
7.	Enter $(registryName)/$(projectName) in Chart Name
8.	Enter $(projectName) in Release Name
9.	Enable Install if release not present and Wait
10.	In Arguments box, type below arguments
`--version $(build.buildId) --set image.repository=$(registryName).azurecr.io/$(projectName) --set image.tag=$(build.buildId) --set ingress.enabled=true --set ingress.hostname=python.<93xxxxxxxxxxxaa994.southeastasia.aksapp.io>`
*replace dns value with http application routing domain (from kubernetes service). *

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-18.png "release")
 
**Variables and Values,**

Add the below variables and Save

**Variable Name: ProjectName**

This is for python project. Use python as projectName

**Variable Name: registryLogin**

Run the below command from Azure Cloud Shell to get registryLogin value

`az ad sp show --id http://$acr-push --query appId -o tsv`

**Variable Name: registryName**

Run the below command from Azure Cloud Shell to get registryName

`az acr show -n $acr --query name`

**Variable Name: registryPassword**

We got this value during service principal setup [echo $registryPassword].
 
Now, click on **Save and Create release** to run this release pipeline, which will deploy the python's Helm chart.

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-19.png "release")

![release](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/release-pipeline-20.png "release")

**Validation**

Once deployed successfully, we can run the below commands from Azure Cloud Shell to check pod, service and hostname details.

`$ kubectl get all -n helloworld`
`$ kubectl get ing -n helloworld`

![validation](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/validation-1.png "validation")

Navigate to below URL in web browser
`http://<HOSTS>/ `
***replace the hosts value*
 
![validation](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/validation-2.png "validation")
 
We have successfully deployed the simple helloworld python app on Kubernetes cluster via a Helm Chart.

Now you can make the changes to your code and push it to Azure Repo and Azure pipelines will automatically build and release the new version. 

Updated the source code and pushed it to Azure repo using Git commands.
 
 ![validation](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/validation-3.png "validation")
 
Azure build pipeline is initiated once the code is pushed to Repo

![validation](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/validation-4.png "validation")
 
Azure release pipeline initiated once build is completed.

![validation](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/validation-5.png "validation")
 
Now, refresh the URL to view the changes,

![validation](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/validation-6.png "validation")
 
Update the replicaCount as 3 in values.yaml file and commit the changes either through VS code or Azure repo.

![validation](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/validation-7.png "validation")
 
Once Build and Release pipelines are successfully configured, you can see the increase in number pods using below command. Now application is running on 3 nodes. 

`$ kubectl get pods -o wide -n helloworld`

![validation](https://github.com/1CloudHub/Azure-AKS/blob/master/Images/validation-8.png "validation")
