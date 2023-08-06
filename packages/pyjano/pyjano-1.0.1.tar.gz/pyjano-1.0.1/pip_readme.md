# pyjano


![Pyjano](logo.png) 

Pyjano stands for **Py**thon **Jan**a **O**rchestrator. Python wrapper over 
[jana2](https://github.com/JeffersonLab/JANA2) framework to make configuration
 and running convenient. 


```bash
pip install pyjano
```

Usage:

```python
from pyjano.jana import Jana
jana = Jana()

# Plugins configuration 
jana.plugin('beagle_reader')\
    .plugin('vmeson')\
    .plugin('event_writer')\
    .plugin('jana', nevents=10000, output='beagle.root')\
    .source('../data/beagle_eD.txt')

# Run
jana.run()
```


