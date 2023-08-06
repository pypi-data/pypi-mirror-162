- Summary：
    - This package includes codes and data for "Efficient Bayesian Inference on Quantile Spectral Analysis of Multivariate Stationary Time Series" by Zhixiong Hu and Raquel Prado.
    - The codes are written in Python 3.7.0 (suggested version >= 3.7).
    - Author: Zhixiong Hu

- Set Up
    - Install Anaconda Python from: https://www.anaconda.com/products/individual
    
    **Note:** If conda command is still unavailable in the terminal, please open Anaconda Navigator app (installed in the previous step) and open the terminal as following: 

    ![image info](anaconda_navigator.png)

    - Open the terminal as in the previous step. To install the package, type 'pip install -i https://pypi.org/simple/ example-qspec==0.1.0' (or type 'pip install --upgrade example_qspec')
    - 'cd' to where the [packaging_tutorial/test] folder is located (set [test] as work directory)

- Run Test Code:
    - In the [test] folder, [runbook_1.py] and [runbook_2.py] are runbooks to show how to use our approach to reproduce part of the results in the paper.   
    - Use Anacoda Prompt command line, type 'python runbook_1.py' or 'python runbook_2.py' to run the test code.
    - The results will be stored (as .png files) in [test] folder.
    - The [test/utils] folder includes sample data used in the runbooks.
- Use .npy data in R
    - All the data is stored as .npy files. To load .npy in R, use the following command:
    
```
# R code, please download reticulate R package first

library(reticulate)
np <- import("numpy")
array = np$load('test/utils/qvar1.npy') # specify where .npy is
```


- Useful linkes:
    - Anaconda: https://www.anaconda.com/products/individual   
    - tensorflow: https://www.tensorflow.org/api_docs (Tensorflow GPU setup: https://www.tensorflow.org/install/gpu)
    - tensorflow-probability: https://www.tensorflow.org/probability

**Note**
    We are actively updating the code. For example, currently the naming convention is messy. In the next step, we want to follow PeP-8 style to improve the readability and consistency of our Python code.