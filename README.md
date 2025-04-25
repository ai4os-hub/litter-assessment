# Litter Assessment: Identify Floating Plastic

[![Build Status](https://jenkins.services.ai4os.eu/buildStatus/icon?job=AI4OS-hub/litter-assessment/main)](https://jenkins.services.ai4os.eu/job/AI4OS-hub/job/litter-assessment/job/main/)

**Project**: This work is part of the iMagine project that receives funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No. 101058625.

This is a software package that provides two trained convolutional neural networks for the detection and classification of plastic waste in drone data. The AI models, as well as the processing steps, can be deployed locally or used as cloud-based tools. In addition to running the pre-trained model, two jupyter notebooks are provided which allow the finetuning of both models to custom data.

## 1. Deployment
First, the module needs to be deployed. This can be done by installing the package directly in your environment (make sure to use a virtual environment!) or by using the provided docker image.

### Local deployment
To launch it, first install the package then run [deepaas](https://github.com/ai4os/DEEPaaS):
```bash
git clone https://github.com/ai4os-hub/litter-assessment
cd litter-assessment
pip install -e .
deepaas-run --listen-ip 0.0.0.0
```
### Local deployment using docker
- download docker image from [docker hub](https://hub.docker.com/r/ai4oshub/litter-assessment): ```docker pull ai4oshub/litter-assessment```

- run docker container: ```docker run -ti -p 5000:5000 -p 6006:6006 -p 8888:8888 ai4oshub/litter-assessment```

Both methods for local deployment launch an API on your local machine under: [http://0.0.0.0:5000/api](http://0.0.0.0:5000/api).

## 2. Inference
Executing the AI models can be done either via the API, launched in step 1., or cloud-based using OSCAR.

### Local deployment

- after the API is launched according to one of the methods described in 1. Deployment, go to [http://0.0.0.1:5000/api](http://0.0.0.1:5000/api) and choose PREDICT endpoint 

- upload your image under **files** and set the following parameters:
```
PLD_plot: {true, false} choose if the plot for Plastic Litter Detection should be generated.

PLQ_plot: {true, false} choose if the plot for Plastic Litter Quantification should be generated.

Face_Detection: {true, false} choose if an additional face detection model should analyse the image before running the litter models. The tiles for which the model detects a face are blacked out.
```

- click **Execute**. After the models are done, you can download the results under **Download file**

### Cloud inference with OSCAR

- users must register [here](https://aai.egi.eu/auth/realms/id/account/#/enroll?groupPath=/vo.imagine-ai.eu) to access OSCAR cluster

- link to OSCAR cluster: [https://inference-walton.cloud.imagine-ai.eu](https://inference-walton.cloud.imagine-ai.eu)

- login via EGI Check-in with any account 

- go to Buckets -> uc-litter-assessment -> input and upload your images there 

- once the prediction is completed, you can find the .zip file with the results under Buckets -> uc-litter-assessment -> output 

**NOTE**: when using the uc-litter-assessment bucket, the uploaded images are visible to everyone who has access to OSCAR. If you need a private bucket, please contact litter_assessment_support@dfki.de 

## Training
The two folders [training_litter_detection](https://github.com/ai4os-hub/litter-assessment/tree/main/training_litter_detection) and [training_litter_quantification](https://github.com/ai4os-hub/litter-assessment/tree/main/training_litter_quantification) contain jupyter notebooks to finetune the pretrained DenseNet121 models on custom data.
The following parameters can be adapted in the main script to modify the training process:
- num_epochs
- learning_rate
- batch_size
- optimizer
- loss_fn

### Data
Ensure your data directories are organized so that each class has its own folder containing the images. The directory structure should look like this:

data/  
│  
├── class0/  
│ &emsp;├── 0.jpg  
│ &emsp;├── 1.jpg  
│ &emsp;└── ...  
│  
├── class1/  
│ &emsp;├── 0.jpg  
│ &emsp;├── 1.jpg  
│ &emsp;└── ...  
│  
├── class2/  
│ &emsp;├── 0.jpg  
│ &emsp;├── 1.jpg  
│ &emsp;└── ...  
│  
└── ... 

Ensure that the names of the folders correspond to the class labels used in your YAML file.

### Label YAML file
The **configs/labels.yaml** file contains the old labels, that the models were trained with. The new, custom labels should have the following structure:  
``` 
label:
    label old: label old: ['Litter-high', 'Litter-low', 'Organic debris', 'Other','Sand-Soil', 'Stones', 'Vegetation', 'Water'] DO NOT CHANGE  
    label new: ['class0', 'class1', ... ]  
```

### Notes
The models were originally trained in a patchwise classification approach. Accordingly, the training input data consisted of image patches of size 128x128 (Plastic Litter Detection) and size 64x64 (Plastic Litter Quantification).

## Project structure
```
├── LICENSE                <- License file
│
├── README.md              <- The top-level README for developers using this project.
│
├── requirements.txt       <- The requirements file for reproducing the analysis environment, e.g.
│                             generated with `pip freeze > requirements.txt`
│
├── pyproject.toml         <- makes project pip installable (pip install -e .) so
│                             litter_assessment_service can be imported
│
├── litter_assessment_service    <- Source code for use in this project.
│   │
│   ├── __init__.py        <- Makes litter_assessment_service a Python module
│   │
│   └── api.py             <- Main script for the integration with DEEP API
│
├── training_litter_detection    <- folder for training the litter detection model
│   │
│   ├── training_detection.ipynb    <- jupyter notebook for running the training
│   │
│   ├── data/              <- store your labelled data here
│
├── training_litter_quantification    <- folder for training the litter quantification model
│   │
│   ├── training_quantification.ipynb    <- jupyter notebook for running the training
│   │
│   ├── data/              <- store your labelled data here
│
└── Jenkinsfile            <- Describes basic Jenkins CI/CD pipeline
```
