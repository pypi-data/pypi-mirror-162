# CW CLI

Es una herramienta que permite a los colaboradores de celuweb implementar sus repositorios con la arquitectura correspondiente.
----
## 1. Instalaciones

### Linux
```
sudo apt install python3-pip
```

----

## 2. Entornos Virtuales
Los entornos virtuales nos ayudan a tener librerias dependientes solo a los proyectos

### Linux
```
sudo apt install python3-venv
```

### Crear entorno
```
python3 -m venv cwcli_env
```

### Entrar al entorno virtual
```
source cwcli_env/bin/activate
```

### Salir del entorno virtual
```
deactivate
```

----

## 3. Intalación

```
pip3 install -r requirements.txt
```

----

## 4. Run
```
python3 -m build
```

### development Mode
```
pip install --editable .
```

## 5. PyPI
```
usuario: celuweb
clave: C3luw3b2021*

twine upload --repository-url https://test.pypi.org/legacy/ dist/*


```

