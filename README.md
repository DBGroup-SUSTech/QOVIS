# QOVIS

Understanding and diagnosing query optimizers is crucial to guarantee the correctness and efficiency of query processing among big data and database systems. In this work, we propose QOVIS to identify the query optimization bugs/issues and investigate the root causes for them via a visualization-assisted approach.

## 1 Deployment

QOVIS is a full-stack web application. The frontend is built with `Vue.js` and the backend is built with `Python3.9`.

Here is a step-by-step guide to deploying QOVIS on your local machine.

### 1.1 Prerequisites
You can check your environment by running the following commands:

```bash
cd <proj_root>/scripts
./check_env.sh
```

This will make sure the following scripts can be executed successfully.

### 1.2 Install the dependencies

Execute the following commands to install the dependencies:

```bash
cd <proj_root>/scripts
./install_dependencies.sh
```

### 1.3 Prepare the data
We have collected the log files of several queries from `Spark 3.3.0`. They are zipped and located in `<proj_root>/qovis_backend/data/data_preset`.

Execute the following commands to prepare the data:

```bash
cd <proj_root>/scripts
./decompress_data.sh data_preset          # decompress the data in dataset "data_preset"
./preprocess_data.sh data_preset          # preprocessing the data in dataset "data_preset"
```

The dataset folders are placed at `<proj_root>/qovis_backend/data`.
Then the optimization traces will be extracted from the log files, and next be analyzed.

### 1.4 Start QOVIS

Execute the following commands to start QOVIS:

```bash
cd <proj_root>/scripts
./start_all.sh data_preset          # start the backend and frontend servers with dataset "data_preset"
```

This will start the backend server and the frontend server as background processes.

Then after a few minutes, you can visit `http://localhost:14000` to access QOVIS. `Edge` and `Chrome` are recommended.

### 1.5 Stop QOVIS

Execute the following commands to stop QOVIS:

```bash
cd <proj_root>/scripts
./stop_all.sh
```


## 2 Evaluation

The materials and results of the evaluation (i.e., case study, user study and performance study) are located in the `eval` folder.
You can visit `http://localhost:14000/question?pid=0&order=0` to access the user study page.
