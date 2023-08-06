# Description
Memory Wrap is an extension to image classification models that improves both data-efficiency and model interpretability, adopting a sparse content-attention mechanism between the input and some memories of past training samples.

# Installation
This is a PyTorch implementation of Memory Wrap. To install Memory Wrap run the following command:
```
pip install memorywrap
```

The library contains two main classes:
- *MemoryWrapLayer*: it is the Memory Wrap variant described in the paper that uses both the input encoding and the memory encoding to compute the output;
- *BaselineMemory*: it is the baseline that uses only the memory encoding to compute the output.

# Usage
## Instantiate the layer
```python
memorywrap = MemoryWrapLayer(encoder_output_dim, output_dim, head=None, classifier=None, distance='cosine')
```
or, for the baseline that uses only the memory to output the prediction:
```python
memorywrap = BaselineMemory(encoder_output_dim, output_dim, head=None, classifier=None, distance='cosine')
```
where
- *encoder_output_dim* (int) is the output dimension of the last layer of the encoder 
- *output_dim* (int) is the desired output dimensione. In the case of the paper *output_dim* is equal to the **number of classes**;
- *head* (torch.nn.Module): Read head used to project the key and query. It can be a linear or non-linear layer. Input dimensions must be equal to encoder_output_dim (in this case 1280). If None, it is fixed as a linear layer with input and output dimension equal to the input dimension of MemoryWrap(encoder_output_dim). (See https://www.nature.com/articles/nature20101 for further information)
- classifier (torch.nn.Module): Classifier on top of MemoryWrap. Inputs dimensions must be equal at encoder_output_dim\*2 for MemoryWrapLayer and encoder_output_dim for BaselineMemory. By default is an MLP as described in the paper. An alternative is to use a linear layer. (e.g. torch.nn.Linear(encoder_output_dim\*2, output_dim). Default: torch.nn.Sequential( torch.nn.Linear(encoder_output_dim*2, encoder_output_dim\*4), torch.nn.ReLU(),            torch.nn.Linear(encoder_output_dim\*4, output_dim)

- distance (str): Distance to use to compute the similarity between input and memory set. Allowed values are: cosine, l2 and dot for respectively cosine similarity, l2 distance and dot product distance. Default=cosine
## Forward call
Add the forward call to your forward function.
```python
output_memorywrap = memorywrap(input_encoding, memory_encoding, return_weights=False)
```
where *input_encoding* and *memory_encoding* are the outputs of the the encoder of rispectively the current input and the memory set. <br>
The last argument of the Memory Wrap's call function is a boolean flag controlling the number of outputs returned. If the flag is True, then the layer returns both the output and the sparse attention weight associated to each memory sample; if the flag is False, then the layer return only the output.

# Additional information
Here you can find link to additional source of information about Memory Wrap:
- <a href="https://trebuchet.public.springernature.app/get_content/809bb246-b0f1-4f37-b640-270d7413ebdc">Paper</a>
- <a href="https://github.com/KRLGroup/memory-wrap">GitHub repo</a>
- <a href="https://colab.research.google.com/drive/1OPjcpTH7X8EV1ev361iuhVzd2Jfp9kFA">Jupyter notebook</a>
